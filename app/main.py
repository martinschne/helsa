import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from openai import OpenAI
from passlib.context import CryptContext
from sqlmodel import Session, select
from starlette import status

from app.database import create_db_and_tables, get_session
from app.models import Token, User, UserCreate, TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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


def authenticate_user(username: str, password: str, session: SessionDep) -> bool | User:
    """
    Authenticate user by verifying password.
    """
    statement = select(User).where(User.username == username)
    results = session.exec(statement)
    user = results.first()

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
    username_check = session.exec(select(User).where(User.username == user_create.username)).first()
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


@app.post("/get-diagnose")
def get_diagnose(current_user: Annotated[User, Depends(get_current_user)]):
    """
        This endpoint serves as a contact with GenAI API,
        to obtain a diagnosis based on the description.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "assistant",
                    "content": "You are a doctor who acts professionally and deeply care about his patients."
                },
                {
                    "role": "user",
                    "content": "The patients describes following symptoms: I have a headache and feeling thirsty. What would be the possible diagnosis and what are the recommended steps for the patient to do."
                }
            ],
            max_tokens=200
        )

        processed_answer = response.choices[0].message.content
        return {"username": current_user.username, "diagnosis": processed_answer}
    except Exception as e:
        print(e)
        return None

