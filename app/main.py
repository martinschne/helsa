from contextlib import asynccontextmanager
from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlmodel import select
from starlette import status

from app.database import create_db_and_tables, SessionDep
from app.models import User, UserCreate, Token

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# define startup behavior (initialize db if does not exists)
@asynccontextmanager
async def lifespan(_: FastAPI):
    # ⏫ Startup
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


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


def authenticate_user(username: str, password: str, session: SessionDep) -> User | bool:
    """
    Authenticate user by verifying password.
    """
    statement = select(User).where(User.username == username)
    results = session.exec(statement)
    user = results.first()
    if not user and not verify_password(password, user.password_hash):
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
    # Check for duplicate email or username
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
