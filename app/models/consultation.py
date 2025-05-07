from enum import Enum
from typing import Annotated, List

from pydantic import BaseModel, StringConstraints, Field


class Prompt(BaseModel):
    system_instruction: Annotated[str | None, StringConstraints(strip_whitespace=True)]
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10)]
    temperature: float | None = Field(ge=0, le=2, default=None)
    max_tokens: int | None = None


class ResponseTone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FUNNY = "funny"


class LanguageStyle(str, Enum):
    MEDICAL = "medical"
    SIMPLE = "simple"


class PatientReport(BaseModel):
    response_tone: ResponseTone = ResponseTone.PROFESSIONAL
    language_style: LanguageStyle = LanguageStyle.SIMPLE
    symptoms: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)]
    duration: Annotated[str | None, StringConstraints(strip_whitespace=True, min_length=5, max_length=250)]
    age_years: Annotated[int, Field(ge=0, description="Age of the patient in years, rounded up to next whole integer.")]


class Diagnose(BaseModel):
    name: str
    description: str
    recommended_action: str


class DoctorsResponse(BaseModel):
    diagnoses: List[Diagnose]
