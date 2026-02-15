
# src/api/items.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.schemas.item import ItemCreate, ItemUpdate, ItemOut
from src.repositories.baseitem import ItemRepository
from src.core.database import get_chosen_db
from src.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/items", tags=["items"])

@router.post(
    "/",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new item",
    description="Creates a new item. Use ?db=supabase to store in Supabase.",
)
async def create_item(
    item: ItemCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = ItemRepository(db)

    try:
        created = await repo.create(item)
        return created
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create item: {str(exc)}",
        ) from exc


@router.get(
    "/{item_id}",
    response_model=ItemOut,
    summary="Get one item by ID",
)
async def get_item(
    item_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = ItemRepository(db)
    item = await repo.get_by_id(item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return item


@router.get(
    "/",
    response_model=List[ItemOut],
    summary="Get list of items with pagination",
)
async def get_all_items(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(50, ge=1, le=500, description="Max number of records to return"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = ItemRepository(db)
    items = await repo.get_all(skip=skip, limit=limit)
    return items


@router.put(
    "/{item_id}",
    response_model=ItemOut,
    summary="Update existing item (partial update)",
)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),

):
    repo = ItemRepository(db)
    updated = await repo.update(item_id, item_data)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return updated


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an item by ID",
)
async def delete_item(
    item_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = ItemRepository(db)
    deleted = await repo.delete(item_id)

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return None  # 204 No Content