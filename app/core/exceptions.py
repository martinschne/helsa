from fastapi.responses import JSONResponse


def error_response(message: str = "Internal server error",
                   status_code: int = 500) -> JSONResponse:
    """
    Factory method for error responses.
    :param message: optionally customizable error message
    :param status_code: http response status code
    :return: JSONResponse object with status code and json content in format:
    ``{"detail": "message"}``
    """
    return JSONResponse(status_code=status_code, content={"detail": message})
