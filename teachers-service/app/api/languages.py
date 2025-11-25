from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas
from typing import List

router = APIRouter()

@router.get("", response_model=List[schemas.StudioLanguageRead])
async def get_languages(
    active_only: bool = Query(False, description="Получить только активные языки"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список языков студии"""
    languages = await crud.get_studio_languages(db, active_only=active_only)
    return languages

@router.get("/{language_id}", response_model=schemas.StudioLanguageRead)
async def get_language(
    language_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить язык по ID"""
    language = await crud.get_studio_language(db, language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Язык не найден")
    return language

@router.post("", response_model=schemas.StudioLanguageRead, status_code=status.HTTP_201_CREATED)
async def create_language(
    language: schemas.StudioLanguageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новый язык"""
    try:
        new_language = await crud.create_studio_language(db, language)
        return new_language
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{language_id}", response_model=schemas.StudioLanguageRead)
async def update_language(
    language_id: int,
    language_update: schemas.StudioLanguageUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить язык"""
    language = await crud.get_studio_language(db, language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Язык не найден")

    try:
        updated_language = await crud.update_studio_language(db, language, language_update)
        return updated_language
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{language_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_language(
    language_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить язык"""
    language = await crud.get_studio_language(db, language_id)
    if not language:
        raise HTTPException(status_code=404, detail="Язык не найден")

    await crud.delete_studio_language(db, language)
    return None

