from enum import Enum
from typing import Annotated, List

from pydantic import BaseModel, StringConstraints, Field


class Prompt(BaseModel):
    """ Represents a prompt with its settings. """
    system_instruction: Annotated[str | None, StringConstraints(strip_whitespace=True)]
    query: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10)]
    temperature: float | None = Field(ge=0, le=2, default=None)
    max_tokens: int | None = None


class ResponseTone(str, Enum):
    """ Requested tone of the response """
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FUNNY = "funny"


class LanguageStyle(str, Enum):
    """ Requested language style of the response """
    MEDICAL = "medical"
    SIMPLE = "simple"


class SexAssignedAtBirth(str, Enum):
    """ Sex assigned at birth """
    MALE = "male"
    FEMALE = "female"
    INTERSEX = "intersex"


class PatientReport(BaseModel):
    """ Model representing data provided by patient for obtaining the diagnoses. """
    response_tone: ResponseTone = ResponseTone.PROFESSIONAL
    language_style: LanguageStyle = LanguageStyle.SIMPLE
    saab: SexAssignedAtBirth | None = None
    symptoms: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=500)]
    duration: Annotated[str | None, StringConstraints(strip_whitespace=True, min_length=5, max_length=250)]
    age_years: Annotated[
        int | None, Field(ge=0, description="Age of the patient in years, rounded up to next whole integer.")]


class Diagnose(BaseModel):
    """ Required format of a diagnosis present in response. """
    name: str
    description: str
    recommended_action: str


class DoctorsResponse(BaseModel):
    """ Model representing the format of returned response: list of diagnoses. """
    diagnoses: List[Diagnose]
