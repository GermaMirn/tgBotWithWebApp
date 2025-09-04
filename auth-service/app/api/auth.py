from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas
from app.utils.auth import get_current_user
from typing import List
from app.utils.auth import create_access_token

router = APIRouter(prefix="/auth")

@router.post("/create", response_model=schemas.UserResponse)
async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):
  """Создание нового пользователя"""
  existing_user = await crud.get_user_by_telegram_id(db, user.telegram_id)
  if existing_user:
    raise HTTPException(
      status_code=400,
      detail="User with this telegram_id already exists"
    )

  return await crud.create_user(db=db, user=user)

# Вход пользователя
@router.post("/login", response_model=schemas.Token)
async def login(
  login_data: schemas.UserLoginRequest,
  db: AsyncSession = Depends(get_db)
):
  """Вход пользователя"""
  user = await crud.get_user_by_telegram_id(db, login_data.telegram_id)
  if not user:
    # Если пользователь не существует, создаем его
    user = await crud.create_user(db=db, user=schemas.UserCreate(
      telegram_id=login_data.telegram_id,
      username=login_data.username,
      full_name=login_data.full_name
    ))

  # Создаем JWT токен
  access_token = create_access_token(
    data={"sub": str(user.id), "telegram_id": user.telegram_id},
    role=user.role
  )

  return {
    "access_token": access_token,
    "token_type": "bearer",
    "user": user
  }

@router.get("/user", response_model=schemas.UserResponse)
async def get_current_user_info(
  current_user: dict = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  """Получение информации о текущем пользователе"""
  user = await crud.get_user(db, current_user.get("sub"))
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

@router.get("/users", response_model=List[schemas.UserResponse])
async def get_users(
  role: str = None,
  db: AsyncSession = Depends(get_db)
):
  """Получение списка пользователей"""
  if role:
    return await crud.get_users_by_role(db, role)
  else:
    return await crud.get_all_users(db)

@router.get("/user-by-telegram/{telegram_id}", response_model=schemas.UserResponse)
async def get_user_by_telegram(
  telegram_id: int,
  db: AsyncSession = Depends(get_db)
):
  """Получение пользователя по Telegram ID (публичный эндпоинт для BFF)"""
  user = await crud.get_user_by_telegram_id(db, telegram_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  return user

@router.put("/update-profile", response_model=schemas.UserResponse)
async def update_user_profile(
  profile_update: schemas.UserProfileUpdate,
  current_user: dict = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  """Обновление профиля пользователя"""
  user = await crud.get_user(db, current_user.get("sub"))
  if not user:
    raise HTTPException(status_code=404, detail="User not found")

  return await crud.update_user_profile(db, user, profile_update)

@router.put("/update-role", response_model=schemas.UserResponse)
async def update_user_role(
  role_update: schemas.RoleUpdate,
  current_user: dict = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  """Обновление роли пользователя (только для админов)"""
  if current_user.get("role") != "admin":
    raise HTTPException(
      status_code=403,
      detail="Only admins can update user roles"
    )

  user = await crud.get_user(db, role_update.user_id)
  if not user:
    raise HTTPException(status_code=404, detail="User not found")

  updated_user = await crud.update_user_role(
    db,
    role_update.user_id,
    role_update.new_role
  )

  return updated_user

@router.post("/users/by-ids", response_model=List[schemas.UserResponse])
async def get_users_by_ids(ids: List[int], db: AsyncSession = Depends(get_db)):
  return await crud.get_users_by_telegram_ids(db, ids)
