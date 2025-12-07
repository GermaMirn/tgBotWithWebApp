from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app import models
from app.schemas import UserCreate
from app.utils.config import settings
import httpx
from typing import List


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
  result = await db.execute(
    select(models.User).where(models.User.telegram_id == telegram_id)
  )
  return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
  # Определяем роль пользователя на основе конфигурации
  role = "admin" if settings.is_admin(user.telegram_id) else "student"

  db_user = models.User(
    telegram_id=user.telegram_id,
    username=user.username or None,
    full_name=user.full_name or 'Пользователь',
    role=role,
    is_active=True,
    is_verified=False,
    timezone='Europe/Kaliningrad'
  )
  db.add(db_user)
  await db.commit()
  await db.refresh(db_user)
  return db_user

async def update_user(db: AsyncSession, db_user: models.User, user_data: UserCreate):
  """Обновляет данные пользователя"""
  db_user.username = user_data.username
  db_user.full_name = user_data.full_name
  await db.commit()
  await db.refresh(db_user)
  return db_user

async def update_user_profile(db: AsyncSession, db_user: models.User, profile_data):
  """Обновляет профиль пользователя (phone_number, email)"""
  if profile_data.phone_number is not None:
    db_user.phone_number = profile_data.phone_number
  if profile_data.email is not None:
    db_user.email = profile_data.email

  await db.commit()
  await db.refresh(db_user)
  return db_user

async def check_user_changes(db_user: models.User, user_data: UserCreate) -> bool:
  """Проверяет, изменились ли данные пользователя"""
  return (
    db_user.username != user_data.username or
    db_user.full_name != user_data.full_name
  )

async def get_user(db: AsyncSession, user_id: str):
  result = await db.execute(
    select(models.User).where(models.User.id == user_id)
  )
  return result.scalars().first()

async def get_all_users(db: AsyncSession):
  result = await db.execute(select(models.User))
  return result.scalars().all()

async def get_users_by_role(db: AsyncSession, role: str = None):
  """Получает пользователей с фильтрацией по роли"""
  if role:
    result = await db.execute(
      select(models.User).where(models.User.role == role)
    )
  else:
    result = await db.execute(select(models.User))
  return result.scalars().all()


# CRUD операции для ссылок переключения ролей
async def create_role_switch_link(
  db: AsyncSession,
  target_role: str,
  created_by: str,
  token: str,
  expires_at,
  target_user_id: str = None,
  target_user_name: str = None
):
  """Создает новую ссылку для переключения роли"""
  db_link = models.RoleSwitchLink(
    token=token,
    target_role=target_role,
    target_user_id=target_user_id,
    target_user_name=target_user_name,
    created_by=created_by,
    expires_at=expires_at
  )
  db.add(db_link)
  await db.commit()
  await db.refresh(db_link)
  return db_link

async def get_role_switch_link_by_token(db: AsyncSession, token: str):
  """Получает ссылку по токену"""
  result = await db.execute(
    select(models.RoleSwitchLink).where(models.RoleSwitchLink.token == token)
  )
  return result.scalars().first()

async def mark_role_switch_link_as_used(
  db: AsyncSession,
  link_id: str,
  used_by: str
):
  """Отмечает ссылку как использованную"""
  result = await db.execute(
    select(models.RoleSwitchLink).where(models.RoleSwitchLink.id == link_id)
  )
  link = result.scalars().first()
  if link:
    link.is_used = True
    link.used_by = used_by
    link.used_at = func.now()
    await db.commit()
    await db.refresh(link)
  return link

async def update_user_role(db: AsyncSession, user_id: str, new_role: str):
  """Обновляет роль пользователя"""
  result = await db.execute(
    select(models.User).where(models.User.id == user_id)
  )
  user = result.scalars().first()
  if user:
    user.role = new_role
    await db.commit()
    await db.refresh(user)
  return user

async def update_user_role_by_telegram_id(db: AsyncSession, telegram_id: int, new_role: str):
  """Обновляет роль пользователя по telegram_id"""
  result = await db.execute(
    select(models.User).where(models.User.telegram_id == telegram_id)
  )
  user = result.scalars().first()
  if user:
    user.role = new_role
    await db.commit()
    await db.refresh(user)
  return user

