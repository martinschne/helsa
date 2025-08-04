import logging

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from src.helsa.core.types import DBSessionDependency
from src.helsa.models.user import UserFlagsRequest
from src.helsa.repositories.user_repository import get_user, save_user_flags
from src.helsa.routers import constants

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.post("/set-user-flags",
             summary=constants.ADMIN_SET_USER_FLAGS_SUMMARY,
             description=constants.ADMIN_SET_USER_FLAGS_DESCRIPTION)
def set_user_flags(user_flags_request: UserFlagsRequest, session: DBSessionDependency):
    """
    This endpoint allows admin to set user flags for an existing user saved in db.

    :param user_flags_request: request model for setting user flags for given username
    :param session: db `Session` instance
    :raise HttpException (400 Bad Request): if username from user_flags_request was not found in db.
    :return: `JSONResponse` with success message, if flags were set and saved in user db record.
    """
    success_message = constants.ADMIN_SUCCESS_MSG_FLAGS_SET.format(
        flags=str(user_flags_request.user_flags.model_dump_json(exclude_none=True))
    )

    user = get_user(str(user_flags_request.username), session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=constants.ADMIN_EXC_MSG_NO_USER_FLAGS_UNSET
        )

    save_user_flags(user, user_flags_request.user_flags, session)
    logging.info(success_message)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": success_message})
