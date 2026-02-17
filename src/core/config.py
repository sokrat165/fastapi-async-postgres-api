# src/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
# security
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from typing import ClassVar

# Security helpers (unchanged)


class Settings(BaseSettings):
    # PostgreSQL connection URL for SQLAlchemy
    DATABASE_URL: str
    SECRET_KEY: str | None = "change-this-to-a-very-long-random-string-64+chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SUPABASE_DB_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    COHERE_API_KEY: str
    GROQ_API_KEY: str   # ← change from XAI_GROK_API_KEY
    GROQ_API_BASE_URL: str = "https://api.groq.com/openai/v1"
    pwd_context: ClassVar[CryptContext] = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme: ClassVar[OAuth2PasswordBearer] = OAuth2PasswordBearer(tokenUrl="token")
    http_bearer: ClassVar[HTTPBearer] = HTTPBearer()
    model_config = SettingsConfigDict(
        env_file="src/.env",           # or ".env" if in project root
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached singleton instance of Settings.
    This is the recommended way to access config in FastAPI.
    """
    return Settings()


# Optional: legacy direct access (you can remove these later)
settings = get_settings()
# SECRET_KEY = settings.SECRET_KEY
# ALGORITHM = settings.ALGORITHM
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# print("DATABASE_URL =", settings.DATABASE_URL)