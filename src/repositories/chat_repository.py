
# src/repositories/chat_repository.py
from uuid import UUID
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.chat import Chat
from src.repositories.baserepository import BaseRepository


class ChatRepository(BaseRepository[Chat]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Chat)

    async def get_by_id(self, chat_id: UUID) -> Optional[Chat]:
        """Get a single chat by ID (no ownership check here – do it in service)."""
        result = await self.session.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_user(self, chat_id: UUID, user_id: int) -> Optional[Chat]:
        """Get chat only if it belongs to the given user."""
        result = await self.session.execute(
            select(Chat)
            .where(Chat.id == chat_id, Chat.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_chats(self, user_id: int) -> List[Chat]:
        """
        Get all chats belonging to a user, newest first.
        """
        result = await self.session.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc().nulls_last(), Chat.created_at.desc())
        )
        return result.scalars().all()

    async def count_user_chats(self, user_id: int) -> int:
        """Quick count – useful for checking if user has any chats."""
        result = await self.session.execute(
            select(func.count()).select_from(Chat).where(Chat.user_id == user_id)
        )
        return result.scalar() or 0

    async def create(self, data: dict) -> Chat:
        """Create and return the new chat instance."""
        chat = Chat(**data)
        self.session.add(chat)
        await self.session.flush()  # so we get the generated UUID immediately
        return chat