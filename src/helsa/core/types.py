from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.helsa.database import get_session

DBSessionDependency = Annotated[Session, Depends(get_session)]