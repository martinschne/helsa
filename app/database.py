from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session
from app.models import User

DATABASE_URL = "sqlite:///./helsa.db"
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
