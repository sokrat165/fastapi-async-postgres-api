# # src/api/dependencies/chat_dependencies.py
# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncSession

# from src.core.database import get_chosen_db
# from src.repositories.chat_repository import ChatRepository
# from src.repositories.Message_Repository import MessageRepository
# from src.services.chat_service import ChatService
# from src.LLM_Clients.factory import get_llm_client


# def get_chat_service(
#     session: AsyncSession = Depends(get_chosen_db),
# ) -> ChatService:
#     llm_client = get_llm_client(provider="cohere")  # can become dynamic later
#     return ChatService(
#         chat_repo=ChatRepository(session),
#         message_repo=MessageRepository(session),
#         llm_client=llm_client,
#     )


# ---------------------------------------------------

# src/api/dependencies/chat_dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_chosen_db
from src.repositories.chat_repository import ChatRepository
from src.repositories.Message_Repository import MessageRepository  # ← fixed name
from src.services.chat_service import ChatService
from src.LLM_Clients.factory import get_llm_client


def get_chat_service(
    session: AsyncSession = Depends(get_chosen_db),
) -> ChatService:
    """
    Dependency that provides a fully wired ChatService instance.
    LLM provider can be made dynamic later (e.g. from user settings or query param).
    """
    llm_client = get_llm_client(provider="cohere")  # ← can be dynamic in future
    return ChatService(
        chat_repo=ChatRepository(session),
        message_repo=MessageRepository(session),
        llm_client=llm_client,
    )