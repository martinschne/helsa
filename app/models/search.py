import uuid
from datetime import datetime, timezone
from typing import List

from sqlmodel import SQLModel, Field, Relationship


class Search(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    symptoms: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    diagnoses: List["Diagnose"] = Relationship(back_populates="search")
    images: List["Image"] | None = Relationship(back_populates="search")


class Diagnose(SQLModel, table=True):
    name: str = Field(nullable=False)
    description: Field(nullable=False)
    recommended_action: Field(nullable=False)
    search_id: str = Field(nullable=False)
    search: "Search" = Relationship(back_populates="diagnoses")


class Image(SQLModel, table=True):
    image_url: str = Field(nullable=False)
    width: int = Field(nullable=False)
    height: int = Field(nullable=False)
    search_id: str = Field(nullable=False)
    search: "Search" = Relationship(back_populates="images")
