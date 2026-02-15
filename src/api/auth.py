
# src/api/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.auth_service import AuthService
from src.repositories.user_Repository import UserRepository
from src.core.security import create_access_token
from src.core.database import get_chosen_db
from src.schemas.token import Token
from src.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/login", tags=["login"])

@router.post("/", response_model=Token, summary="Login and get JWT access token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_chosen_db)
):
    repo = UserRepository(db)
    service = AuthService(repo)

    user = await service.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(access_token=access_token, token_type="bearer")
