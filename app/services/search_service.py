from PIL.ImageFile import ImageFile
from sqlmodel import Session

from app.models.consultation import PatientReport, Diagnose, DoctorsResponse
from app.models.search import SearchImage, SearchDiagnose, Search
from app.models.user import User


def _create_search_diagnose(diagnose: Diagnose):
    return SearchDiagnose(
        name=diagnose.name,
        description=diagnose.description,
        recommended_action=diagnose.recommended_action
    )


def _create_search_image(image: ImageFile):
    width, height = image.size
    image_src = image.filename
    image.close()
    return SearchImage(image_src=image_src, width=width, height=height)


def create_search(
        report: PatientReport,
        user: User,
        response: DoctorsResponse,
        images: list[ImageFile]
):
    search = Search(
        symptoms=report.symptoms,
        diagnoses=[_create_search_diagnose(diagnose) for diagnose in response.diagnoses],
        patient_age_years=report.age_years,
        response_tone=report.response_tone,
        language_style=report.language_style,
        user_id=user.id,
        user=user,
        images=[_create_search_image(image) for image in images]
    )

    return search


def save_search(search: Search, session: Session):
    session.add(search)
    session.commit()
    session.refresh(search)
