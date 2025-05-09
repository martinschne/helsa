from typing import List

from sqlmodel import Session

from app.models.consultation import PatientReport
from app.models.search import SearchImage, SearchDiagnose, Search
from app.models.user import User


def save_search(report: PatientReport,
                current_user: User,
                images: List[SearchImage],
                diagnoses: List[SearchDiagnose],
                session: Session):
    search = Search(
        symptoms=report.symptoms,
        diagnoses=diagnoses,
        patient_age_years=report.age_years,
        response_tone=report.response_tone,
        language_style=report.language_style,
        user_id=current_user.id,
        user=current_user,
        images=images
    )

    session.add(search)
    session.commit()
    session.refresh(search)
