

# src/api/chat.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from src.schemas.chat import ChatCreate, ChatOut
from src.schemas.message import MessageCreate, MessageOut
from src.api.dependencies.chat_dependencies import get_chat_service
from src.services.chat_service import ChatService
from src.api.dependencies.auth import get_current_user
from src.models.register import User

router = APIRouter(prefix="/chats", tags=["chats"])

# -------------------------
# Create new chat
# -------------------------
@router.post(
    "/",
    response_model=ChatOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat",
)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Create a new chat for the current user.
    The user_id is taken from JWT, not from body.
    """
    return await service.create_chat(
        user_id=current_user.id,
        title=chat_data.title
    )

# -------------------------
# Get all chats of user
# -------------------------
@router.get(
    "/",
    response_model=List[ChatOut],
    summary="Get list of chats of the current user",
)
async def get_user_chats(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Returns paginated list of chats for the current user.
    """
    chats = await service.get_user_chats(current_user.id)
    return chats[skip: skip + limit]

# -------------------------
# Send message → AI answers with full context
# -------------------------
@router.post("/{chat_id}/messages", response_model=List[MessageOut])
async def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Send a message to a chat → AI responds using full conversation history.
    Returns both user message and AI response.
    """
    if not current_user or not current_user.id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    messages = await service.send_message(
        user_id=current_user.id,
        chat_id=chat_id,
        content=message_data.content
    )

    return messages  # list of both user + assistant messages

# -------------------------
# Get all messages of a chat
# -------------------------
@router.get(
    "/{chat_id}/messages",
    response_model=List[MessageOut],
    summary="Get all messages of a chat",
)
async def get_chat_messages(
    chat_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Returns all messages of a chat belonging to current user, with pagination.
    """
    messages = await service.get_chat_messages(
        user_id=current_user.id,
        chat_id=chat_id
    )
    return messages[skip: skip + limit]

# -------------------------
# Delete a chat
# -------------------------
@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat and all its messages",
)
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Deletes the chat if it belongs to the current user.
    """
    await service.delete_chat(user_id=current_user.id, chat_id=chat_id)
    return None

# -------------------------
# Update chat metadata (title)
# -------------------------
@router.patch(
    "/{chat_id}",
    response_model=ChatOut,
    summary="Update chat title",
)
async def update_chat(
    chat_id: int,
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    """
    Updates chat title. Ownership verified.
    """
    return await service.update_chat(
        user_id=current_user.id,
        chat_id=chat_id,
        title=chat_data.title
    )