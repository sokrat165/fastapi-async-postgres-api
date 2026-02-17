from fastapi import HTTPException, status

from src.repositories.user_Repository import UserRepository
from src.schemas.register import UserCreate, UserUpdate
from src.core.config import settings
from src.models.register import User

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register_user(self, user_data: UserCreate) -> User:
        existing = await self.repo.get_by_email_or_username(user_data.email, user_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with given email or username already exists"
            )

        password_hash = settings.pwd_context.hash(user_data.password)
        payload = user_data.model_dump()
        payload.pop("password", None)
        payload["password_hash"] = password_hash

        return await self.repo.create(payload)

    async def update_user(self, username: str, user_update: UserUpdate) -> User:
        values = user_update.model_dump(exclude_unset=True)
        if "password" in values:
            values["password_hash"] = settings.pwd_context.hash(values.pop("password"))
        updated = await self.repo.update_by_username(username, values)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return updated
