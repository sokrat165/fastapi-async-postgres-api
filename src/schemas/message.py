# src/schemas/message.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime


# =========================
# Request Schema
# =========================

class MessageCreate(BaseModel):
    content: str


# =========================
# Response Schema
# =========================

class MessageOut(BaseModel):
    id: int
    role: str              # "user" or "assistant"
    content: str
    chat_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
