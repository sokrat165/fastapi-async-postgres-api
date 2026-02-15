# # src/models/Messages.py
# from sqlalchemy import String, Integer, Float, DateTime, ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from datetime import datetime
# from src.models.chat import Chat
# from src.core.database import Base
# from src.models.register import User


# class Message(Base):
#     __tablename__ = "messages"

#     id: Mapped[int] = mapped_column(
#         Integer,
#         primary_key=True,
#         autoincrement=True,
#     )
#     chat_id: Mapped[int] = mapped_column(
#         Integer,
#         ForeignKey("chats.id", ondelete="CASCADE"),
#         nullable=False,
#     )
#     sender: Mapped[str] = mapped_column(
#         String(50),
#         nullable=False,
#     )
#     content: Mapped[str] = mapped_column(
#         String(1000),
#         nullable=False,
#     )
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime,
#         nullable=False,
#         default=datetime.utcnow,
#     )


#     chat: Mapped["Chat"] = relationship(back_populates="messages")

#     def __repr__(self) -> str:
#         return f"<Message(id={self.id}, chat_id={self.chat_id}, sender={self.sender!r}, timestamp={self.timestamp})>"

# src/models/Messages.py
# src/models/Messages.py
# 

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
import datetime

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),   # better than default=datetime.utcnow
    )

    # Use string reference — no need to import Chat
    chat: Mapped["Chat"] = relationship(
        "Chat",                        # ← string = class name
        back_populates="messages"
    )

    def __repr__(self) -> str:
    # Check if relationship was already loaded (without triggering query)
     loaded = "messages" in self.__dict__
     count = len(self.__dict__["messages"]) if loaded else "lazy"
     
     return (
         f"<Chat(id={self.id}, "
         f"user_id={self.user_id}, "
         f"title={self.title!r}, "
         f"messages={count}, "
         f"timestamp={self.timestamp})>"
     )