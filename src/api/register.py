# src/api/register.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.register import UserCreate, UserOut, UserUpdate
from src.repositories.user_Repository import UserRepository  # <-- استخدم الاسم الصحيح
from src.services.user_service import UserService
from src.core.database import get_chosen_db

router = APIRouter(prefix="/register", tags=["register"])

# DI for Repository
def get_user_repo(db: AsyncSession = Depends(get_chosen_db)) -> UserRepository:
    return UserRepository(db)

# DI for Service
def get_user_service(repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(repo)

# Routes
@router.post("/", response_model=UserOut)
async def register_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    return await service.register_user(user)

@router.put("/{username}", response_model=UserOut)
async def update_user(username: str, user_update: UserUpdate, service: UserService = Depends(get_user_service)):
    return await service.update_user(username, user_update)
