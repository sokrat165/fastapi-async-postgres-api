# src/models/student.py
from __future__ import annotations 
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from src.core.database import Base

if TYPE_CHECKING:
    from src.models.item import Item


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True, 
    )
    name: Mapped[str] = mapped_column(
        String(100),        
        nullable=False,
        index=False,          
    )
    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    grade: Mapped[str] = mapped_column(
        String(20),           
        nullable=False,
    )
    items: Mapped[list["Item"]] = relationship("Item", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name={self.name!r}, age={self.age}, grade={self.grade!r})>"