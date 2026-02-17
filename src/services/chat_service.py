
# # src/services/chat_service.py
# from fastapi import HTTPException, status
# from typing import List

# from sqlalchemy import select, delete, update

# from src.models.chat import Chat
# from src.models.Messages import Message
# from src.repositories.chat_repository import ChatRepository
# from src.repositories.Message_Repository import MessageRepository
# from src.LLM_Clients.factory  import LLMClient
# from src.LLM_Clients.base import LLMMessage


# class ChatService:
#     def __init__(
#         self,
#         chat_repo: ChatRepository,
#         message_repo: MessageRepository,
#         llm_client: LLMClient,
#     ):
#         self.chat_repo = chat_repo
#         self.message_repo = message_repo
#         self.llm_client = llm_client

#     async def create_chat(self, user_id: int, title: str | None = None) -> Chat:
#         if not user_id:
#             raise HTTPException(status_code=401, detail="User ID required")

#         chat_data = {"user_id": user_id, "title": title or "New Chat"}
#         return await self.chat_repo.create(chat_data)

#     async def send_message(self, user_id: int, chat_id: int, content: str) -> list[Message]:
#         chat = await self.chat_repo.get_by_id(chat_id)
#         if not chat or chat.user_id != user_id:
#             raise HTTPException(status_code=404, detail="Chat not found or access denied")

#         # Save user message
#         user_msg = await self.message_repo.create(
#             {"chat_id": chat_id, "role": "user", "content": content}
#         )

#         # Load history (oldest first)
#         history_result = await self.message_repo.session.execute(
#             select(Message)
#             .where(Message.chat_id == chat_id)
#             .order_by(Message.created_at.asc())
#         )
#         history = history_result.scalars().all()

#         messages: List[LLMMessage] = [
#             {"role": m.role, "content": m.content} for m in history
#         ] + [{"role": "user", "content": content}]

#         try:
#             llm_response = await self.llm_client.chat_completion(
#                 messages=messages,
#                 model="command-r-plus-08-2024",  # ← move to DB / user setting later
#                 temperature=0.7,
#                 max_tokens=1024,
#             )
#             answer = llm_response.content
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

#         assistant_msg = await self.message_repo.create(
#             {"chat_id": chat_id, "role": "assistant", "content": answer}
#         )

#         return [user_msg, assistant_msg]

#     async def get_chat_messages(self, user_id: int, chat_id: int) -> list[Message]:
#         chat = await self.chat_repo.get_by_id(chat_id)
#         if not chat or chat.user_id != user_id:
#             raise HTTPException(status_code=404, detail="Chat not found or access denied")

#         result = await self.message_repo.session.execute(
#             select(Message)
#             .where(Message.chat_id == chat_id)
#             .order_by(Message.created_at.asc())
#         )
#         return result.scalars().all()

#     async def get_user_chats(self, user_id: int) -> List[Chat]:
#         return await self.chat_repo.get_user_chats(user_id)

#     async def delete_chat(self, user_id: int, chat_id: int) -> None:
#         chat = await self.chat_repo.get_by_id(chat_id)
#         if not chat or chat.user_id != user_id:
#             raise HTTPException(status_code=404, detail="Chat not found or access denied")

#         # Delete messages first (or use CASCADE in DB)
#         await self.message_repo.session.execute(
#             delete(Message).where(Message.chat_id == chat_id)
#         )
#         await self.message_repo.session.delete(chat)
#         await self.message_repo.session.commit()

#     async def update_chat(self, user_id: int, chat_id: int, title: str) -> Chat:
#         chat = await self.chat_repo.get_by_id(chat_id)
#         if not chat or chat.user_id != user_id:
#             raise HTTPException(status_code=404, detail="Chat not found or access denied")

#         stmt = (
#             update(Chat)
#             .where(Chat.id == chat_id)
#             .values(title=title)
#             .returning(Chat)
#         )
#         result = await self.chat_repo.session.execute(stmt)
#         await self.chat_repo.session.commit()
#         return result.scalar_one()

# src/services/chat_service.py

from uuid import UUID
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import select, delete, update, func

from src.models.chat import Chat
from src.models.Messages import Message
from src.repositories.chat_repository import ChatRepository
from src.repositories.Message_Repository import MessageRepository
from src.LLM_Clients.base import LLMClient, LLMMessage


# class ChatService:
#     def __init__(
#         self,
#         chat_repo: ChatRepository,
#         message_repo: MessageRepository,
#         llm_client: LLMClient,
#     ):
#         self.chat_repo = chat_repo
#         self.message_repo = message_repo
#         self.llm_client = llm_client

