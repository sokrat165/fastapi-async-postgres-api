# src/core/database.py
from typing import AsyncGenerator
from src.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from fastapi import Query, HTTPException, status

# Load environment variables (relative path from this file)

DATABASE_URL = settings.DATABASE_URL
SUPABASE_DB_URL = settings.SUPABASE_DB_URL
 
db_list=("local", "supabase")
if not DATABASE_URL or not SUPABASE_DB_URL:
    raise ValueError("Missing DATABASE_URL or SUPABASE_DB_URL in environment")


class DatabaseFactory:
    """Factory for managing multiple database engines and sessions."""
    
    def __init__(self):
        self.engines = {}
        self.sessionmakers = {}
        self._init_engines()

    def _init_engines(self):
        # Local PostgreSQL
        self.engines["local"] = create_async_engine(
            DATABASE_URL,
            echo=False,               # set True for debugging SQL queries
            pool_pre_ping=True,
            pool_recycle=300,
        )

        # Supabase (use connection pooler + disable prepared statements)
        self.engines["supabase"] = create_async_engine(
            SUPABASE_DB_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
            },
        )

        # Create session makers
        for db_type, engine in self.engines.items():
            self.sessionmakers[db_type] = sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

    async def get_session(
        self,
        db_type: str = 'local'
    ) -> AsyncGenerator[AsyncSession, None]:
        """Get AsyncSession for the specified database type."""
        db_type = db_type.lower()
        if db_type not in self.sessionmakers:
            raise ValueError(
                f"Invalid database choice: '{db_type}'. Allowed: 'local', 'supabase'"
            )
        
        SessionLocal = self.sessionmakers[db_type]
        async with SessionLocal() as session:
            yield session


# Singleton instance
db_factory = DatabaseFactory()


# ────────────────────────────────────────────────
# Reusable FastAPI dependency (recommended name)
# ────────────────────────────────────────────────
async def get_chosen_db(
    db: str = Query(
        default="local",
        description="Target database: 'local' (PostgreSQL) or 'supabase'"
    )
) -> AsyncSession:
    """
    FastAPI dependency to inject AsyncSession for the chosen database.
    Usage: db: AsyncSession = Depends(get_chosen_db)
    """
    choice = db.lower().strip()
    if choice not in db_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid database choice. Allowed values: {db_list}"
        )

    async for session in db_factory.get_session(choice):
        yield session


# ────────────────────────────────────────────────
# Compatibility layer – keep old code working
# ────────────────────────────────────────────────

# For old code that imports 'engine'
engine = db_factory.engines["local"]  # defaults to local

# For old code that imports 'async_session_factory'
async_session_factory = db_factory.sessionmakers["local"]

# Base class for models (if still used in some places)
class Base(DeclarativeBase):
    pass


# Fallback for old dependencies that expect get_db() without args
async def get_local_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_factory.get_session("local"):
        yield session


# Optional: simple test function (can be removed later)
async def test_connection(db_type: str = "local"):
    async for db in db_factory.get_session(db_type):
        result = await db.execute(text("SELECT 1"))
        print(f"Connection to {db_type} successful: {result.scalar() == 1}")