async def get_all_role_switch_links(db: AsyncSession):
  """Получает все ссылки для переключения ролей"""
  result = await db.execute(select(models.RoleSwitchLink))
  return result.scalars().all()

async def delete_role_switch_link(db: AsyncSession, link_id: str):
  """Удаляет ссылку для переключения роли"""
  result = await db.execute(
    select(models.RoleSwitchLink).where(models.RoleSwitchLink.id == link_id)
  )
  link = result.scalars().first()
  if link:
    await db.delete(link)
    await db.commit()
  return link

async def delete_student_profile(db: AsyncSession, telegram_id: int):
  """Удаляет профиль студента (вызов внешнего сервиса)"""
  try:
    async with httpx.AsyncClient() as client:
      response = await client.delete(f"http://students-service:8004/students/by-telegram/{telegram_id}")
      return response.status_code == 200
  except:
    return False

async def delete_teacher_profile(db: AsyncSession, telegram_id: int):
  """Удаляет профиль учителя (вызов внешнего сервиса)"""
  try:
    print(f"Trying to delete teacher profile with telegram_id: {telegram_id}")
    async with httpx.AsyncClient() as client:
      # Сначала получаем учителя по telegram_id
      get_response = await client.get(f"http://teachers-service:8003/teachers/by-telegram/{telegram_id}")
      print(f"Get teacher response status: {get_response.status_code}")

      if get_response.status_code == 200:
        teacher_data = get_response.json()
        teacher_id = teacher_data.get('id')
        print(f"Found teacher with ID: {teacher_id}")

        # Теперь удаляем по teacher_id
        delete_response = await client.delete(f"http://teachers-service:8003/teachers/{teacher_id}")
        print(f"Delete teacher response status: {delete_response.status_code}")
        if delete_response.status_code != 204:
          print(f"Delete teacher response text: {delete_response.text}")
        return delete_response.status_code == 204
      else:
        print(f"Teacher not found with telegram_id: {telegram_id}")
        return False
  except Exception as e:
    print(f"Exception in delete_teacher_profile: {e}")
    return False

async def create_teacher_profile_if_not_exists(db: AsyncSession, telegram_id: int):
  """Создает профиль учителя в teachers-service, если его еще нет"""
  try:
    print(f"[Auth Service] Creating teacher profile if not exists for telegram_id: {telegram_id}")
    async with httpx.AsyncClient() as client:
      # Проверяем, существует ли уже учитель
      get_response = await client.get(
        f"http://teachers-service:8003/teachers/by-telegram/{telegram_id}",
        timeout=10
      )

      if get_response.status_code == 200:
        print(f"[Auth Service] Teacher profile already exists for telegram_id: {telegram_id}")
        return True

      if get_response.status_code != 404:
        print(f"[Auth Service] Unexpected status when checking teacher: {get_response.status_code}")
        return False

      # Учителя нет, создаем его с минимальными данными
      print(f"[Auth Service] Teacher not found, creating new teacher profile...")
      create_response = await client.post(
        f"http://teachers-service:8003/teachers/create-without-auth",
        json={
          "telegram_id": telegram_id,
          "bio": None,
          "specialization": None,
          "experience_years": 0,
          "education": None,
          "certificates": [],
          "hourly_rate": None
        },
        timeout=10
      )

      if create_response.status_code == 201:
        print(f"[Auth Service] Teacher profile created successfully for telegram_id: {telegram_id}")
        return True
      elif create_response.status_code == 400:
        # Учитель уже существует (race condition)
        print(f"[Auth Service] Teacher already exists (race condition) for telegram_id: {telegram_id}")
        return True
      else:
        error_text = create_response.text
        print(f"[Auth Service] Failed to create teacher profile: {create_response.status_code} - {error_text}")
        return False
  except httpx.RequestError as e:
    print(f"[Auth Service] Request error creating teacher profile: {e}")
    return False
  except Exception as e:
    print(f"[Auth Service] Exception creating teacher profile: {e}")
    import traceback
    print(f"[Auth Service] Traceback: {traceback.format_exc()}")
    return False

async def get_users_by_telegram_ids(db: AsyncSession, ids: List[int]) -> List[models.User]:
  """Получить пользователей по списку telegram_id"""
  result = await db.execute(
    select(models.User).where(models.User.telegram_id.in_(ids))
  )
  return result.scalars().all()
