# src/core/database.py

from typing import AsyncGenerator, Dict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from fastapi import Query, HTTPException, status
from src.core.config import settings


# ────────────────────────────────────────────────
# Base class for SQLAlchemy models
# ────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ────────────────────────────────────────────────
# Database configuration (SCALABLE)
# ────────────────────────────────────────────────
DATABASE_URLS: Dict[str, str] = {
    "local": settings.DATABASE_URL,
    "supabase": settings.SUPABASE_DB_URL,
    # add more here later
    # "analytics": settings.ANALYTICS_DB_URL,
}

# validate
missing = [k for k, v in DATABASE_URLS.items() if not v]
if missing:
    raise ValueError(f"Missing database URLs for: {missing}")


# ────────────────────────────────────────────────
# Factory
# ────────────────────────────────────────────────
class DatabaseFactory:
    """Manages multiple database engines and sessionmakers."""

    def __init__(self, db_urls: Dict[str, str]):
        self.engines = {}
        self.sessionmakers = {}
        self._init_engines(db_urls)

    def _init_engines(self, db_urls: Dict[str, str]):
        for name, url in db_urls.items():

            connect_args = {}
            if name == "supabase":
                connect_args = {
                    "statement_cache_size": 0,
                    "prepared_statement_cache_size": 0,
                }

            engine = create_async_engine(
                url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300,
                connect_args=connect_args,
            )

            self.engines[name] = engine
            self.sessionmakers[name] = sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

    def get_db_types(self):
        return list(self.engines.keys())

    async def get_session(self, db_type: str = "local") -> AsyncGenerator[AsyncSession, None]:
        db_type = db_type.lower()

        if db_type not in self.sessionmakers:
            raise ValueError(f"Invalid database '{db_type}'. Allowed: {self.get_db_types()}")

        SessionLocal = self.sessionmakers[db_type]

        async with SessionLocal() as session:
            try:
                yield session
                await session.commit()
            except:
                await session.rollback()
                raise


# ────────────────────────────────────────────────
# Singleton
# ────────────────────────────────────────────────
db_factory = DatabaseFactory(DATABASE_URLS)
db_list = tuple(db_factory.get_db_types())


# ────────────────────────────────────────────────
# FastAPI dependency
# ────────────────────────────────────────────────
async def get_chosen_db(
    db: str = Query(default="local", description=f"Target DB: {db_list}")
) -> AsyncGenerator[AsyncSession, None]:
    if db not in db_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid DB. Allowed: {db_list}"
        )

    async for session in db_factory.get_session(db):
        yield session
