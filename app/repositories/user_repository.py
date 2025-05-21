from sqlmodel import Session, select

from app.models.user import User, UserFlags


def get_user(username: str, session: Session) -> User:
    """
    Helper method to get a user instance from db.

    :param username: username to search for in the db
    :param session: db `Session` instance
    :return: `User` instance obtained from db
    """
    user = session.exec(select(User).where(User.username == username)).first()

    return user


def save_user_flags(user: User, user_flags: UserFlags, session: Session):
    """
    Save set flags for a user to the db.

    :param user: user model instance
    :param user_flags: `UserFlags` model instance with user flags set
    :param session: db `Session` instance
    """
    for key, value in user_flags.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
