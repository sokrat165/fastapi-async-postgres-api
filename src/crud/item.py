from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.item import Item
from src.schemas.item import ItemCreate, ItemUpdate


class ItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, item_data: ItemCreate) -> Item:
        """Create a new item"""
        item = Item(**item_data.model_dump())
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """Get item by ID"""
        stmt = select(Item).where(Item.id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 50) -> list[Item]:
        """Get all items with pagination"""
        stmt = select(Item).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, item_id: int, item_data: ItemUpdate) -> Optional[Item]:
        """Update an item (partial update)"""
        item = await self.get_by_id(item_id)
        if item is None:
            return None

        # Only update fields that were explicitly set
        update_dict = item_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(item, key, value)

        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def delete(self, item_id: int) -> Optional[Item]:
        """Delete an item by ID"""
        item = await self.get_by_id(item_id)
        if item is None:
            return None

        await self.session.delete(item)
        await self.session.commit()
        return item
