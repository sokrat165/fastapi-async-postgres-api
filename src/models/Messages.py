# src/models/Messages.py
from __future__ import annotations
from litellm import Chat
from datetime import datetime  
from sqlalchemy import String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.chat import Chat
from src.core.database import Base
import datetime
import uuid
from sqlalchemy import UUID



class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime ] = mapped_column(  # ← now correct (datetime is the class)
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    chat: Mapped["Chat"] = relationship(
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id!r}, role={self.role}, chat_id={self.chat_id!r})>"