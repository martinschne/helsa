from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # env. variables
    SECRET_KEY: str
    OPENAI_API_KEY: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    BUILD_TARGET: str
    SERVER_PORT: str
    SERVER_DEBUG_PORT: str
    DB_PORT: str

    # constants
    UPLOADS_DIRECTORY: str = "./app/static/uploads"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    model_config = {
        "env_file": ".env"
    }


settings = Settings()
