from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
  id: UUID
  telegram_id: int
  username: Optional[str] = None
  full_name: str
  phone_number: Optional[str] = None
  email: Optional[str] = None
  is_active: bool
  is_verified: bool
  role: str
  timezone: str = "Europe/Kaliningrad"
  created_at: datetime
  updated_at: Optional[datetime] = None

class UserCreate(BaseModel):
  telegram_id: int
  username: Optional[str] = None
  full_name: str
  phone_number: Optional[str] = None
  email: Optional[str] = None
  role: str = "student"

class UserUpdate(BaseModel):
  username: Optional[str] = None
  full_name: Optional[str] = None
  phone_number: Optional[str] = None
  email: Optional[str] = None
  timezone: Optional[str] = None
