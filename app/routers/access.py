from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.core.config import settings
from app.core.security import create_access_token, hash_password
from app.core.types import DBSessionDependency
from app.models.security import Token
from app.models.user import UserCreate, User
from app.routers import constants
from app.services.auth_service import authenticate_user

router = APIRouter(
    prefix="/access",
    tags=["access"]
)


@router.post(
    "/get-access-token",
    summary=constants.ACCESS_GET_ACCESS_TOKEN_SUMMARY,
    description=constants.ACCESS_GET_ACCESS_TOKEN_DESCRIPTION
)
async def get_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: DBSessionDependency
) -> Token:
    """
    Login endpoint that provides client with JWT token for authentication
    assuming correct credentials were provided.

    Response format::

        {
            "access_token": "eyJhbGciOiJIUzI1NiI...",
            "token_type": "bearer"
        }

    :param form_data: user credentials set as form data: `username` and `password`
    :param session: db `Session` instance
    :raise HttpException (401 Unauthorized): if invalid username or password were provided
    :return: standard response format for authentication
    """
    user = authenticate_user(
        username=form_data.username,
        password=form_data.password,
        session=session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=constants.ACCESS_EXC_MSG_INCORRECT_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type=constants.ACCESS_TOKEN_TYPE)


@router.post(
    "/register-user",
    summary=constants.ACCESS_REGISTER_USER_SUMMARY,
    description=constants.ACCESS_REGISTER_USER_DESCRIPTION
)
def register_user(user_create: UserCreate, session: DBSessionDependency):
    """
    Register a new user with valid username and password provided.

    :param user_create: `UserCreate` instance with valid username and password values
    :param session: db `Session` instance
    :raise HttpException (400 Bad Request): if username already exists in db
    :return: `JSONResponse` with success message if new user was registered
    """
    # Check for duplicate email (username)
    username_check = session.exec(select(User).where(User.username == user_create.username)).first()
    if username_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ACCESS_EXC_MSG_USERNAME_EXISTS,
        )

    user = User(username=user_create.username, password_hash=hash_password(user_create.password))
    session.add(user)
    session.commit()
    session.refresh(user)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": constants.ACCESS_SUCCESS_MSG_USER_CREATED}
    )
