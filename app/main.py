import logging
import os
import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated, List

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status, Form, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from openai import OpenAI
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlmodel import Session, select

from app.database import create_db_and_tables, get_session
from app.models.auth import Token, TokenData
from app.models.consultation import ResponseTone, PatientReport, Prompt, DoctorsResponse
from app.models.search import Search, SearchDiagnose, SearchImage
from app.models.user import User, UserCreate

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPLOADS_DIRECTORY = os.getenv("UPLOADS_DIRECTORY")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# create uploads dir if it does not exist
os.makedirs(UPLOADS_DIRECTORY, exist_ok=True)

# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# define startup behavior (initialize db if does not exists)
@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

SessionDep = Annotated[Session, Depends(get_session)]


def hash_password(password: str) -> str:
    """
    Hash a plain password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str, session: Session) -> User:
    user = session.exec(
        select(User).where(User.username == username)
    ).first()

    return user


def authenticate_user(username: str, password: str, session: Session) -> bool | User:
    """
    Authenticate user by verifying password.
    """
    user = get_user(username, session)
    if not user:
        return False

    if not verify_password(password, user.password_hash):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token with expiration.
    """
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, session: SessionDep):
    # Check for duplicate email (username)
    username_check = session.exec(
        select(User).where(User.username == user_create.username)
    ).first()
    if username_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user = User(
        username=user_create.username,
        password_hash=hash_password(user_create.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {"message": f"User: {user.username} created successfully"}


@app.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: SessionDep
) -> Token:
    """
       Login endpoint that returns a JWT access token.
    """
    user = authenticate_user(
        username=form_data.username,
        password=form_data.password,
        session=session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = session.exec(select(User).where(User.username == token_data.username)).first()
    if user is None:
        raise credentials_exception
    return user


def save_search(report: PatientReport, current_user: User, images: list[SearchImage], diagnoses: list[SearchDiagnose],
                session: Session):
    search = Search(
        symptoms=report.symptoms,
        diagnoses=diagnoses,
        patient_age_years=report.age_years,
        response_tone=report.response_tone,
        language_style=report.language_style,
        user_id=current_user.id,
        user=current_user,
        images=images
    )

    session.add(search)
    session.commit()
    session.refresh(search)


def get_configured_temperature(tone: ResponseTone) -> float:
    if tone == ResponseTone.FUNNY or tone == ResponseTone.FRIENDLY:
        return 0.3

    return 0.1


def build_diagnose_prompt(patient_report: PatientReport) -> Prompt:
    """
    May raise validation error.
    :param patient_report:
    :return:
    """
    system_instruction = f"You are a {patient_report.tone} doctor."
    prompt = f"""
    The patient describes following symptoms: '{patient_report.symptoms}'
    The patient says about the duration of the symptoms: '{patient_report.duration if patient_report.duration else "N/A"}'
    If patient provided images, please take them in the account when finding appropriate diagnoses.
    Briefly describe what you see on the images and how it supports/disapproves the diagnoses of your choice.
    If patient provided images that do not display symptoms of a medical condition or unrelated images, e.g. images
    of objects instead of body parts, do NOT take them into account and inform the patient about it.
    Answer shortly, and use {patient_report.tone} tone.
    Address the person directly using 'you' in the answer.
    Use {patient_report.style} language in the answer, as if you were speaking to an average person aged: 
    {patient_report.age_years if patient_report.age_years else "N/A"}.
    What would be the possible diagnosis and what are the recommended steps for the patient to do?
    """

    prompt = Prompt(
        system_instruction=system_instruction,
        query=prompt,
        temperature=get_configured_temperature(patient_report.tone)
    )

    return prompt


def error_response(message: str = "Internal server error", status_code: int = 500):
    """Factory method for error responses."""
    return JSONResponse(status_code=status_code, content={"detail": message})


async def upload_images(current_user: User, symptom_images: list[UploadFile]):
    if symptom_images is not None and not current_user.has_premium_tier:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="For uploading images you need to have a paid premium tier."
        )

    if symptom_images is not None and len(symptom_images) > 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="It is only possible to upload a maximum of 3 images.")

    saved_images = []
    allowed_mime_types = {"image/jpeg", "image/png", "image/webp"}
    for image in symptom_images:
        if image.content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported media type: only image files in jpeg, png or webp format are allowed."
            )

        # image_data = await image.read()
        # image = Image.open(io.BytesIO(image_data))
        destination = f"{UPLOADS_DIRECTORY}{image.filename}"
        with open(destination, "wb") as fileBuffer:
            shutil.copyfileobj(image.file, fileBuffer)


# TODO: implement rate limits for this endpoint
@app.post("/get-diagnose")
def get_diagnose(
        patient_report: Annotated[PatientReport, Form()],
        symptom_images: Annotated[List[UploadFile] | None, File()],
        current_user: Annotated[User, Depends(get_current_user)]):
    """
        This endpoint serves as a contact with GenAI API,
        to obtain a diagnosis based on the description.
    """
    upload_images(current_user, symptom_images)

    request_failed_msg = "Requesting diagnose failed, please try again later."
    try:
        prompt = build_diagnose_prompt(patient_report)
        response = client.responses.parse(
            model="gpt-4o",
            input=[  # enable adding pictures and enforce size limits (costs)
                {"role": "system", "content": prompt.system_instruction},
                {"role": "user", "content": prompt.query}
            ],
            temperature=prompt.temperature,
            text_format=DoctorsResponse,
            user=str(current_user.id)
        )  # TODO: add timeout (set up default value for 1 min)
        # TODO: refactor checking response correctness into function
        response_content = response.output[0].content[0]

        if not response_content.parsed:
            logger.error("OpenAI API did not parse the response properly.")
            return error_response(message=request_failed_msg)

        parsed_response = response_content.parsed
        jsonable_answer = jsonable_encoder(parsed_response)

        # TODO: implement saving the search (with optionally added images and received diagnoses)
        # save_search(report=patient_report, current_user=current_user, images=)

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_answer)
    # TODO: catch more exceptions - read open API docs to fig. out which can be raised by parse()
    except ValidationError as e:
        logger.error(f"Prompt creation failed: {e}")
        return error_response(message=request_failed_msg)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Designed for handling unexpected crashes.
    :param request:
    :param exc:
    :return:
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )
