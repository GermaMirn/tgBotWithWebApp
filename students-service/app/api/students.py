from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas
from typing import List

router = APIRouter()

@router.post("/", response_model=schemas.StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
  student: schemas.StudentCreate,
  db: AsyncSession = Depends(get_db)
):
  """Создать нового студента"""
  # Проверяем, существует ли уже студент с таким telegram_id
  existing_student = await crud.get_student_by_telegram_id(db, student.telegram_id)
  if existing_student:
    raise HTTPException(
      status_code=400,
      detail="Student with this telegram_id already exists"
    )

  return await crud.create_student(db=db, student=student)

@router.get("/", response_model=List[schemas.StudentResponse])
async def get_students(
  skip: int = 0,
  limit: int = 100,
  db: AsyncSession = Depends(get_db)
):
  """Получить список всех студентов"""
  students = await crud.get_all_students(db, skip=skip, limit=limit)
  return students

@router.get("/{student_id}", response_model=schemas.StudentResponse)
async def get_student(
  student_id: str,
  db: AsyncSession = Depends(get_db)
):
  """Получить студента по ID"""
  student = await crud.get_student_by_id(db, student_id=student_id)
  if not student:
    raise HTTPException(status_code=404, detail="Student not found")
  return student

@router.get("/by-telegram/{telegram_id}", response_model=schemas.StudentResponse)
async def get_student_by_telegram(
  telegram_id: int,
  db: AsyncSession = Depends(get_db)
):
  """Получить студента по telegram_id"""
  student = await crud.get_student_by_telegram_id(db, telegram_id=telegram_id)
  if not student:
    raise HTTPException(status_code=404, detail="Student not found")
  return student

@router.get("/me/{telegram_id}", response_model=schemas.StudentResponse)
async def get_current_student(
  telegram_id: int,
  db: AsyncSession = Depends(get_db)
):
  """Получить данные текущего студента (alias для by-telegram)"""
  student = await crud.get_student_by_telegram_id(db, telegram_id=telegram_id)
  if not student:
    raise HTTPException(status_code=404, detail="Student not found")
  return student

@router.put("/{student_id}", response_model=schemas.StudentResponse)
async def update_student(
  student_id: str,
  student_update: schemas.StudentUpdate,
  db: AsyncSession = Depends(get_db)
):
  """Обновить данные студента"""
  db_student = await crud.get_student_by_id(db, student_id=student_id)
  if not db_student:
    raise HTTPException(status_code=404, detail="Student not found")

  return await crud.update_student(db=db, db_student=db_student, student_update=student_update)

@router.put("/by-telegram/{telegram_id}", response_model=schemas.StudentResponse)
async def update_student_by_telegram(
  telegram_id: int,
  student_update: schemas.StudentUpdate,
  db: AsyncSession = Depends(get_db)
):
  """Обновить данные студента по telegram_id"""
  db_student = await crud.get_student_by_telegram_id(db, telegram_id=telegram_id)
  if not db_student:
    raise HTTPException(status_code=404, detail="Student not found")

  return await crud.update_student(db=db, db_student=db_student, student_update=student_update)

@router.put("/me/{telegram_id}", response_model=schemas.StudentResponse)
async def update_current_student(
  telegram_id: int,
  student_update: schemas.StudentUpdate,
  db: AsyncSession = Depends(get_db)
):
  """Обновить данные текущего студента (alias для by-telegram)"""
  db_student = await crud.get_student_by_telegram_id(db, telegram_id=telegram_id)
  if not db_student:
    raise HTTPException(status_code=404, detail="Student not found")

  return await crud.update_student(db=db, db_student=db_student, student_update=student_update)

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
  student_id: str,
  db: AsyncSession = Depends(get_db)
):
  """Удалить студента"""
  success = await crud.delete_student(db, student_id=student_id)
  if not success:
    raise HTTPException(status_code=404, detail="Student not found")
  return None

@router.delete("/by-telegram/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student_by_telegram(
  telegram_id: int,
  db: AsyncSession = Depends(get_db)
):
  """Удалить студента по telegram_id"""
  success = await crud.delete_student_by_telegram_id(db, telegram_id=telegram_id)
  if not success:
    raise HTTPException(status_code=404, detail="Student not found")
  return None

@router.post("/assign-group", status_code=201)
async def assign_group_to_student(
  data: dict,
  db: AsyncSession = Depends(get_db)
):
  telegram_id = data.get("telegram_id")
  group_id = data.get("group_id")

  if not telegram_id or not group_id:
    raise HTTPException(status_code=400, detail="telegram_id and group_id are required")

  student = await crud.get_student_by_telegram_id(db, telegram_id)
  if not student:
    raise HTTPException(status_code=404, detail="Student not found")

  # Здесь создаем связь student ↔ group (через table group_students)
  await crud.add_student_to_group(db, student.id, group_id)
  return {"message": "Student assigned to group"}


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
  """Проверка здоровья сервиса"""
  return {"status": "healthy", "service": "students-service"}