#     async def create_chat(self, user_id: int, title: str | None = None) -> Chat:
#         """Explicitly create a new empty chat (rarely used directly)."""
#         if not user_id:
#             raise HTTPException(status_code=401, detail="User ID required")

#         chat_data = {
#             "user_id": user_id,
#             "title": title or "New Chat",
#         }
#         return await self.chat_repo.create(chat_data)

#     async def send_message(
#         self,
#         user_id: int,
#         content: str,
#         chat_id: Optional[UUID] = None,
#         create_new: bool = False,
#     ) -> Tuple[Chat, List[Message]]:
#         """
#         Main message sending endpoint with smart chat handling.

#         Behavior:
#         - chat_id provided → continue that chat (must exist + belong to user)
#         - no chat_id:
#             - if user has ZERO chats → auto-create new chat
#             - if user already has chats → raise error (ask to provide chat_id or set create_new=true)
#         - create_new=True → force creation of a new chat
#         """
#         if not content or not content.strip():
#             raise HTTPException(status_code=400, detail="Message content cannot be empty")

#         # ────────────────────────────────────────────────
#         # 1. Resolve or create chat
#         # ────────────────────────────────────────────────
#         if chat_id and not create_new:
#             chat = await self.chat_repo.get_by_id(chat_id)
#             if not chat or chat.user_id != user_id:
#                 raise HTTPException(
#                     status_code=404,
#                     detail="Chat not found or you do not have access to it"
#                 )
#         else:
#             # Check if user has any existing chats
#             has_existing = await self._user_has_chats(user_id)

#             if not has_existing or create_new:
#                 # Auto-create (first chat ever) or explicit new chat request
#                 chat = await self.chat_repo.create({
#                     "user_id": user_id,
#                     "title": "New Chat"  # temporary – will be updated after first reply
#                 })
#             else:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=(
#                         "You already have existing chats. "
#                         "Please specify chat_id to continue a conversation "
#                         "or set create_new=true to start a new one."
#                     )
#                 )

#         # ────────────────────────────────────────────────
#         # 2. Save user's message
#         # ────────────────────────────────────────────────
#         user_msg = await self.message_repo.create({
#             "chat_id": chat.id,
#             "role": "user",
#             "content": content.strip(),
#         })

#         # ────────────────────────────────────────────────
#         # 3. Build full context and call LLM
#         # ────────────────────────────────────────────────
#         history = await self.message_repo.get_messages_for_chat(chat.id)
#         messages: List[LLMMessage] = [
#             {"role": m.role, "content": m.content} for m in history
#         ] + [{"role": "user", "content": content}]

#         try:
#             llm_response = await self.llm_client.chat_completion(
#                 messages=messages,
#                 model="command-r-plus-08-2024",
#                 temperature=0.7,
#                 max_tokens=1024,
#             )
#             answer = llm_response.content.strip()
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"LLM provider error: {str(e)}")

#         assistant_msg = await self.message_repo.create({
#             "chat_id": chat.id,
#             "role": "assistant",
#             "content": answer,
#         })

#         # ────────────────────────────────────────────────
#         # 4. Auto-generate title from first two messages if still default
#         # ────────────────────────────────────────────────
#         if chat.title in (None, "", "New Chat"):
#             title = await self._generate_title_from_first_two(chat.id)
#             if title:
#                 chat.title = title
#                 await self.chat_repo.session.flush()  # persist title change

#         # Refresh chat to return latest state
#         await self.chat_repo.session.refresh(chat)

#         return chat, [user_msg, assistant_msg]

#     async def _user_has_chats(self, user_id: int) -> bool:
#         """Quick check if user has at least one chat."""
#         result = await self.chat_repo.session.execute(
#             select(func.count()).select_from(Chat).where(Chat.user_id == user_id)
#         )
#         return result.scalar() > 0

#     async def _generate_title_from_first_two(self, chat_id: UUID) -> Optional[str]:
#         """Generate simple title from first user message + first assistant reply."""
#         result = await self.message_repo.session.execute(
#             select(Message)
#             .where(Message.chat_id == chat_id)
#             .order_by(Message.created_at.asc())
#             .limit(2)
#         )
#         msgs = result.scalars().all()

#         if len(msgs) < 1:
#             return None

#         if len(msgs) == 1:
#             # Only user message so far
#             text = msgs[0].content.strip()[:55]
#             return text + "..." if len(text) >= 55 else text or "New chat"

#         # User + Assistant
#         user_part = msgs[0].content.strip()[:35]
#         ai_part = msgs[1].content.strip()[:35]
#         combined = f"{user_part} → {ai_part}"
#         if len(combined) > 70:
#             combined = combined[:67] + "..."

#         return combined or "Conversation started"

