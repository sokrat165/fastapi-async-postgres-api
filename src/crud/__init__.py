# src/crud/__init__.py
from .basestudent import StudentRepository
from .baseitem import ItemRepository

__all__ = ["StudentRepository", "ItemRepository"]
