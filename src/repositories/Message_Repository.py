
# # src/repositories/Message_Repository.py
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from src.models.chat import Chat
# from src.repositories.baserepository import BaseRepository


# class MessageRepository(BaseRepository[Chat]):

#     def __init__(self, session: AsyncSession):
#         super().__init__(session, Chat)

#     async def get_user_chats(self, user_id: int) -> list[Chat]:
#         result = await self.session.execute(
#             select(Chat)
#             .where(Chat.user_id == user_id)
#             .order_by(Chat.id.desc())
#         )
#         return result.scalars().all()


# src/repositories/Message_Repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from src.models.Messages import Message   # ← make sure this import is correct
from src.repositories.baserepository import BaseRepository

class MessageRepository(BaseRepository[Message]):   # ← [Message], not [Chat]
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)          # ← Message, not Chat

    # You can add message-specific methods here if needed, e.g.:
    async def get_messages_for_chat(self, chat_id: int):
        result = await self.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at)
        )
        return result.scalars().all()
    
    # src/repositories/Message_Repository.py
async def get_by_chat_id(self, chat_id: int) -> list[Message]:
    result = await self.session.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()