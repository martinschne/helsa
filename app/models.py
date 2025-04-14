from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel


class Token(BaseModel):
    access_token: str
    token_type: str


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: EmailStr = Field(index=True, nullable=False, unique=True)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_verified: bool = Field(default=False, nullable=False)
    is_active: bool = Field(default=False, nullable=False)
    is_admin: bool = Field(default=False, nullable=False)


class UserCreate(BaseModel):
    username: EmailStr
    password: str
