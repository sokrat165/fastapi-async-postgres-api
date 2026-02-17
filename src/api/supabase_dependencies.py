# src/api/dependencies/supabase_dependencies.py
"""
Dependencies specific to Supabase (Storage + Postgres DB).
Used in endpoints that need Supabase features (file upload, auth, etc.).
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import Client

from src.core.supabase import get_supabase_client, get_supabase_db
from src.api.dependencies.auth import get_current_user
from src.models.register import User


# ────────────────────────────────────────────────
# 1. Supabase Client (Storage + Realtime + Auth)
# ────────────────────────────────────────────────
def get_supabase(
    client: Client = Depends(get_supabase_client)
) -> Client:
    """
    Dependency to inject the Supabase client (supabase-py).
    Use for Storage uploads, signed URLs, Realtime subscriptions, etc.
    
    Example:
        async def upload_file(supabase: Client = Depends(get_supabase)):
            ...
    """
    return client


# ────────────────────────────────────────────────
# 2. Supabase PostgreSQL DB session
# ────────────────────────────────────────────────
async def get_supabase_session(
    db: AsyncSession = Depends(get_supabase_db)
) -> AsyncSession:
    """
    Dependency to get an async SQLAlchemy session connected to Supabase Postgres.
    
    Usage:
        async def some_endpoint(db: AsyncSession = Depends(get_supabase_session)):
            result = await db.execute(...)
    """
    return db


# ────────────────────────────────────────────────
# 3. Combined: Current user + Supabase client + DB session
# ────────────────────────────────────────────────
async def get_supabase_context(
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
    db: AsyncSession = Depends(get_supabase_session),
):
    """
    Convenience dependency for endpoints that need:
    - Authenticated user
    - Supabase client (Storage)
    - Supabase DB session
    
    Example:
        async def upload_and_save(
            file: UploadFile,
            ctx = Depends(get_supabase_context)
        ):
            user = ctx['user']
            supabase = ctx['supabase']
            db = ctx['db']
            ...
    """
    return {
        "user": current_user,
        "supabase": supabase,
        "db": db
    }