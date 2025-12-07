from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.auth import get_current_user
from app.schemas.language import StudioLanguageCreate, StudioLanguageUpdate, StudioLanguageRead
from typing import List
import httpx

router = APIRouter(tags=["languages"])

TEACHERS_SERVICE_URL = "http://teachers-service:8003/languages"

@router.get("", response_model=List[StudioLanguageRead])
async def get_languages(
  active_only: bool = Query(False, description="Получить только активные языки")
):
  """Получить список языков студии"""
  try:
    async with httpx.AsyncClient() as client:
      response = await client.get(
        f"{TEACHERS_SERVICE_URL}",
        params={"active_only": active_only},
        timeout=10
      )
      if response.status_code != 200:
        error_text = response.text
        raise HTTPException(status_code=response.status_code, detail=error_text)
      return response.json()
  except Exception as e:
    raise HTTPException(status_code=502, detail=f"teachers-service error: {str(e)}")

@router.get("/{language_id}", response_model=StudioLanguageRead)
async def get_language(language_id: int):
  """Получить язык по ID"""
  try:
    async with httpx.AsyncClient() as client:
      response = await client.get(
        f"{TEACHERS_SERVICE_URL}/{language_id}",
        timeout=10
      )
      response.raise_for_status()
      return response.json()
  except httpx.HTTPStatusError as e:
    try:
      error_data = e.response.json()
      error_detail = error_data.get("detail", "Ошибка при получении языка")
      if isinstance(error_detail, str) and error_detail.strip().startswith('{'):
        import json
        try:
          nested = json.loads(error_detail)
          error_detail = nested.get("detail", error_detail)
        except:
          pass
    except:
      error_detail = "Ошибка при получении языка"
    raise HTTPException(status_code=e.response.status_code, detail=error_detail)
  except Exception as e:
    error_msg = str(e) if not isinstance(e, str) else e
    raise HTTPException(status_code=502, detail=f"teachers-service error: {error_msg}")

@router.post("", response_model=StudioLanguageRead, status_code=201)
async def create_language(
  language: StudioLanguageCreate,
):
  """Создать новый язык (доступно всем авторизованным пользователям)"""
  try:
    async with httpx.AsyncClient() as client:
      response = await client.post(
        f"{TEACHERS_SERVICE_URL}",
        json=language.dict(),
        timeout=10
      )
      if response.status_code != 201:
        error_text = response.text
        raise HTTPException(status_code=response.status_code, detail=error_text)
      return response.json()
  except Exception as e:
    raise HTTPException(status_code=502, detail=f"teachers-service error: {str(e)}")

@router.put("/{language_id}", response_model=StudioLanguageRead)
async def update_language(
  language_id: int,
  language_update: StudioLanguageUpdate,
  current_user: dict = Depends(get_current_user)
):
  """Обновить язык (только для админов)"""
  role = current_user.get("role")
  if role != "admin":
    raise HTTPException(status_code=403, detail="Недостаточно прав для обновления языка")

  try:
    async with httpx.AsyncClient() as client:
      response = await client.put(
        f"{TEACHERS_SERVICE_URL}/{language_id}",
        json=language_update.dict(exclude_unset=True),
        timeout=10
      )
      if response.status_code != 200:
        error_text = response.text
        raise HTTPException(status_code=response.status_code, detail=error_text)
      return response.json()
  except Exception as e:
    raise HTTPException(status_code=502, detail=f"teachers-service error: {str(e)}")

@router.delete("/{language_id}", status_code=204)
async def delete_language(
  language_id: int,
  current_user: dict = Depends(get_current_user)
):
  """Удалить язык (только для админов)"""
  role = current_user.get("role")
  if role != "admin":
    raise HTTPException(status_code=403, detail="Недостаточно прав для удаления языка")

  try:
    async with httpx.AsyncClient() as client:
      response = await client.delete(
        f"{TEACHERS_SERVICE_URL}/{language_id}",
        timeout=10
      )
      if response.status_code != 204:
        error_text = response.text
        raise HTTPException(status_code=response.status_code, detail=error_text)
      return None
  except Exception as e:
    raise HTTPException(status_code=502, detail=f"teachers-service error: {str(e)}")

