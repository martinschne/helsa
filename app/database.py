from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)


def create_db_and_tables():
    """ Create database and the table based on sql models created. """
    SQLModel.metadata.create_all(engine)


def get_session():
    """ Provides `Session` instance for database operations. """
    with Session(engine) as session:
        yield session
