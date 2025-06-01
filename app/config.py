# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "HCA FastAPI Backend"
    PROJECT_DESCRIPTION: str = "A cross-platform FastAPI backend with live reload capability"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
