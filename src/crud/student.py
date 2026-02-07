from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.student import Student
from src.schemas.student import StudentCreate, StudentUpdate


async def create_student(session: AsyncSession, student_data: StudentCreate) -> Student:
    student = Student(**student_data.model_dump())
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return student


async def get_student(session: AsyncSession, student_id: int) -> Student | None:
    result = await session.execute(select(Student).where(Student.id == student_id))
    return result.scalar_one_or_none()


async def get_all_students(session: AsyncSession, skip: int = 0, limit: int = 50) -> list[Student]:
    result = await session.execute(
        select(Student).offset(skip).limit(limit).order_by(Student.id)
    )
    return result.scalars().all()


async def update_student(
    session: AsyncSession, student_id: int, update_data: StudentUpdate
) -> Student | None:
    stmt = (
        update(Student)
        .where(Student.id == student_id)
        .values(**update_data.model_dump(exclude_unset=True))
        .returning(Student)
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none()


async def delete_student(session: AsyncSession, student_id: int) -> Student | None:
    stmt = delete(Student).where(Student.id == student_id).returning(Student)
    result = await session.execute(stmt)
    await session.commit()
    return result.scalar_one_or_none()