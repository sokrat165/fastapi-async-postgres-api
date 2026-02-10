from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer


SECRET_KEY = os.getenv("SECRET_KEY", "change-this-to-a-very-long-random-string-64+chars")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")   # ← this enables the nice login form in /docs
http_bearer = HTTPBearer()

# ── Models ────────────────────────
class Settings(BaseSettings):
    # PostgreSQL connection URL for SQLAlchemy
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file="src/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )



settings = Settings()
print("DATABASE_URL =", settings.DATABASE_URL)
