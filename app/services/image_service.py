import shutil
from typing import List

from fastapi import HTTPException, status, UploadFile

from app.core.config import settings
from app.core.exceptions import error_response
from app.models.user import User


def check_upload_criteria(current_user: User, symptom_images: List[UploadFile]):
    if symptom_images is not None and not current_user.has_premium_tier:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="For uploading images you need to have a paid premium tier."
        )

    if symptom_images is not None and len(symptom_images) > 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="It is only possible to upload a maximum of 3 images.")


def upload_images(current_user: User, symptom_images: List[UploadFile]):
    check_upload_criteria(current_user, symptom_images)

    saved_images = []
    allowed_mime_types = {"image/jpeg", "image/png", "image/webp"}
    for image in symptom_images:
        if image.content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported media type: only image files in jpeg, png or webp format are allowed."
            )

        # image_data = await image.read()
        # image = Image.open(io.BytesIO(image_data))
        destination = f"{settings.UPLOADS_DIRECTORY}/{image.filename}"
        try:
            with open(destination, "wb") as file_buffer:
                shutil.copyfileobj(image.file, file_buffer)
        except IOError:
            return error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Error occurred when saving images. Please try again later."
            )

        saved_images.append(destination)

    return saved_images