#     async def get_chat_messages(self, user_id: int, chat_id: UUID) -> List[Message]:
#         chat = await self.chat_repo.get_by_id(chat_id)
#         if not chat or chat.user_id != user_id:
#             raise HTTPException(status_code=404, detail="Chat not found or access denied")

#         result = await self.message_repo.session.execute(
#             select(Message)
#             .where(Message.chat_id == chat_id)
#             .order_by(Message.created_at.asc())
#         )
#         return result.scalars().all()

#     async def get_user_chats(self, user_id: int) -> List[Chat]:
#         return await self.chat_repo.get_user_chats(user_id)

#     async def delete_chat(self, user_id: int, chat_id: UUID) -> None:
#         chat = await self.chat_repo.get_by_id(chat_id)
#         if not chat or chat.user_id != user_id:
#             raise HTTPException(status_code=404, detail="Chat not found or access denied")

#         # Messages deleted via CASCADE if set in DB, or explicitly here
#         await self.message_repo.session.execute(
#             delete(Message).where(Message.chat_id == chat_id)
#         )
#         await self.message_repo.session.delete(chat)
#         await self.message_repo.session.commit()

#     async def update_chat_title(
#         self, user_id: int, chat_id: UUID, title: str
#     ) -> Chat:
#         """Update chat title (manual rename by user)."""
#         if not title or not title.strip():
#             raise HTTPException(status_code=400, detail="Title cannot be empty")

#         chat = await self.chat_repo.get_by_id(chat_id)
#         if not chat or chat.user_id != user_id:
#             raise HTTPException(status_code=404, detail="Chat not found or access denied")

#         stmt = (
#             update(Chat)
#             .where(Chat.id == chat_id)
#             .values(title=title.strip())
#             .returning(Chat)
#         )
#         result = await self.chat_repo.session.execute(stmt)
#         await self.chat_repo.session.commit()

#         updated_chat = result.scalar_one()
#         if not updated_chat:
#             raise HTTPException(status_code=500, detail="Failed to update chat")

#         return updated_chat# src/services/chat_service.py

from uuid import UUID
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import select, delete, update, func

from src.models.chat import Chat
from src.models.Messages import Message
from src.repositories.chat_repository import ChatRepository
from src.repositories.Message_Repository import MessageRepository
from src.LLM_Clients.base import LLMClient, LLMMessage



