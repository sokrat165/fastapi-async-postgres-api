from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request

from src.core.config import settings


async def connect_to_mongo(app):
    """Create Motor client and attach to app.state.

    Prefer using `settings.DATABASE_URL` (per your request). If that's not set,
    fall back to `settings.MONGO_URL`.
    """
    # Use DATABASE_URL only (user requested). If missing, attach None.
    uri = settings.MONGO_URL
    if not uri:
        app.state.mongo_client = None
        app.state.mongo_db = None
        return

    app.state.mongo_client = AsyncIOMotorClient(uri)
    # get_default_database() will use the database from the URI if present
    try:
        app.state.mongo_db = app.state.mongo_client.get_default_database()
    except Exception:
        # fallback: allow callers to access client and select a DB themselves
        app.state.mongo_db = None


async def close_mongo_connection(app):
    """Close Motor client on shutdown."""
    client: AsyncIOMotorClient | None = getattr(app.state, "mongo_client", None)
    if client is not None:
        client.close()


def get_mongo_db(request: Request):
    """Dependency - returns the Motor database instance attached to the app.

    Use in path operations like: db = Depends(get_mongo_db)
    If no DB was attached, returns the client (so caller can select a DB) or None.
    """
    db = getattr(request.app.state, "mongo_db", None)
    if db is None:
        # If no default DB was parsed from the URI, return the client so caller can pick
        return getattr(request.app.state, "mongo_client", None)
    return db
