# src/api/register.py# src/api/register.py
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.register import UserCreate, UserOut,UserUpdate
from src.crud.baseregister import UserRepository
from src.core.database import db_factory, get_chosen_db
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)


router = APIRouter(prefix="/register", tags=["register"])



def get_user_repository(db: AsyncSession=Depends(get_chosen_db)) -> UserRepository:
    return UserRepository(db)





@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user in the selected database. Use ?db=supabase to store in Supabase."
)
async def register_user(
    user: UserCreate,
    repo:UserRepository = Depends(get_user_repository)):
    """
    Register a new user

    Query parameter:
    - db: "local" (default) or "supabase"
    """
    
    try:
        created = await repo.create(user)
        return created

    except Exception as exc:
        await repo.session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(exc)}"
        ) from exc
    
async def update_user(
    username: str,
    user_update: UserUpdate,
    repo: UserRepository = Depends(get_user_repository)
):

    try:
        updated = await repo.update(username, user_update)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated

    except Exception as exc:
        await repo.session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Update failed: {str(exc)}"
        ) from exc