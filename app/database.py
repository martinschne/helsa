from sqlmodel import Session, SQLModel, create_engine

from app.models import User

DATABASE_URL = "sqlite:///./helsa.db"
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
