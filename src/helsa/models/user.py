import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import EmailStr, BaseModel, field_validator
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """
    DB model defining data saved into `user` table.

    It also defines relationships to other sql models:
        * zero or more searches for one user
    """
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
    """
    Model holding credentials for registering a new user.

    It also contains password validation. A valid password must:
        * be at least eight characters long
        * contain at least one uppercase, one lowercase character and one digit
    """
    username: EmailStr
    password: str

    @field_validator("password")
    def check_password(cls, value):
        value = str(value)
        if len(value) < 8:
            raise ValueError("Password must have at least 8 characters")
        if not any(c.isupper() for c in value):
            raise ValueError("Password must have at least one uppercase letter")
        if not any(c.islower() for c in value):
            raise ValueError("Password must have at least one lowercase letter")
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must have at least one digit")
        return value


class UserFlags(BaseModel):
    """ Model encapsulating user flags for user settings. """
    is_verified: bool | None = None
    is_active: bool | None = None
    is_admin: bool | None = None
    has_premium_tier: bool | None = None
    model_config = {"extra": "forbid"}


class UserFlagsRequest(BaseModel):
    """ Request model for setting user flags on user. """
    username: EmailStr
    user_flags: UserFlags
