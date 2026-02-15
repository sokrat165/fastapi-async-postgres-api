# from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from datetime import datetime
# from src.core.database import Base
# from src.models.register import User
# from src.models.Messages import Message


# class Chat(Base):
#     __tablename__ = "chats"

#     id: Mapped[int] = mapped_column(
#         Integer,
#         primary_key=True,
#         autoincrement=True,
#     )
#     user_id: Mapped[int] = mapped_column(
#         Integer,
#         ForeignKey("users.id", ondelete="CASCADE"),
#         nullable=False,
#     )
#     title: Mapped[str] = mapped_column(String(100), nullable=True)  # ← هنا

#     timestamp: Mapped[datetime] = mapped_column(
#         DateTime,
#         nullable=False,
#         default=datetime.utcnow,
#     )

#     user: Mapped["User"] = relationship(back_populates="chats")
#     messages: Mapped[list["Message"]] = relationship(
#         back_populates="chat",
#         cascade="all, delete"
#     )
#     def __repr__(self) -> str:
#         return f"<Chat(id={self.id}, user_id={self.user_id}, message={self.message!r}, timestamp={self.timestamp})>"

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.core.database import Base
from src.models.register import User

class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    user: Mapped["User"] = relationship(back_populates="chats")

    # Use string reference — no need to import Message
    messages: Mapped[list["Message"]] = relationship(
        "Message",                     # ← string = class name
        back_populates="chat",
        cascade="all, delete-orphan",  # recommended over "all, delete"
        passive_deletes=True           # helps with ON DELETE CASCADE
    )

    def __repr__(self) -> str:
        return (
        f"<Chat(id={self.id}, "
        f"user_id={self.user_id}, "
        f"title={self.title!r}, "
        f"timestamp={self.timestamp})>"
    )