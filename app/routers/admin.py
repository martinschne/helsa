import logging

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.core.types import DBSessionDependency
from app.models.user import UserFlagsRequest
from app.repositories.user_repository import get_user, save_user_flags
from app.routers import constants

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.post("/set-user-flags")
def set_user_flags(user_flags_request: UserFlagsRequest, session: DBSessionDependency):
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
