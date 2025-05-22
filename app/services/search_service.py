from PIL.ImageFile import ImageFile
from sqlmodel import Session

from app.models.consultation import PatientReport, Diagnose, DoctorsResponse
from app.models.search import SearchImage, SearchDiagnose, Search
from app.models.user import User


def _create_search_diagnose(diagnose: Diagnose):
    """
    Created `SearchDiagnose` based on `Diagnose`.

    :param diagnose: diagnose containing name, description and recommended action
    :return: `SearchDiagnose` instance with data from `Diagnose`
    """
    return SearchDiagnose(
        name=diagnose.name,
        description=diagnose.description,
        recommended_action=diagnose.recommended_action
    )


def _create_search_image(image: ImageFile):
    """
    Create `SearchImage` based on the data from provided image file.

    :param image: image file carrying needed `size` and `filename` data
    :return: `SearchImage` instance
    """
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
    """
    Create `Search` based on data from patient's report, images, user data and response from AI.

    :param report: patients report containing symptom data
    :param user: user making the search
    :param response: AI generated parsed response in `DoctorsResponse` format
    :param images: list of image files related to the search
    :return: `Search` instance
    """
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
    """
    Save the provided `Search` to the db.

    :param search: `Search` with data to save
    :param session: db `Session` instance
    """
    session.add(search)
    session.commit()
    session.refresh(search)
