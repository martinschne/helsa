import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field, Relationship

from app.models.search import Search


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: EmailStr = Field(index=True, nullable=False, unique=True)
    password_hash: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_verified: bool = Field(default=False, nullable=False)
    is_active: bool = Field(default=False, nullable=False)
    is_admin: bool = Field(default=False, nullable=False)
    has_premium_tier: bool = Field(default=False, nullable=False)
    searches: List["Search"] | None = Relationship(back_populates="user", cascade_delete=True)


class UserCreate(BaseModel):
    username: EmailStr
    password: str


class UserFlags(BaseModel):
    is_verified: bool | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    has_premium_tier: bool | None = None
    model_config = {"extra": "forbid"}


class UserFlagsRequest(BaseModel):
    username: EmailStr
    user_flags: UserFlags