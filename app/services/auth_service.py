from sqlmodel import Session

from app.core.security import verify_password
from app.models.user import User
from app.repositories.user_repository import get_user


def authenticate_user(username: str, password: str, session: Session) -> bool | User:
    """
    Returns authenticated user if user was found in the db and the password is correct.

    :param username: username to find the user by in the db
    :param password: password in plain text format to verify for authentication
    :param session: db `Session` instance
    :return: `User` instance if username and password match the found user record, otherwise False.
    """
    user = get_user(username, session)
    if not user:
        return False

    if not verify_password(password, user.password_hash):
        return False

    return user
