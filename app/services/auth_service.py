from sqlmodel import Session

from app.core.security import verify_password
from app.models.user import User
from app.repositories.user_repository import get_user


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
