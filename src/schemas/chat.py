from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


# =========================
# Request Schema
# =========================

class ChatCreate(BaseModel):
    title: Optional[str] = None


# =========================
# Response Schema
# =========================

class ChatOut(BaseModel):
    id: int
    title: str
    created_at: datetime = Field(alias="timestamp")
    model_config = ConfigDict(from_attributes=True)
