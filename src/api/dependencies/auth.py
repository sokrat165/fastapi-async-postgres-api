# src/api/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from src.core.security import decode_token
from src.repositories.user_Repository import UserRepository
from src.services.auth_service import AuthService
from src.core.database import get_chosen_db
from src.schemas.register import UserOut


security = HTTPBearer()

# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: AsyncSession = Depends(get_chosen_db)
# ) -> UserOut:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     try:
#         token = credentials.credentials
#         payload = decode_token(token)
#         username = payload.get("sub")
#         if not username:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
    

#     service = AuthService(UserRepository(db))
#     return await service.get_current_user(username)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_chosen_db)
) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    service = AuthService(UserRepository(db))
    user_orm = await service.repo.get_by_username(username)   # or keep service.get_current_user if you prefer
    if not user_orm:
        raise credentials_exception

    return UserOut.model_validate(user_orm)   # ← convert here