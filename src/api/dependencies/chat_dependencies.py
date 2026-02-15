# #src/api/dependencies/chat_dependencies.py
# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncSession

# from src.core.database import get_chosen_db

# from src.repositories.chat_repository import ChatRepository
# from src.repositories.Message_Repository import MessageRepository
# from src.services.chat_service import ChatService


# def get_chat_service(
#     session: AsyncSession = Depends(get_chosen_db),
# ) -> ChatService:

#     chat_repo = ChatRepository(session)
#     message_repo = MessageRepository(session)

#     return ChatService(
#         chat_repo=chat_repo,
#         message_repo=message_repo,
#     )

# src/api/dependencies/chat_dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_chosen_db
from src.repositories.chat_repository import ChatRepository
from src.repositories.Message_Repository import MessageRepository
from src.services.chat_service import ChatService
from src.LLM_Client.cohere_client import get_co_client   # ← important import

def get_chat_service(
    session: AsyncSession = Depends(get_chosen_db),
    co_client = Depends(get_co_client),                   # ← this line was missing
) -> ChatService:
    chat_repo = ChatRepository(session)
    message_repo = MessageRepository(session)
    
    return ChatService(
        chat_repo=chat_repo,
        message_repo=message_repo,
        co_client=co_client                               # ← pass it here
    )