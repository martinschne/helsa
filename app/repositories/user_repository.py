from sqlmodel import Session, select

from app.models.user import User, UserFlags


def get_user(username: str, session: Session) -> User:
    user = session.exec(select(User).where(User.username == username)).first()

    return user


def save_user_flags(user: User, user_flags: UserFlags, session: Session):
    for key, value in user_flags.model_dump(exclude_none=True).items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
