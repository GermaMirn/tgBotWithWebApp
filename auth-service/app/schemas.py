from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
  username: Optional[str] = Field(None, min_length=1, max_length=50, example="john_doe")
  telegram_id: Optional[int] = Field(None, example=123456789)
  full_name: Optional[str] = Field(None, example="John Doe")

class UserLoginRequest(UserBase):
  pass

class UserCreate(UserBase):
  pass

class UserResponse(BaseModel):
  id: UUID = Field(..., example="bb255a8c-1174-4114-9097-c5cba86ad9a5")
  telegram_id: int = Field(..., example=123456789)
  username: Optional[str] = Field(None, example="john_doe")
  full_name: str = Field(..., example="John Doe")
  phone_number: Optional[str] = Field(None, example="+1234567890")
  email: Optional[str] = Field(None, example="john@example.com")
  is_active: bool = Field(default=True)
  is_verified: bool = Field(default=False)
  created_at: datetime
  updated_at: Optional[datetime] = None
  role: str = Field(..., example="student")
  timezone: str = Field(default="Europe/Kaliningrad")

  class Config:
    from_attributes = True
    json_schema_extra = {
      "example": {
        "id": "bb255a8c-1174-4114-9097-c5cba86ad9a5",
        "telegram_id": 123456789,
        "username": "john_doe",
        "full_name": "John Doe",
        "phone_number": "+1234567890",
        "email": "john@example.com",
        "is_active": True,
        "is_verified": False,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "role": "student",
        "timezone": "Europe/Kaliningrad"
      }
    }

class Token(BaseModel):
  access_token: str = Field(..., example="eyJhbGciOi...")
  token_type: str = Field(default="bearer", example="bearer")


# Схемы для переключения ролей
class RoleSwitchLinkCreate(BaseModel):
  target_role: str = Field(..., description="Целевая роль", example="teacher")
  target_user_id: Optional[str] = Field(None, description="ID пользователя, которому меняется роль", example="bb255a8c-1174-4114-9097-c5cba86ad9a5")
  target_user_name: Optional[str] = Field(None, description="Имя пользователя, которому меняется роль", example="John Doe")
  expires_in_hours: int = Field(default=24, description="Время жизни ссылки в часах", example=24)

class RoleSwitchLinkResponse(BaseModel):
  id: UUID
  token: str
  target_role: str
  target_user_id: Optional[UUID] = Field(None, description="ID пользователя, которому меняется роль")
  target_user_name: Optional[str] = Field(None, description="Имя пользователя, которому меняется роль")
  expires_at: datetime
  created_at: datetime
  is_used: bool

  class Config:
    from_attributes = True

class RoleSwitchRequest(BaseModel):
  token: str = Field(..., description="Токен ссылки для переключения роли")

class RoleUpdate(BaseModel):
    user_id: str = Field(..., description="ID пользователя", example="bb255a8c-1174-4114-9097-c5cba86ad9a5")
    new_role: str = Field(..., description="Новая роль", example="teacher")

class RoleSwitchResponse(BaseModel):
    success: bool
    message: str
    new_role: str
    access_token: str

class UserProfileUpdate(BaseModel):
    phone_number: Optional[str] = Field(None, example="+1234567890")
    email: Optional[str] = Field(None, example="john@example.com")
