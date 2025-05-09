from typing import Annotated, List

from fastapi import Depends, File, Form, status, UploadFile, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from openai import OpenAI
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import error_response
from app.core.logging import logger
from app.core.security import get_current_user
from app.models.consultation import ResponseTone, LanguageStyle, DoctorsResponse, PatientReport
from app.models.user import User
from app.services.image_service import upload_images
from app.services.prompt_service import build_diagnose_prompt

router = APIRouter()

client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=120)


# TODO: implement rate limits for this endpoint
@router.post("/diagnose", tags=["diagnose"])
def get_diagnose(
        current_user: Annotated[User, Depends(get_current_user)],
        symptoms: Annotated[str, Form()],
        duration: Annotated[str | None, Form()] = None,
        age_years: Annotated[int | None, Form()] = None,
        symptom_images: Annotated[List[UploadFile] | None, File()] = None,
        response_tone: ResponseTone = ResponseTone.PROFESSIONAL,
        language_style: LanguageStyle = LanguageStyle.SIMPLE
):
    """
        This endpoint serves as a contact with GenAI API,
        to obtain a diagnosis based on the description.
    """
    upload_images(current_user, symptom_images)
    request_failed_msg = "Requesting diagnose failed, please try again later."
    try:
        patient_report = PatientReport(
            response_tone=response_tone,
            language_style=language_style,
            symptoms=symptoms,
            duration=duration,
            age_years=age_years
        )

        prompt = build_diagnose_prompt(patient_report)

        response = client.responses.parse(
            model="gpt-4.1",
            input=[  # enable adding pictures and enforce size limits (costs)
                {"role": "system", "content": prompt.system_instruction},
                {"role": "user", "content": prompt.query}
            ],
            temperature=prompt.temperature,
            text_format=DoctorsResponse,
            user=str(current_user.id)
        )
        response_content = response.output[0].content[0]

        if not response_content.parsed:
            logger.error("OpenAI API did not parse the response properly.")
            return error_response(message=request_failed_msg)

        parsed_response = response_content.parsed
        jsonable_response = jsonable_encoder(parsed_response)

        # TODO: implement saving the search (with optionally added images and received diagnoses)
        # save_search(report=patient_report, current_user=current_user, images=)

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_response)
    # TODO: catch more exceptions - read open API docs to fig. out which can be raised by parse()
    except ValidationError as e:
        validation_error_message = f"Validation error: {e.errors}"
        logger.error(validation_error_message)

        return error_response(status_code=status.HTTP_400_BAD_REQUEST, message=validation_error_message)
