# # src/services/auth_service.py
# from fastapi import HTTPException, status
# from src.repositories.user_Repository import UserRepository
# from src.core.security import verify_password

# class AuthService:

#     def __init__(self, repo: UserRepository):
#         self.repo = repo

#     async def get_current_user(self, username: str):
#         user = await self.repo.get_by_username(username)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="User not found"
#             )
#         return user

#     async def authenticate_user(self, username: str, password: str):
#         user = await self.repo.get_by_username(username)
#         if not user:
#             return None
#         if not verify_password(password, user.password_hash):
#             return None
#         return user
# src/services/auth_service.py
from fastapi import HTTPException, status
from src.repositories.user_Repository import UserRepository
from src.core.security import verify_password
from src.schemas.register import UserOut   # ← import here

class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_current_user(self, username: str) -> UserOut:
        user = await self.repo.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return UserOut.model_validate(user)   # ← explicit ORM → Pydantic conversion

    async def authenticate_user(self, username: str, password: str) -> UserOut | None:
        user = await self.repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return UserOut.model_validate(user)   # ← same here for consistency