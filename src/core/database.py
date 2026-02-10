# from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker

# from sqlalchemy.orm import DeclarativeBase
# #orm is object-relational mapping, it is a technique that allows you to interact with a database using object-oriented programming concepts. It provides a way to map database tables to Python classes and allows you to perform database operations using Python objects instead of writing raw SQL queries.

# from src.core.config import settings

# #create_async_engine --> async_sessionmaker --> AsyncSession

# # crate_async_engine to connect to the database
# #check_same_thread=False is used to allow multiple threads to access the database at the same time. It is necessary when using SQLite in a multi-threaded environment, as SQLite does not allow multiple threads to access the same database file simultaneously by default.
# engine=create_async_engine(settings.DATABASE_URL,echo=True)

# #async_sessionmaker to create a session for interacting with the database
# #expire_on_commit=False is used to prevent the session from expiring the objects after a commit. This means that the objects will still be available in the session after a commit, and you can continue to work with them without having to refresh them from the database.
# async_session_factory=async_sessionmaker(engine,expire_on_commit=False,class_=AsyncSession)



# class Base(DeclarativeBase):
#     pass

# src/core/database.py
# src/core/database.py
# src/core/database.py
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
from fastapi import Query, HTTPException, status

# Load environment variables (relative path from this file)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
DEFAULT_DB = os.getenv("DEFAULT_DB", "local").lower()

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
        db_type: str = DEFAULT_DB
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
    if choice not in ("local", "supabase"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid database choice. Allowed values: 'local' or 'supabase'"
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