
from __future__ import annotations  
import uuid
from datetime import datetime
from datetime import datetime  
from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.models.register import User
from sqlalchemy import UUID


class Chat(Base):


    __tablename__ = "chats"



    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),   # ← best: let DB set it
        nullable=False,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    user: Mapped[User] = relationship(back_populates="chats")
    
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Message.created_at.asc()",
    )

    def __repr__(self) -> str:
        return (
            f"<Chat(id={self.id!r}, user_id={self.user_id!r}, "
            f"title={self.title!r}, created_at={self.created_at})>"
        )