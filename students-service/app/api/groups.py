from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app import schemas, crud
from app.database import get_db
from typing import List

router = APIRouter()

@router.post("", response_model=schemas.GroupRead)
async def create_group_in_students(group: schemas.GroupCreate, db: AsyncSession = Depends(get_db)):
  return await crud.create_group(db, group)

@router.get("/{group_id}/students", response_model=List[schemas.StudentResponse])
async def get_group_students(group_id: int, db: AsyncSession = Depends(get_db)):
  students = await crud.get_students_in_group(db, group_id)
  return students or []

@router.delete("/students/{telegram_id}/groups/{group_id}")
async def leave_group(telegram_id: int, group_id: int, db: AsyncSession = Depends(get_db)):
    # 1. ищем студента по telegram_id
    student = await crud.get_student_by_telegram_id(db, telegram_id)
    if not student:
      raise HTTPException(status_code=404, detail="Student not found")

    # 2. удаляем по UUID
    deleted = await crud.remove_student_from_group(db, student.id, group_id)
    if not deleted:
      raise HTTPException(status_code=404, detail="Student not found in group")

    # 3. возвращаем и UUID, и telegram_id
    return {
      "message": "Student removed from group",
      "student_id": str(student.id),
      "telegram_id": student.telegram_id,
    }
