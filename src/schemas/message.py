# # src/schemas/message.py
# from pydantic import BaseModel, ConfigDict
# from datetime import datetime


# # =========================
# # Request Schema
# # =========================

# class MessageCreate(BaseModel):
#     content: str


# # =========================
# # Response Schema
# # =========================

# class MessageOut(BaseModel):
#     id: int
#     role: str              # "user" or "assistant"
#     content: str
#     chat_id: int
#     created_at: datetime

#     model_config = ConfigDict(from_attributes=True)

# src/schemas/message.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# ────────────────────────────────────────────────
# Request Schemas
# ────────────────────────────────────────────────

class MessageCreate(BaseModel):
    """
    Request body for sending a new message (used in POST /chats/messages)
    """
    content: str = Field(
        ...,
        min_length=1,
        max_length=8192,           # reasonable limit for most LLM inputs
        description="The text content of the user's message"
    )
    chat_id: Optional[UUID] = Field(
        None,
        description=(
            "ID of the chat to send the message to. "
            "Omit for auto-creation (if user has no chats) or to force new chat"
        )
    )
    create_new: bool = Field(
        False,
        description="Force creation of a new chat even if user already has existing chats"
    )


# ────────────────────────────────────────────────
# Response Schemas
# ────────────────────────────────────────────────

class MessageOut(BaseModel):
    """
    Full representation of a single message (used in responses and chat history)
    """
    id: UUID = Field(..., description="Unique identifier of the message")
    chat_id: UUID = Field(..., description="ID of the chat this message belongs to")
    
    role: str = Field(
        ...,
        description="Message sender role: 'user' or 'assistant'"
    )
    content: str = Field(..., description="The text content of the message")
    created_at: datetime = Field(..., description="When the message was created")

    # Optional – only if you add these fields to the Message model later
    # updated_at: Optional[datetime] = Field(None, description="Last edit time (if editable)")

    model_config = ConfigDict(
        from_attributes=True,          # Enable ORM mode (SQLAlchemy compatibility)
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str                      # UUIDs serialized as strings in JSON
        }
    )


class MessageListOut(BaseModel):
    """
    Wrapper for returning multiple messages (e.g. full chat history)
    """
    messages: list[MessageOut]
    total: int = Field(..., description="Total number of messages in the chat")
    # Optional pagination info
    limit: Optional[int] = None
    offset: Optional[int] = None


class MessageWithChatInfoOut(MessageOut):
    """
    Extended version – used when returning messages + chat context
    """
    chat_title: Optional[str] = Field(None, description="Title of the containing chat")