# src/repositories/chat_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.chat import Chat
from src.repositories.baserepository import BaseRepository

class ChatRepository(BaseRepository[Chat]):

    def __init__(self, session: AsyncSession):
        super().__init__(session, Chat)

    async def get_user_chats(self, user_id: int) -> list[Chat]:
        result = await self.session.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.id.desc())
        )
        return result.scalars().all()
