import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app import models
from app.schemas import StudentCreate, StudentUpdate
from typing import List, Optional

async def get_student_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[models.Student]:
  """Получить студента по telegram_id"""
  result = await db.execute(
    select(models.Student).where(models.Student.telegram_id == telegram_id)
  )
  return result.scalars().first()

async def get_student_by_id(db: AsyncSession, student_id: str) -> Optional[models.Student]:
  """Получить студента по id"""
  result = await db.execute(
    select(models.Student).where(models.Student.id == student_id)
  )
  return result.scalars().first()

async def create_student(db: AsyncSession, student: StudentCreate) -> models.Student:
  """Создать нового студента"""
  db_student = models.Student(
    telegram_id=student.telegram_id,
    level=student.level,
    preferred_languages=student.preferred_languages,
    study_goals=student.study_goals
  )
  db.add(db_student)
  await db.commit()
  await db.refresh(db_student)
  return db_student

async def update_student(db: AsyncSession, db_student: models.Student, student_update: StudentUpdate) -> models.Student:
  """Обновить данные студента"""
  update_data = student_update.dict(exclude_unset=True)

  for field, value in update_data.items():
    setattr(db_student, field, value)

  await db.commit()
  await db.refresh(db_student)
  return db_student

async def get_all_students(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Student]:
  """Получить всех студентов с пагинацией"""
  result = await db.execute(
    select(models.Student).offset(skip).limit(limit)
  )
  return result.scalars().all()

async def delete_student(db: AsyncSession, student_id: str) -> bool:
  """Удалить студента"""
  student = await get_student_by_id(db, student_id)
  if student:
    await db.delete(student)
    await db.commit()
    return True
  return False

async def remove_student_from_group(db: AsyncSession, student_id: uuid.UUID, group_id: int) -> bool:
  """Удалить студента из группы (удалить запись из связи many-to-many)"""
  stmt = delete(models.group_students).where(
    models.group_students.c.student_id == student_id,
    models.group_students.c.group_id == group_id
  )
  result = await db.execute(stmt)
  await db.commit()
  return result.rowcount > 0


async def delete_student_by_telegram_id(db: AsyncSession, telegram_id: int) -> bool:
  """Удалить студента по telegram_id"""
  student = await get_student_by_telegram_id(db, telegram_id)
  if student:
    await db.delete(student)
    await db.commit()
    return True
  return False

async def add_student_to_group(db: AsyncSession, student_id: str, group_id: str):
  """Добавить студента в группу"""
  stmt = models.group_students.insert().values(student_id=student_id, group_id=group_id)
  await db.execute(stmt)
  await db.commit()

async def create_group(db: AsyncSession, group_data):
  """Создать новую группу"""
  existing_group = await db.get(models.Group, group_data.id)
  if existing_group:
    return existing_group

  new_group = models.Group(id=group_data.id)
  db.add(new_group)
  await db.commit()
  await db.refresh(new_group)
  return new_group

async def get_students_in_group(db: AsyncSession, group_id: int) -> List[models.Student]:
  """Получить всех студентов в группе"""
  result = await db.execute(
    select(models.Student)
    .join(models.group_students, models.Student.id == models.group_students.c.student_id)
    .where(models.group_students.c.group_id == group_id)
  )
  return result.scalars().all()
