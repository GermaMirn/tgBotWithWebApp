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
    print(f"[CRUD] Creating teacher with telegram_id: {teacher.telegram_id}")
    print(f"[CRUD] Teacher data: bio={teacher.bio}, specialization={teacher.specialization}, experience={teacher.experience_years}, education={teacher.education}, hourly_rate={teacher.hourly_rate}")

    try:
        db_teacher = models.Teacher(
            telegram_id=teacher.telegram_id,
            bio=teacher.bio,
            specialization=teacher.specialization,
            experience_years=teacher.experience_years or 0,
            education=teacher.education,
            certificates=json.dumps(teacher.certificates) if teacher.certificates else None,
            hourly_rate=teacher.hourly_rate
        )
        print(f"[CRUD] Teacher model created, adding to session...")
        db.add(db_teacher)
        print(f"[CRUD] Committing to database...")
        await db.commit()
        print(f"[CRUD] Committed, refreshing teacher...")
        await db.refresh(db_teacher)
        print(f"[CRUD] Teacher created with id: {db_teacher.id}")

        if db_teacher.certificates:
            db_teacher.certificates = json.loads(db_teacher.certificates)

        print(f"[CRUD] Returning teacher: id={db_teacher.id}, telegram_id={db_teacher.telegram_id}")
        return db_teacher
    except Exception as e:
        print(f"[CRUD] Error in create_teacher: {str(e)}")
        import traceback
        print(f"[CRUD] Traceback: {traceback.format_exc()}")
        await db.rollback()
        raise

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

# StudioLanguage CRUD operations
async def get_studio_languages(db: AsyncSession, active_only: bool = False) -> List[models.StudioLanguage]:
    """Получить список языков студии"""
    query = select(models.StudioLanguage)
    if active_only:
        query = query.filter(models.StudioLanguage.is_active == True)
    result = await db.execute(query.order_by(models.StudioLanguage.name))
    return result.scalars().all()

async def get_studio_language(db: AsyncSession, language_id: int) -> Optional[models.StudioLanguage]:
    """Получить язык по ID"""
    result = await db.execute(select(models.StudioLanguage).filter(models.StudioLanguage.id == language_id))
    return result.scalars().first()

async def get_studio_language_by_code(db: AsyncSession, code: str) -> Optional[models.StudioLanguage]:
    """Получить язык по коду"""
    result = await db.execute(select(models.StudioLanguage).filter(models.StudioLanguage.code == code))
    return result.scalars().first()

async def create_studio_language(db: AsyncSession, language_data) -> models.StudioLanguage:
    """Создать новый язык"""
    existing_by_code = await get_studio_language_by_code(db, language_data.code)
    if existing_by_code:
        raise ValueError(f"Язык с кодом '{language_data.code}' уже существует")

    existing_by_name = await db.execute(
        select(models.StudioLanguage).filter(models.StudioLanguage.name == language_data.name)
    )
    if existing_by_name.scalars().first():
        raise ValueError(f"Язык с названием '{language_data.name}' уже существует")

    db_language = models.StudioLanguage(
        name=language_data.name,
        code=language_data.code,
        is_active=language_data.is_active if hasattr(language_data, 'is_active') else True
    )
    db.add(db_language)
    await db.commit()
    await db.refresh(db_language)
    return db_language

async def update_studio_language(db: AsyncSession, language: models.StudioLanguage, update_data) -> models.StudioLanguage:
    """Обновить язык"""
    if hasattr(update_data, 'code') and update_data.code and update_data.code != language.code:
        existing = await get_studio_language_by_code(db, update_data.code)
        if existing:
            raise ValueError(f"Язык с кодом '{update_data.code}' уже существует")

    if hasattr(update_data, 'name') and update_data.name and update_data.name != language.name:
        existing = await db.execute(
            select(models.StudioLanguage).filter(
                models.StudioLanguage.name == update_data.name,
                models.StudioLanguage.id != language.id
            )
        )
        if existing.scalars().first():
            raise ValueError(f"Язык с названием '{update_data.name}' уже существует")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(language, key, value)
    await db.commit()
    await db.refresh(language)
    return language

async def delete_studio_language(db: AsyncSession, language: models.StudioLanguage) -> None:
    """Удалить язык"""
    await db.delete(language)
    await db.commit()
