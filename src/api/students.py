from fastapi import APIRouter, HTTPException, status, Depends

from src.core.database import async_session_factory
from src.schemas.student import StudentCreate, StudentUpdate, StudentOut
from src.crud import StudentRepository   # ← we use this now
from src.core.security import get_current_user

router = APIRouter(prefix="/students", tags=["students"])


# 1. CREATE (POST)
@router.post("/", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate, current_user = Depends(get_current_user)):
    """
    Create a new student
    """
    async with async_session_factory() as session:
        repo = StudentRepository(session)
        created = await repo.create(student)
        return created


# 2. READ ONE (GET by id)
@router.get("/{student_id}", response_model=StudentOut)
async def get_student(student_id: int, current_user = Depends(get_current_user)):
    """
    Get one student by ID
    """
    async with async_session_factory() as session:
        repo = StudentRepository(session)
        student = await repo.get_by_id(student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
        return student


# 3. READ ALL (GET list)
@router.get("/", response_model=list[StudentOut])
async def get_all_students(skip: int = 0, limit: int = 50, current_user = Depends(get_current_user)):
    """
    Get list of students with pagination
    """
    async with async_session_factory() as session:
        repo = StudentRepository(session)
        students = await repo.get_all(skip=skip, limit=limit)
        return students


# 4. UPDATE (PUT - partial update)
@router.put("/{student_id}", response_model=StudentOut)
async def update_student(student_id: int, student_data: StudentUpdate, current_user = Depends(get_current_user)):
    """
    Update existing student (partial update - only sent fields are updated)
    """
    async with async_session_factory() as session:
        repo = StudentRepository(session)

        # Optional: check if at least one field is provided
        if not student_data.model_dump(exclude_unset=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for update"
            )

        updated = await repo.update(student_id, student_data)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        return updated


# 5. DELETE
@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(student_id: int, current_user = Depends(get_current_user)):
    """
    Delete a student by ID
    """
    async with async_session_factory() as session:
        repo = StudentRepository(session)
        deleted = await repo.delete(student_id)
        if deleted is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
    # No need to return anything → FastAPI will send 204 No Content