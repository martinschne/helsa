from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # env. variables
    SECRET_KEY: str
    SUPERUSER_PASSWORD: str
    OPENAI_API_KEY: str
    UPLOADS_DIRECTORY: str

    # constants
    DATABASE_URL: str = "sqlite:///./helsa.db"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    model_config = {
        "env_file": ".env"
    }


settings = Settings()
