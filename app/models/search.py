import uuid
from datetime import datetime, timezone
from typing import List

from sqlmodel import SQLModel, Field, Relationship

from app.models.consultation import ResponseTone, LanguageStyle


class Search(SQLModel, table=True):
    """
    DB model defining data saved into the 'search' table.
    It also defines relationships to other sql models:
        * zero or more searches for one user
        * zero or more search images for one search
        * zero or more diagnoses for one search
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    symptoms: str = Field(nullable=False)
    diagnoses: list["SearchDiagnose"] = Relationship(back_populates="search", cascade_delete=True)
    patient_age_years: int | None = Field(nullable=True)
    response_tone: ResponseTone = Field(nullable=False)
    language_style: LanguageStyle = Field(nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="searches")
    images: List["SearchImage"] | None = Relationship(back_populates="search", cascade_delete=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SearchDiagnose(SQLModel, table=True):
    """
    DB model defining diagnose related to a search and its attributes.
    Each search diagnose belongs to one specific search.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False)
    description: str = Field(nullable=False)
    recommended_action: str = Field(nullable=False)
    search_id: uuid.UUID = Field(foreign_key="search.id")
    search: Search = Relationship(back_populates="diagnoses")


class SearchImage(SQLModel, table=True):
    """
    DB model defining image related to a search and its attributes.
    Each search image belongs to one specific search.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    image_src: str = Field(nullable=False)
    width: int = Field(nullable=False)
    height: int = Field(nullable=False)
    search_id: uuid.UUID = Field(foreign_key="search.id")
    search: Search = Relationship(back_populates="images")