class ChatService:
    def __init__(
        self,
        chat_repo: ChatRepository,
        message_repo: MessageRepository,
        llm_client: LLMClient,
    ):
        self.chat_repo = chat_repo
        self.message_repo = message_repo
        self.llm_client = llm_client

    async def create_chat(self, user_id: int, title: str | None = None) -> Chat:
        """Explicitly create a new empty chat (rarely used directly)."""
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID required")

        chat_data = {
            "user_id": user_id,
            "title": title or "New Chat",
        }
        return await self.chat_repo.create(chat_data)

    async def send_message(
        self,
        user_id: int,
        content: str,
        chat_id: Optional[UUID] = None,
        create_new: bool = False,
    ) -> Tuple[Chat, List[Message]]:
        """
        Main message sending endpoint with smart chat handling.

        Behavior:
        - chat_id provided → continue that chat (must exist + belong to user)
        - no chat_id:
            - if user has ZERO chats → auto-create new chat
            - if user already has chats → raise error (ask to provide chat_id or set create_new=true)
        - create_new=True → force creation of a new chat
        """
        if not content or not content.strip():
            raise HTTPException(status_code=400, detail="Message content cannot be empty")

        # ────────────────────────────────────────────────
        # 1. Resolve or create chat
        # ────────────────────────────────────────────────
        if chat_id and not create_new:
            chat = await self.chat_repo.get_by_id(chat_id)
            if not chat or chat.user_id != user_id:
                raise HTTPException(
                    status_code=404,
                    detail="Chat not found or you do not have access to it"
                )
        else:
            # Check if user has any existing chats
            has_existing = await self._user_has_chats(user_id)

            if not has_existing or create_new:
                # Auto-create (first chat ever) or explicit new chat request
                chat = await self.chat_repo.create({
                    "user_id": user_id,
                    "title": "New Chat"  # temporary – will be updated after first reply
                })
            else:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "You already have existing chats. "
                        "Please specify chat_id to continue a conversation "
                        "or set create_new=true to start a new one."
                    )
                )

        # ────────────────────────────────────────────────
        # 2. Save user's message
        # ────────────────────────────────────────────────
        user_msg = await self.message_repo.create({
            "chat_id": chat.id,
            "role": "user",
            "content": content.strip(),
        })

        # ────────────────────────────────────────────────
        # 3. Build full context and call LLM
        # ────────────────────────────────────────────────
        history = await self.message_repo.get_messages_for_chat(chat.id)
        messages: List[LLMMessage] = [
            {"role": m.role, "content": m.content} for m in history
        ] + [{"role": "user", "content": content}]

        try:
            llm_response = await self.llm_client.chat_completion(
                messages=messages,
                model="command-r-plus-08-2024",
                temperature=0.7,
                max_tokens=1024,
            )
            answer = llm_response.content.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM provider error: {str(e)}")

        assistant_msg = await self.message_repo.create({
            "chat_id": chat.id,
            "role": "assistant",
            "content": answer,
        })

        # ────────────────────────────────────────────────
        # 4. Auto-generate title from first two messages if still default
        # ────────────────────────────────────────────────
        if chat.title in (None, "", "New Chat"):
            title = await self._generate_title_from_first_two(chat.id)
            if title:
                chat.title = title
                await self.chat_repo.session.flush()  # persist title change

        # Refresh chat to return latest state
        await self.chat_repo.session.refresh(chat)

        return chat, [user_msg, assistant_msg]

    async def _user_has_chats(self, user_id: int) -> bool:
        """Quick check if user has at least one chat."""
        result = await self.chat_repo.session.execute(
            select(func.count()).select_from(Chat).where(Chat.user_id == user_id)
        )
        return result.scalar() > 0

    async def _generate_title_from_first_two(self, chat_id: UUID) -> Optional[str]:
        """Generate simple title from first user message + first assistant reply."""
        result = await self.message_repo.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .limit(2)
        )
        msgs = result.scalars().all()

        if len(msgs) < 1:
            return None

        if len(msgs) == 1:
            # Only user message so far
            text = msgs[0].content.strip()[:55]
            return text + "..." if len(text) >= 55 else text or "New chat"

        # User + Assistant
        user_part = msgs[0].content.strip()[:35]
        ai_part = msgs[1].content.strip()[:35]
        combined = f"{user_part} → {ai_part}"
        if len(combined) > 70:
            combined = combined[:67] + "..."

        return combined or "Conversation started"

    async def get_chat_messages(self, user_id: int, chat_id: UUID) -> List[Message]:
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat or chat.user_id != user_id:
            raise HTTPException(status_code=404, detail="Chat not found or access denied")

        result = await self.message_repo.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()

    # async def get_user_chats(self, user_id: int) -> List[Chat]:
    #     return await self.chat_repo.get_user_chats(user_id)
    async def get_user_chats(self, user_id: int) -> List[Chat]:
    # Basic query
        stmt = (
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc().nulls_last(), Chat.created_at.desc())
        )
        result = await self.chat_repo.session.execute(stmt)
        chats = result.scalars().all()

        # Optional: enrich with message count & preview (efficient way)
        for chat in chats:
            # Count messages
            count_stmt = select(func.count()).select_from(Message).where(Message.chat_id == chat.id)
            count_result = await self.chat_repo.session.execute(count_stmt)
            chat.message_count = count_result.scalar() or 0

            # Last message preview (first 50 chars)
            if chat.message_count > 0:
                preview_stmt = (
                    select(Message.content)
                    .where(Message.chat_id == chat.id)
                    .order_by(Message.created_at.desc())
                    .limit(1)
                )
                preview_result = await self.chat_repo.session.execute(preview_stmt)
                last_content = preview_result.scalar()
                chat.last_message_preview = (last_content[:50] + "...") if last_content else None
            else:
                chat.last_message_preview = None

        return chats

    async def delete_chat(self, user_id: int, chat_id: UUID) -> None:
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat or chat.user_id != user_id:
            raise HTTPException(status_code=404, detail="Chat not found or access denied")

        # Messages deleted via CASCADE if set in DB, or explicitly here
        await self.message_repo.session.execute(
            delete(Message).where(Message.chat_id == chat_id)
        )
        await self.message_repo.session.delete(chat)
        await self.message_repo.session.commit()

    async def update_chat_title(
        self, user_id: int, chat_id: UUID, title: str
    ) -> Chat:
        """Update chat title (manual rename by user)."""
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")

        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat or chat.user_id != user_id:
            raise HTTPException(status_code=404, detail="Chat not found or access denied")

        stmt = (
            update(Chat)
            .where(Chat.id == chat_id)
            .values(title=title.strip())
            .returning(Chat)
        )
        result = await self.chat_repo.session.execute(stmt)
        await self.chat_repo.session.commit()

        updated_chat = result.scalar_one()
        if not updated_chat:
            raise HTTPException(status_code=500, detail="Failed to update chat")

        return updated_chat