from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # single DATABASE_URL used for all DB connections (SQL and Mongo as requested)
    DATABASE_URL: str
    MONGO_URL:str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
print("DATABASE_URL =", settings.DATABASE_URL)
print("MONGO_URL =", settings.MONGO_URL)