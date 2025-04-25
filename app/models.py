from datetime import datetime, timezone
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints
from sqlmodel import Field, SQLModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


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


class Prompt(BaseModel):
    system_instruction: Annotated[str | None, StringConstraints(strip_whitespace=True)]
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10)]
    temperature: float | None = Field(ge=0, le=2, default=None)
    max_tokens: int | None = None


class ResponseTone(str, Enum):
    FORMAL = "formal"
    FRIENDLY = "friendly"
    DIRECT = "direct"
    FUNNY = "funny"


class LanguageStyle(str, Enum):
    MEDICAL = "medical"
    SIMPLE = "simple"


class SymptomReport(BaseModel):
    tone: ResponseTone = ResponseTone.FORMAL
    style: LanguageStyle = LanguageStyle.SIMPLE
    symptoms: str = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=500)]
    duration: str = Annotated[str | None, StringConstraints(strip_whitespace=True, min_length=10, max_length=250)]
    age_years: int = Field(ge=0, description="Age of the patient in years, rounded up to next whole integer.")
