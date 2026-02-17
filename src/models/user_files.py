from __future__ import annotations
from sqlalchemy import String, Text, ForeignKey, BigInteger, func, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
import uuid
from src.core.database import Base

class UserFile(Base):
    __tablename__ = "user_files"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    public_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_files")
