import logging

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.core.types import DBSessionDependency
from app.models.user import UserFlagsRequest
from app.repositories.user_repository import get_user, save_user_flags

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.post("/set-user-flags")
def set_user_flags(user_flags_request: UserFlagsRequest, session: DBSessionDependency):
    success_message = (f"User {user_flags_request.username} have been "
                       f"updated with flags: {str(str(user_flags_request.user_flags.model_dump_json()))}")

    user = get_user(str(user_flags_request.username), session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_flags_request.user_name} not found. Flags were not set."
        )

    save_user_flags(user, user_flags_request.user_flags, session)
    logging.info(success_message)

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": success_message})
