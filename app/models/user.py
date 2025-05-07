import uuid
from datetime import datetime, timezone

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
    searches: list[Search] | None = Relationship(back_populates="user", cascade_delete=True)


class UserCreate(BaseModel):
    username: EmailStr
    password: str
