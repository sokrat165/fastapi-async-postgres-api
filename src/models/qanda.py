#src/models/qanda.py
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from src.core.database import Base
from src.models.register import User

class QandA(Base):
    __tablename__ = "q_and_a"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    question: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    answer: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    timestamp: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),   # ← add timezone=True        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    user: Mapped[User] = relationship("User", backref="q_and_a_entries")

    def __repr__(self) -> str:
        return f"<QandA(id={self.id}, question={self.question!r}, user_id={self.user_id})>"