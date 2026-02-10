from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm

from src.core.database import async_session_factory
from src.crud.baseregister import UserRepository
from src.core.security import verify_password, create_access_token
from src.schemas.token import Token
from src.core.config import ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(prefix="/login", tags=["login"])

async def authenticate_user(repo: UserRepository, username: str, password: str):
    user = await repo.get_by_username_and_password(username, password)
    return user

@router.post("/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    User login to obtain JWT token
    """
    async with async_session_factory() as session:
        repo = UserRepository(session)
        user = await authenticate_user(repo, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

