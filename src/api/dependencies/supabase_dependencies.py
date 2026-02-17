# src/api/dependencies/supabase_dependencies.py
"""
Dependencies for Supabase-specific features (Storage client + DB session).
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from supabase import Client

from src.database_client.supabase_client import get_supabase_client, get_supabase_db
from src.api.dependencies.auth import get_current_user
from src.models.register import User


def get_supabase_client_dep() -> Client:
    """Inject the Supabase client (for Storage uploads, URLs, etc.)."""
    return get_supabase_client()


async def get_supabase_session(db: AsyncSession = Depends(get_supabase_db)) -> AsyncSession:
    """Inject Supabase PostgreSQL async session."""
    return db


async def get_supabase_context(
    current_user: User = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client_dep),
    db: AsyncSession = Depends(get_supabase_session),
):
    """
    Combined context: authenticated user + Supabase client + DB session.
    Use in endpoints that need all three.
    """
    return {
        "user": current_user,
        "supabase": supabase,
        "db": db
    }