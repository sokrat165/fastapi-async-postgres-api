# # src/api/dependencies/db.py
# from fastapi import Query, HTTPException, status
# from sqlalchemy.ext.asyncio import AsyncSession
# from typing import AsyncGenerator

# from src.core.database import db_factory, db_list  # use the singleton from core

# async def get_chosen_db(
#     db: str = Query(
#         default="local",
#         description="Database to use: 'local' or 'supabase'"
#     )
# ) -> AsyncGenerator[AsyncSession, None]:
#     """
#     FastAPI dependency to inject AsyncSession for the chosen database.
#     Usage: db: AsyncSession = Depends(get_chosen_db)
#     """
#     choice = db.lower().strip()
#     if choice not in db_list:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid database choice. Allowed: {db_list}"
#         )

#     async for session in db_factory.get_session(choice):
#         yield session

# src/api/dependencies/db.py
from fastapi import Query, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator, Annotated

from src.core.database import db_factory, db_list  # your singleton factory & list


async def get_chosen_db(
    db: Annotated[
        str,
        Query(
            default="local",
            description="Database to use: 'local' (PostgreSQL) or 'supabase'"
        )
    ]
) -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to provide AsyncSession for the chosen database.
    
    Usage in endpoint:
        async def some_endpoint(db: AsyncSession = Depends(get_chosen_db)):
            ...
    """
    choice = db.lower().strip()

    if choice not in db_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid database choice '{choice}'. Allowed values: {', '.join(db_list)}"
        )

    try:
        async for session in db_factory.get_session(choice):
            yield session
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed for '{choice}': {str(e)}"
        )