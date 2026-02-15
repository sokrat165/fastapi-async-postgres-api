from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.register import User

from src.repositories.baserepository import BaseRepository


class UserRepository(BaseRepository[User]):


    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, email: str, username: str) -> Optional[User]:
        stmt = select(User).where(
            or_(User.email == email, User.username == username)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_by_username(self, username: str, update_values: dict) -> Optional[User]:
        """
        Update user by username. Only updates fields in `update_values`.
        """
        user = await self.get_by_username(username)
        if not user:
            return None

        for key, value in update_values.items():
            setattr(user, key, value)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
