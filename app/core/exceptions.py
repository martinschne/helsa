from fastapi.responses import JSONResponse


def error_response(message: str = "Internal server error",
                   status_code: int = 500):
    """Factory method for error responses."""
    return JSONResponse(status_code=status_code, content={"detail": message})
