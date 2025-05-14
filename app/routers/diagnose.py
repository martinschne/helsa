from typing import Annotated, List

from fastapi import Depends, File, Form, status, UploadFile, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from openai import OpenAI, APIError, RateLimitError, BadRequestError, AuthenticationError
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import error_response
from app.core.logging import logger
from app.core.security import get_current_user
from app.core.types import DBSessionDependency
from app.models.consultation import ResponseTone, LanguageStyle, DoctorsResponse, PatientReport
from app.models.user import User
from app.services.image_service import upload_images, encode_images_to_base64, base64_images_to_urls
from app.services.prompt_service import build_diagnose_prompt
from app.services.search_service import save_search, create_search

router = APIRouter()

client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=120)


# TODO: implement rate limits for this endpoint
@router.post("/diagnose", tags=["diagnose"])
def get_diagnose(
        current_user: Annotated[User, Depends(get_current_user)],
        session: DBSessionDependency,
        symptoms: Annotated[str, Form()],
        duration: Annotated[str | None, Form()] = None,
        age_years: Annotated[int | None, Form()] = None,
        symptom_images: List[UploadFile] = File(default=[]),
        response_tone: ResponseTone = ResponseTone.PROFESSIONAL,
        language_style: LanguageStyle = LanguageStyle.SIMPLE
):
    """
        This endpoint serves as a contact with GenAI API,
        to obtain a diagnosis based on the description.
    """
    logger.info(f"Symptom images: {symptom_images}")

    images = upload_images(current_user, symptom_images)
    image_paths = [image.filename for image in images]
    base64_images = encode_images_to_base64(image_paths)
    image_urls = base64_images_to_urls(base64_images)

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
            input=[
                {"role": "system", "content": prompt.system_instruction},
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt.query},
                        *[{"type": "input_image", "image_url": url, "detail": "high"} for url in image_urls]
                    ]
                }
            ],
            temperature=prompt.temperature,
            text_format=DoctorsResponse,
            user=str(current_user.id)
        )

        parsed_response = response.output[0].content[0].parsed
        if not parsed_response:
            logger.error("OpenAI API did not parse the response properly.")
            return error_response(message="Requesting diagnose failed, please try again later.")

        search = create_search(
            report=patient_report,
            user=current_user,
            response=parsed_response,
            images=images
        )
        save_search(search, session)

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(parsed_response))
    except ValidationError as e:
        logger.error(f"OpenAI Validation error: {e}")
        return error_response(status_code=status.HTTP_400_BAD_REQUEST,
                              message="Invalid output from AI service. Please try again later.")
    except APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return error_response(status_code=status.HTTP_502_BAD_GATEWAY,
                              message="AI service is not available. Please try again later.")
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        return error_response(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                              message="Too many requests. Please wait and retry later.")
    except BadRequestError as e:
        logger.error(f"Bad request: {e}")
        return error_response(status_code=status.HTTP_400_BAD_REQUEST, message="Invalid input.")
    except AuthenticationError as e:
        logger.critical(f"Authentication failed: {e}")
        return error_response(status_code=status.HTTP_401_UNAUTHORIZED,
                              message="Authentication with AI service failed.")
    except Exception as e:
        logger.exception("Unexpected error while obtaining AI response.")
        return error_response(message="An unexpected error occurred while obtaining the diagnosis.")