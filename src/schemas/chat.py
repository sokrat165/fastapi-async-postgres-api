# from pydantic import BaseModel, ConfigDict, Field
# from typing import Optional
# from datetime import datetime


# # =========================
# # Request Schema
# # =========================

# class ChatCreate(BaseModel):
#     title: Optional[str] = None


# # =========================
# # Response Schema
# # =========================

# class ChatOut(BaseModel):
#     id: int
#     title: str
#     created_at: datetime = Field(alias="timestamp")
#     model_config = ConfigDict(from_attributes=True)

# src/schemas/chat.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# ────────────────────────────────────────────────
# Request Schemas
# ────────────────────────────────────────────────

class ChatCreate(BaseModel):
    """
    Used when explicitly creating a new chat (rarely needed).
    Most creation happens automatically via send_message.
    """
    title: Optional[str] = Field(
        None,
        description="Optional custom title. If not provided, defaults to 'New Chat'",
        max_length=120
    )


class SendMessageRequest(BaseModel):
    """
    Main request body for POST /chats/messages
    """
    content: str = Field(..., min_length=1, description="The user's message content")
    chat_id: Optional[UUID] = Field(
        None,
        description="ID of existing chat to continue. Omit for auto-create (first chat) or new chat"
    )
    create_new: bool = Field(
        False,
        description="Force creation of a new chat even if user already has chats"
    )


class UpdateChatTitle(BaseModel):
    """
    For PATCH /chats/{chat_id}
    """
    title: str = Field(..., min_length=1, max_length=120, description="New chat title")


# ────────────────────────────────────────────────
# Response Schemas
# ────────────────────────────────────────────────

class ChatOut(BaseModel):
    """
    Full chat representation for list / detail responses
    """
    id: UUID = Field(..., description="Unique chat identifier")
    user_id: UUID = Field(..., description="ID of the owning user")  # ← changed from int to UUID
    title: Optional[str] = Field(None, description="Chat title (auto-generated or custom)")
    created_at: datetime = Field(..., description="When the chat was created")
    updated_at: Optional[datetime] = Field(
        None,
        description="Last time the chat was updated (e.g. new message)"
    )

    # Optional useful fields (very common in chat apps)
    message_count: Optional[int] = Field(
        None,
        description="Total number of messages in this chat"
    )
    last_message_preview: Optional[str] = Field(
        None,
        description="Short preview of the most recent message"
    )

    model_config = ConfigDict(
        from_attributes=True,          # ORM mode (SQLAlchemy compatibility)
        populate_by_name=True,         # allow snake_case → camelCase if needed later
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
    )


class ChatListOut(BaseModel):
    """
    Used for GET /chats (list of user's chats)
    Slightly lighter than full detail
    """
    id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    message_count: Optional[int]
    last_message_preview: Optional[str]
    message_count: Optional[int] = None
    last_message_preview: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            UUID: str,                  # Serialize UUIDs as strings
            datetime: lambda v: v.isoformat()
        },
        exclude_none=True
    )
    


# class MessageOut(BaseModel):
#     """
#     Single message response (used in chat history)
#     """
#     id: UUID
#     chat_id: UUID
#     role: str  # "user" or "assistant"
#     content: str
#     created_at: datetime

#     model_config = ConfigDict(from_attributes=True)