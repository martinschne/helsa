import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.requests import Request

from app.core.config import settings
from app.core.exceptions import error_response
from app.core.logging import logger
from app.database import create_db_and_tables
from .routers import access, diagnose, admin

os.makedirs(settings.UPLOADS_DIRECTORY, exist_ok=True)

@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(access.router)
app.include_router(diagnose.router)
app.include_router(admin.router)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Designed for handling unexpected crashes.
    :param request:
    :param exc:
    :return:
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return error_response()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
