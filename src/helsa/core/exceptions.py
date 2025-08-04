from fastapi.exceptions import HTTPException


def exception_response(message: str = "Internal server error",
                       status_code: int = 500) -> HTTPException:
    """
    Factory method for error responses.

    :param message: optionally customizable error message
    :param status_code: http response status code
    :return: `HTTPException` object with status code and detail
    """
    return HTTPException(status_code=status_code, detail=message)

