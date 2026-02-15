

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession   # ← ADD THIS LINE
from typing import List
from src.schemas.student import StudentCreate, StudentUpdate, StudentOut
from src.repositories import StudentRepository
from src.api.dependencies.auth import get_current_user
from fastapi import Depends, HTTPException, status
from src.core.database import get_chosen_db

router = APIRouter(prefix="/students", tags=["students"])


@router.post(
    "/",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Creates a new student. Use ?db=supabase to store in Supabase.",
)
async def create_student(
    student: StudentCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = StudentRepository(db)

    try:
        created = await repo.create(student)
        return created
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create student: {str(exc)}",
        ) from exc


@router.get(
    "/{student_id}",
    response_model=StudentOut,
    summary="Get one student by ID",
)
async def get_student(
    student_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = StudentRepository(db)
    student = await repo.get_by_id(student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return student


@router.get(
    "/",
    response_model=List[StudentOut],
    summary="Get list of students with pagination",
)
async def get_all_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = StudentRepository(db)
    students = await repo.get_all(skip=skip, limit=limit)
    return students


@router.put(
    "/{student_id}",
    response_model=StudentOut,
    summary="Update existing student (partial update)",
)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = StudentRepository(db)
    updated = await repo.update(student_id, student_data)

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return updated


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student by ID",
)
async def delete_student(
    student_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_chosen_db),
):
    repo = StudentRepository(db)
    deleted = await repo.delete(student_id)

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )