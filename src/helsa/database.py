from sqlmodel import Session, SQLModel, create_engine

from src.helsa.core.config import settings

DB_USER = settings.POSTGRES_USER
DB_PSW = settings.POSTGRES_PASSWORD
DB_NAME = settings.POSTGRES_DB
DATABASE_URL =  f"postgresql://{DB_USER}:{DB_PSW}@db:5432/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """ Create database and the table based on sql models created. """
    SQLModel.metadata.create_all(engine)


def get_session():
    """ Provides `Session` instance for database operations. """
    with Session(engine) as session:
        yield session
