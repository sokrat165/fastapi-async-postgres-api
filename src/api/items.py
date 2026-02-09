from fastapi import APIRouter, HTTPException, status, Depends

from src.core.database import async_session_factory
from src.schemas.item import ItemCreate, ItemUpdate, ItemOut
from src.crud.baseitem import ItemRepository


router = APIRouter(prefix="/items", tags=["items"])


# 1. CREATE (POST)
@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """
    Create a new item
    """
    async with async_session_factory() as session:
        repo = ItemRepository(session)
        created = await repo.create(item)
        return created


# 2. READ ONE (GET by id)
@router.get("/{item_id}", response_model=ItemOut)
async def get_item(item_id: int):
    """
    Get one item by ID
    """
    async with async_session_factory() as session:
        repo = ItemRepository(session)
        item = await repo.get_by_id(item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        return item


# 3. READ ALL (GET list)
@router.get("/", response_model=list[ItemOut])
async def get_all_items(skip: int = 0, limit: int = 50):
    """
    Get list of items with pagination
    """
    async with async_session_factory() as session:
        repo = ItemRepository(session)
        items = await repo.get_all(skip=skip, limit=limit)
        return items


# 4. UPDATE (PUT - partial update)
@router.put("/{item_id}", response_model=ItemOut)
async def update_item(item_id: int, item_data: ItemUpdate):
    """
    Update existing item (partial update - only sent fields are updated)
    """
    async with async_session_factory() as session:
        repo = ItemRepository(session)

        # Check if at least one field is provided
        if not item_data.model_dump(exclude_unset=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for update"
            )

        updated = await repo.update(item_id, item_data)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
        return updated


# 5. DELETE
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """
    Delete an item by ID
    """
    async with async_session_factory() as session:
        repo = ItemRepository(session)
        deleted = await repo.delete(item_id)
        if deleted is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found"
            )
