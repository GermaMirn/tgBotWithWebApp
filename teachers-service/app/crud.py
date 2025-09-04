from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models
import json
from app.schemas import TeacherCreate, TeacherUpdate
from typing import List, Optional

async def get_teacher_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[models.Teacher]:
    """Получить преподавателя по telegram_id"""
    result = await db.execute(
        select(models.Teacher).where(models.Teacher.telegram_id == telegram_id)
    )
    teacher = result.scalars().first()
    if teacher and teacher.certificates:
        teacher.certificates = json.loads(teacher.certificates)
    return teacher

async def get_teacher_by_id(db: AsyncSession, teacher_id: str) -> Optional[models.Teacher]:
    """Получить преподавателя по id"""
    result = await db.execute(
        select(models.Teacher).where(models.Teacher.id == teacher_id)
    )
    teacher = result.scalars().first()
    if teacher and teacher.certificates:
        teacher.certificates = json.loads(teacher.certificates)
    return teacher

async def create_teacher(db: AsyncSession, teacher: TeacherCreate) -> models.Teacher:
    """Создать нового преподавателя"""
    db_teacher = models.Teacher(
        telegram_id=teacher.telegram_id,
        bio=teacher.bio,
        specialization=teacher.specialization,
        experience_years=teacher.experience_years,
        education=teacher.education,
        certificates=json.dumps(teacher.certificates) if teacher.certificates else None,
        hourly_rate=teacher.hourly_rate
    )
    db.add(db_teacher)
    await db.commit()
    await db.refresh(db_teacher)

    if db_teacher.certificates:
        db_teacher.certificates = json.loads(db_teacher.certificates)
    return db_teacher

async def update_teacher(db: AsyncSession, db_teacher: models.Teacher, teacher_update: TeacherUpdate) -> models.Teacher:
    """Обновить данные преподавателя"""
    update_data = teacher_update.dict(exclude_unset=True)

    if "certificates" in update_data:
        update_data["certificates"] = json.dumps(update_data["certificates"]) if update_data["certificates"] else None

    for field, value in update_data.items():
        setattr(db_teacher, field, value)

    await db.commit()
    await db.refresh(db_teacher)

    if db_teacher.certificates:
        db_teacher.certificates = json.loads(db_teacher.certificates)
    return db_teacher

async def get_all_teachers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Teacher]:
    """Получить всех преподавателей с пагинацией"""
    result = await db.execute(
        select(models.Teacher).offset(skip).limit(limit)
    )
    teachers = result.scalars().all()
    for t in teachers:
        if t.certificates:
            t.certificates = json.loads(t.certificates)
    return teachers

async def delete_teacher(db: AsyncSession, teacher_id: str) -> bool:
    """Удалить преподавателя"""
    teacher = await get_teacher_by_id(db, teacher_id)
    if teacher:
        await db.delete(teacher)
        await db.commit()
        return True
    return False

async def delete_teacher_by_telegram_id(db: AsyncSession, telegram_id: int) -> bool:
    """Удалить преподавателя по telegram_id"""
    teacher = await get_teacher_by_telegram_id(db, telegram_id)
    if teacher:
        await db.delete(teacher)
        await db.commit()
        return True
    return False
