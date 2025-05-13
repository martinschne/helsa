import os
import shutil
import uuid
from typing import List

from fastapi import HTTPException, status, UploadFile

from app.core.config import settings
from app.core.exceptions import error_response
from app.models.user import User


def adjust_image_resolution():
    pass


def check_upload_criteria(current_user: User, symptom_images: List[UploadFile]):
    max_images_count = 3
    if symptom_images is not None and not current_user.has_premium_tier:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="For uploading images you need to have a paid premium tier."
        )

    if symptom_images is not None and len(symptom_images) > max_images_count:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Too many images. Maximum allowed count is {max_images_count}."
        )

def upload_images(current_user: User, symptom_images: List[UploadFile]):
    check_upload_criteria(current_user, symptom_images)

    saved_img_paths = []
    allowed_mime_types = {"image/jpeg", "image/png", "image/webp"}
    for image in symptom_images:
        if image.content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Unsupported media type: only image files in jpeg, png or webp format are allowed."
            )

        # image_data = await image.read()
        # image = Image.open(io.BytesIO(image_data))
        uploaded_filename = f"{uuid.uuid4()}{os.path.splitext(image.filename)[1]}"
        upload_destination = os.path.join(settings.UPLOADS_DIRECTORY, uploaded_filename)
        try:
            with open(upload_destination, "wb") as file_buffer:
                shutil.copyfileobj(image.file, file_buffer)
        except IOError:
            return error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Error occurred when saving images. Please try again later."
            )

        saved_img_paths.append(upload_destination)

    return saved_img_paths
