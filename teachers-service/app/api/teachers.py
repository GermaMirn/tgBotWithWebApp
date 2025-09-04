from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas
from typing import List

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "teachers-service"}

@router.post("/", response_model=schemas.TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher: schemas.TeacherCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать нового преподавателя"""
    existing_teacher = await crud.get_teacher_by_telegram_id(db, teacher.telegram_id)
    if existing_teacher:
        raise HTTPException(
            status_code=400,
            detail="Teacher with this telegram_id already exists"
        )
    return await crud.create_teacher(db=db, teacher=teacher)

@router.post("/create-without-auth", response_model=schemas.TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher_without_auth(
    teacher: schemas.TeacherCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать нового преподавателя без авторизации (для переключения ролей)"""
    existing_teacher = await crud.get_teacher_by_telegram_id(db, teacher.telegram_id)
    if existing_teacher:
        raise HTTPException(
            status_code=400,
            detail="Teacher with this telegram_id already exists"
        )
    return await crud.create_teacher(db=db, teacher=teacher)

@router.get("/", response_model=List[schemas.TeacherResponse])
async def get_teachers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех преподавателей"""
    teachers = await crud.get_all_teachers(db, skip=skip, limit=limit)
    return teachers

@router.get("/{teacher_id}", response_model=schemas.TeacherResponse)
async def get_teacher(
    teacher_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Получить преподавателя по ID"""
    teacher = await crud.get_teacher_by_id(db, teacher_id=teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.get("/by-telegram/{telegram_id}", response_model=schemas.TeacherResponse)
async def get_teacher_by_telegram(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить преподавателя по telegram_id"""
    teacher = await crud.get_teacher_by_telegram_id(db, telegram_id=telegram_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.get("/me/{telegram_id}", response_model=schemas.TeacherResponse)
async def get_current_teacher(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить данные текущего преподавателя (alias для by-telegram)"""
    teacher = await crud.get_teacher_by_telegram_id(db, telegram_id=telegram_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.put("/{teacher_id}", response_model=schemas.TeacherResponse)
async def update_teacher(
    teacher_id: str,
    teacher_update: schemas.TeacherUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить данные преподавателя"""
    db_teacher = await crud.get_teacher_by_id(db, teacher_id=teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return await crud.update_teacher(db=db, db_teacher=db_teacher, teacher_update=teacher_update)

@router.put("/by-telegram/{telegram_id}", response_model=schemas.TeacherResponse)
async def update_teacher_by_telegram(
    telegram_id: int,
    teacher_update: schemas.TeacherUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить данные преподавателя по telegram_id"""
    db_teacher = await crud.get_teacher_by_telegram_id(db, telegram_id=telegram_id)
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return await crud.update_teacher(db=db, db_teacher=db_teacher, teacher_update=teacher_update)

@router.put("/me/{telegram_id}", response_model=schemas.TeacherResponse)
async def update_current_teacher(
    telegram_id: int,
    teacher_update: schemas.TeacherUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить данные текущего преподавателя (alias для by-telegram)"""
    db_teacher = await crud.get_teacher_by_telegram_id(db, telegram_id=telegram_id)
    if not db_teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return await crud.update_teacher(db=db, db_teacher=db_teacher, teacher_update=teacher_update)

@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Удалить преподавателя"""
    success = await crud.delete_teacher(db, teacher_id=teacher_id)
    if not success:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return None

@router.delete("/by-telegram/{telegram_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher_by_telegram(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить преподавателя по telegram_id"""
    success = await crud.delete_teacher_by_telegram_id(db, telegram_id=telegram_id)
    if not success:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return None
