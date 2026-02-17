# ────────────────────────────────────────────────
# Existing local database code (keep it unchanged)
# ...

# ── Add this for Supabase ─────────────────────────
# src/database_client/supabase_client.py
# import os
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv
# import os

# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
# if not SUPABASE_DB_URL:
#     raise ValueError("SUPABASE_DB_URL environment variable is not set")

# supabase_engine = create_async_engine(
#     SUPABASE_DB_URL,
#     echo=True,  # keep for now to see logs
#     pool_pre_ping=True,
#     pool_recycle=300,
#     connect_args={
#         "statement_cache_size": 0,           # ← Critical for pooler
#         "prepared_statement_cache_size": 0,
        
#     },
    
# )
# SupabaseSessionLocal = sessionmaker(
#     supabase_engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )

# async def get_supabase_db():
#     """Dependency to get Supabase DB session"""
#     async with SupabaseSessionLocal() as session:
#         yield session


# src/database_client/supabase_client.py
"""
Central Supabase client + database session factory.
Handles both Storage (files) and PostgreSQL (tables).
"""

import os
from typing import AsyncGenerator

from supabase import create_client, Client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.config import settings  # ← your Settings class with SUPABASE_URL, etc.


# ────────────────────────────────────────────────
# 1. Supabase Storage & Auth client (supabase-py)
# ────────────────────────────────────────────────
def get_supabase_client() -> Client:
    """
    Returns authenticated Supabase client (use service_role key for server-side ops).
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set")

    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY  # service_role for full access
    )


# ────────────────────────────────────────────────
# 2. SQLAlchemy async engine + session for Supabase Postgres
# ────────────────────────────────────────────────
supabase_engine = create_async_engine(
    settings.SUPABASE_DB_URL,
    echo=False,                    # set to True only for debugging
    pool_pre_ping=True,
    pool_recycle=300,              # recycle connections every 5 min
    pool_size=10,
    max_overflow=20,
    connect_args={
        "statement_cache_size": 0,          # important for Supabase connection pooler
        "prepared_statement_cache_size": 0,
    }
)

SupabaseSessionLocal = sessionmaker(
    supabase_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_supabase_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get a new async DB session for Supabase Postgres.
    Usage: db: AsyncSession = Depends(get_supabase_db)
    """
    async with SupabaseSessionLocal() as session:
        yield session


# ────────────────────────────────────────────────
# Optional: helper to get Storage bucket easily
# ────────────────────────────────────────────────
def get_storage_bucket(client: Client, bucket_name: str = "your-bucket-name"):
    return client.storage.from_(bucket_name)