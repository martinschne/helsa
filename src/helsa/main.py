import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.requests import Request

from src.helsa.core.config import settings
from src.helsa.core.exceptions import exception_response
from src.helsa.core.logging import logger
from src.helsa.database import create_db_and_tables
from src.helsa.routers import access, diagnose, admin


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
    Handles uncaught exceptions and logs unexpected server errors.

    Logs the error details and raises a standardized error response.
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    raise exception_response()