import base64
import os
import uuid
from datetime import datetime

from PIL import Image, ExifTags, UnidentifiedImageError
from fastapi import HTTPException, status, UploadFile

from app.core.config import settings
from app.core.exceptions import exception_response
from app.core.logging import logger
from app.models.user import User
from app.services import constants


def _get_exif_orientation_key() -> int | None:
    """
    Get orientation key from exif tags metadata.

    :return: orientation key
    """
    orientation = None
    for orientation_key in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation_key] == 'Orientation':
            orientation = orientation_key

    return orientation


def _rotate_image(image: Image.Image):
    """
    Rotate image based on the orientation value obtained from its metadata.

    :param image: `Image` object
    :return: rotated image
    """
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


def _check_upload_criteria(current_user: User, symptom_images: list[UploadFile]):
    """
    Check if user account and image fits criteria for uploading.

    Uploading criteria:

        * flag `has_premium_tier` set on `User` instance
        * maximum length of `symptom_images` list is 3
        * maximum size of an image file is 5 MB

    The request will be denied if criteria are not met for all uploaded images.

    :param current_user: `User` instance
    :param symptom_images: list of files to upload
    :return:
    """
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

    for img_file in symptom_images:
        if img_file.size > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=constants.IMAGE_SERVICE_EXC_MSG_IMAGE_TOO_LARGE
            )


def upload_images(user: User, symptom_images: list[UploadFile]):
    """
    Process the user uploaded images and save them as static files.

    If images are meeting the upload criteria, they are saved to static directory
    on the server and the list `Image` instances is returned for further processing.
    :param user: `User` instance - owner of images
    :param symptom_images: list of files to upload
    :return: list of `Image` instances
    """
    _check_upload_criteria(user, symptom_images)

    saved_images = []
    for img_file in symptom_images:
        uploaded_filename = f"{uuid.uuid4()}_{datetime.now().strftime("%Y%m%d-%H%M%S")}"
        upload_destination = os.path.join(settings.UPLOADS_DIRECTORY, uploaded_filename)
        try:
            # process original image
            image = Image.open(fp=img_file.file, formats=["JPEG", "PNG", "WEBP"])
            image = image.convert("RGB")
            image = _rotate_image(image)
            # collect the properties for new image
            mode = image.mode
            size = image.size
            image_data = list(image.getdata())
            image.close()
            # create and save new image - based on original, without exif data
            image_sans_exif = Image.new(mode, size)
            image_sans_exif.putdata(image_data)
            image_sans_exif.filename = upload_destination
        except UnidentifiedImageError as e:
            logger.error(constants.IMAGE_SERVICE_EXC_MSG_UNSUPPORTED_IMAGE_FORMAT + ": " + str(e))
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=constants.IMAGE_SERVICE_EXC_MSG_UNSUPPORTED_IMAGE_FORMAT
            )
        except IOError as e:
            logger.error(constants.IMAGE_SERVICE_EXC_MSG_SAVING_IO_ERROR + ": " + str(e))
            raise exception_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=constants.IMAGE_SERVICE_EXC_MSG_SAVING_IO_ERROR
            )
        saved_images.append(image_sans_exif)

    for image_sans_exif in saved_images:
        try:
            image_sans_exif.save(fp=image_sans_exif.filename, format=image_sans_exif.format, optimize=True)
        except OSError as e:
            logger.error(constants.IMAGE_SERVICE_EXC_MSG_SAVING_IO_ERROR + ": " + str(e))
            raise HTTPException(status_code=500, detail=constants.IMAGE_SERVICE_EXC_MSG_SAVING_IO_ERROR)

    return saved_images


def image_to_base64(image_path: str):
    """
    Encode image under provided path to base64 format.

    :param image_path: path to the image
    :return: base64-encoded image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def encode_images_to_base64(image_paths: list[str]):
    """
    Encode images under provided paths to base64 format.

    Intended for development purposes only.
    For production serve static files directly instead of embedding them.
    :param image_paths: list of image paths
    :return: list of base64-encoded image strings
    """
    return [image_to_base64(path) for path in image_paths]


def base64_images_to_urls(base64_images: list[str]):
    """
    Convert a list of base64-encoded images to data URLs.

    Intended for development purposes only.
    For production serve static files directly instead of embedding them.
    :param base64_images: list of base64-encoded image strings.
    :return: list of data URLs in the format: data:image/jpeg;base64,<image data>.
    """
    return [f"data:image/jpeg;base64,{image}" for image in base64_images]