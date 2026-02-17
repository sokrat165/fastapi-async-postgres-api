
# # src/repositories/Message_Repository.py
# from sqlalchemy.ext.asyncio import AsyncSession
# from src.models.Messages import Message   # ← make sure this import is correct
# from src.repositories.baserepository import BaseRepository

# class MessageRepository(BaseRepository[Message]):   # ← [Message], not [Chat]
#     def __init__(self, session: AsyncSession):
#         super().__init__(session, Message)          # ← Message, not Chat

#     # You can add message-specific methods here if needed, e.g.:
#     async def get_messages_for_chat(self, chat_id: int):
#         result = await self.session.execute(
#             select(Message)
#             .where(Message.chat_id == chat_id)
#             .order_by(Message.created_at)
#         )
#         return result.scalars().all()
    
#     # src/repositories/Message_Repository.py
# async def get_by_chat_id(self, chat_id: int) -> list[Message]:
#     result = await self.session.execute(
#         select(Message)
#         .where(Message.chat_id == chat_id)
#         .order_by(Message.created_at.asc())
#     )
#     return result.scalars().all()
# ------------------------------------------------------


# src/repositories/message_repository.py
from uuid import UUID
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.Messages import Message
from src.repositories.baserepository import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def create(self, data: dict) -> Message:
        """Create and return the new message."""
        message = Message(**data)
        self.session.add(message)
        await self.session.flush()  # get generated UUID
        return message

    async def get_by_id(self, message_id: UUID) -> Optional[Message]:
        result = await self.session.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_messages_for_chat(
        self,
        chat_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Message]:
        """
        Get messages for a specific chat, oldest first.
        Supports basic pagination.
        """
        result = await self.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_last_message(self, chat_id: UUID) -> Optional[Message]:
        """Get the most recent message in a chat (useful for previews)."""
        result = await self.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def count_messages_in_chat(self, chat_id: UUID) -> int:
        """Count total messages in a chat."""
        result = await self.session.execute(
            select(func.count()).select_from(Message).where(Message.chat_id == chat_id)
        )
        return result.scalar() or 0