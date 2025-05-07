import uuid
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, Relationship

from app.models.consultation import ResponseTone, LanguageStyle
from app.models.user import User


class Search(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    symptoms: str = Field(nullable=False)
    diagnoses: list["SearchDiagnose"] = Relationship(back_populates="search", cascade_delete=True)
    patient_age_years: int | None = Field(nullable=True)
    response_tone: ResponseTone = Field(nullable=False)
    language_style: LanguageStyle = Field(nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="search")
    images: list["SearchImage"] | None = Relationship(back_populates="search", cascade_delete=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SearchDiagnose(SQLModel, table=True):
    name: str = Field(nullable=False)
    description: Field(nullable=False)
    recommended_action: Field(nullable=False)
    search_id: str = Field(foreign_key="search.id")
    search: Search = Relationship(back_populates="diagnoses")


class SearchImage(SQLModel, table=True):
    image_url: str = Field(nullable=False)
    width: int = Field(nullable=False)
    height: int = Field(nullable=False)
    search_id: str = Field(foreign_key="search.id")
    search: Search = Relationship(back_populates="images")
