# src/routers/qanda.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.qanda import QandACreate, QandAUpdate, QandAOut
from src.crud.qanda import QandARepository
from src.core.database import get_chosen_db
from src.core.security import get_current_user

router = APIRouter(
    prefix="/qanda",
    tags=["qanda"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=QandAOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Q&A entry",
    description="Creates a new question & answer entry in the database.",
)
async def create_qanda(
    qanda: QandACreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = QandARepository(db)
    try:
        created = await repo.create(qanda)
        return created
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create Q&A: {str(exc)}",
        ) from exc


@router.get(
    "/{qanda_id}",
    response_model=QandAOut,
    summary="Get one Q&A entry by ID",
)
async def get_qanda(
    qanda_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = QandARepository(db)
    qanda = await repo.get_by_id(qanda_id)

    if qanda is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Q&A not found",
        )

    return qanda


@router.get(
    "/",
    response_model=List[QandAOut],
    summary="List Q&A entries (paginated)",
)
async def list_qanda(
    skip: int = Query(0, ge=0, description="Records to skip (offset)"),
    limit: int = Query(20, ge=1, le=200, description="Number of records to return"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = QandARepository(db)
    return await repo.get_all(skip=skip, limit=limit)


@router.put(
    "/{qanda_id}",
    response_model=QandAOut,
    summary="Update Q&A entry (partial update)",
)
async def update_qanda(
    qanda_id: int,
    qanda_update: QandAUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = QandARepository(db)
    updated = await repo.update(qanda_id, qanda_update)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Q&A not found",
        )

    return updated


@router.delete(
    "/{qanda_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Q&A entry by ID",
)
async def delete_qanda(
    qanda_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = QandARepository(db)
    deleted = await repo.delete(qanda_id)

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Q&A not found",
        )

    return None  # 204 No Content