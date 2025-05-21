import base64
import os
import uuid

from PIL import Image, ExifTags
from PIL.Image import Resampling
from fastapi import HTTPException, status, UploadFile

from app.core.config import settings
from app.core.exceptions import exception_response
from app.models.user import User
from app.services import constants


def _get_exif_orientation_key():
    orientation = None
    for orientation_key in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation_key] == 'Orientation':
            orientation = orientation_key

    return orientation


def _rotate_image(image: Image.Image):
    image_exif = image.getexif()
    if image_exif:
        orientation_key = _get_exif_orientation_key()
        exif = dict(image_exif.items())
        if exif.get(orientation_key) == 3:
            image = image.rotate(180, expand=True)
        elif exif.get(orientation_key) == 6:
            image = image.rotate(270, expand=True)
        elif exif.get(orientation_key) == 8:
            image = image.rotate(90, expand=True)

    return image


def check_upload_criteria(current_user: User, symptom_images: list[UploadFile]):
    max_images_count = 3
    if symptom_images is not None and not current_user.has_premium_tier:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=constants.IMAGE_SERVICE_EXC_MSG_NO_PREMIUM_TIER
        )

    if symptom_images is not None and len(symptom_images) > max_images_count:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=constants.IMAGE_SERVICE_EXC_MSG_IMAGE_COUNT_EXCEEDED.format(max_images_count)
        )


def upload_images(user: User, symptom_images: list[UploadFile]):
    check_upload_criteria(user, symptom_images)

    saved_images = []
    allowed_mime_types = {"image/jpeg", "image/png", "image/webp"}
    for img_file in symptom_images:
        if img_file.content_type not in allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=constants.IMAGE_SERVICE_EXC_MSG_UNSUPPORTED_IMAGE_FORMAT
            )

        uploaded_filename = f"{uuid.uuid4()}{os.path.splitext(img_file.filename)[1]}"
        upload_destination = os.path.join(settings.UPLOADS_DIRECTORY, uploaded_filename)
        try:
            # process original image
            image = Image.open(img_file.file)
            image = image.convert("RGB")
            image = _rotate_image(image)
            image.thumbnail(size=(2048, 2048), resample=Resampling.LANCZOS)
            # collect the properties for new image
            mode = image.mode
            size = image.size
            image_data = list(image.getdata())
            image.close()
            # create and save new image - based on original, without exif data
            image_sans_exif = Image.new(mode, size)
            image_sans_exif.putdata(image_data)
            image_sans_exif.filename = upload_destination
            image_sans_exif.save(fp=upload_destination, format='JPEG', optimize=True)
        except IOError:
            raise exception_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=constants.IMAGE_SERVICE_EXC_MSG_SAVING_IO_ERROR
            )

        saved_images.append(image_sans_exif)

    return saved_images


# for development: encode image to base64 format
# for deployment: serve mounted static files directly
def image_to_base64(image_path: str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# for development - convert list of image paths to a list of base64 strings
def encode_images_to_base64(image_paths: list[str]):
    return [image_to_base64(path) for path in image_paths]


def base64_images_to_urls(base64_images: list[str]):
    return [f"data:image/jpeg;base64,{image}" for image in base64_images]
