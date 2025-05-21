from pydantic import BaseModel


class Token(BaseModel):
    """ Standard response format for authentication endpoint. """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """ Wrapper model for token data. """
    username: str | None = None
