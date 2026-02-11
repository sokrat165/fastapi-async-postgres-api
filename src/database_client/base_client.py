# src/databaseclient/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic

T = TypeVar('T')  # generic for returned data type

class DatabaseClient(ABC, Generic[T]):
    """Abstract interface for all database backends."""

    @abstractmethod
    async def create(self, table: str, data: Dict[str, Any]) -> T:
        """Insert one record and return created item."""
        pass

    @abstractmethod
    async def get_by_id(self, table: str, id_value: Any, id_column: str = "id") -> Optional[T]:
        """Fetch one record by ID."""
        pass

    @abstractmethod
    async def list_all(self, table: str, limit: int = 100, offset: int = 0) -> List[T]:
        """Fetch multiple records (simple pagination)."""
        pass

    @abstractmethod
    async def update(self, table: str, id_value: Any, data: Dict[str, Any], id_column: str = "id") -> Optional[T]:
        """Update one record."""
        pass

    @abstractmethod
    async def delete(self, table: str, id_value: Any, id_column: str = "id") -> bool:
        """Delete one record."""
        pass

    # Add more methods later: filter, count, batch ops, transactions, etc.