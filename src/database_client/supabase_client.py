# ────────────────────────────────────────────────
# Existing local database code (keep it unchanged)
# ...

# ── Add this for Supabase ─────────────────────────
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL")
if not SUPABASE_DB_URL:
    raise ValueError("SUPABASE_DB_URL environment variable is not set")

supabase_engine = create_async_engine(
    SUPABASE_DB_URL,
    echo=True,  # keep for now to see logs
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "statement_cache_size": 0,           # ← Critical for pooler
        "prepared_statement_cache_size": 0,
        
    },
    
)
SupabaseSessionLocal = sessionmaker(
    supabase_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_supabase_db():
    """Dependency to get Supabase DB session"""
    async with SupabaseSessionLocal() as session:
        yield session