# # src/services/chat_service.py

from fastapi import HTTPException
from src.models.chat import Chat
from src.models.Messages import Message
from src.repositories.chat_repository import ChatRepository
from src.repositories.Message_Repository import MessageRepository
from typing import List
# src/services/chat_service.py
from sqlalchemy import select

class ChatService:
    def __init__(
        self,
        chat_repo: ChatRepository,
        message_repo: MessageRepository,
        co_client,   # ← Cohere AsyncClientV2
    ):
        self.chat_repo = chat_repo
        self.message_repo = message_repo
        self.co_client = co_client

    async def create_chat(self, user_id: int, title: str | None = None) -> Chat:
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID required")

        chat_data = {
            "user_id": user_id,
            "title": title or "New Chat",
        }

        return await self.chat_repo.create(chat_data)
    async def send_message(self, user_id: int, chat_id: int, content: str) -> list[Message]:
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat or chat.user_id != user_id:
            raise HTTPException(404, "Chat not found")

        # Save user message
        user_msg = await self.message_repo.create({
            "chat_id": chat_id,
            "role": "user",
            "content": content
        })

        # Load full history
        history_result = await self.message_repo.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
        )
        history = history_result.scalars().all()

        # Prepare correct Cohere format
        cohere_messages = [
            {"role": msg.role, "content": msg.content}  # ← "content", not "message"
            for msg in history
        ] + [
            {"role": "user", "content": content}
        ]

        # Call Cohere
        try:
            response = await self.co_client.chat(
                model="command-r-plus-08-2024",
                messages=cohere_messages,
                temperature=0.7,
                max_tokens=1024,
            )
            answer = response.message.content[0].text.strip()
        except Exception as e:
            raise HTTPException(500, f"Cohere failed: {str(e)}")

        # Save assistant response
        assistant_msg = await self.message_repo.create({
            "chat_id": chat_id,
            "role": "assistant",
            "content": answer
        })

        return [user_msg, assistant_msg]
    
    # Add this method inside the ChatService class
    async def get_chat_messages(self, user_id: int, chat_id: int) -> list[Message]:
        """
        Fetch all messages for a chat, with ownership check.
        """
        # Verify chat exists and belongs to the user
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat or chat.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found or you do not have access"
            )
    
        # Query messages, ordered by time
        result = await self.message_repo.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())  # oldest first
        )
    
        return result.scalars().all()
    async def get_user_chats(self, user_id: int) -> List[Chat]:
        """
        Return all chats belonging to the user, ordered by ID descending.
        """
        return await self.chat_repo.get_user_chats(user_id)