from fastapi import APIRouter, HTTPException, status, Depends
from src.core.database import async_session_factory
from src.schemas.register import UserCreate, UserOut
from src.crud.baseregister import UserRepository   


router = APIRouter(prefix="/register", tags=["register"])

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    """
    Register a new user
    """
    async with async_session_factory() as session:
        repo = UserRepository(session)
        created = await repo.create(user)
        return created
    



    
