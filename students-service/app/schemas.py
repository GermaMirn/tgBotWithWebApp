from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class StudentBase(BaseModel):
  level: str = Field(..., description="Уровень студента", example="beginner")
  preferred_languages: List[str] = Field(default=[], description="Предпочитаемые языки", example=["английский", "испанский"])
  study_goals: Optional[str] = Field(None, description="Цели обучения", example="Подготовка к экзамену IELTS")

class StudentCreate(StudentBase):
  telegram_id: int = Field(..., description="Telegram ID пользователя")

class StudentUpdate(BaseModel):
  level: Optional[str] = Field(None, description="Уровень студента")
  preferred_languages: Optional[List[str]] = Field(None, description="Предпочитаемые языки")
  study_goals: Optional[str] = Field(None, description="Цели обучения")

class StudentResponse(StudentBase):
  id: UUID
  telegram_id: int

  class Config:
    orm_mode = True

class GroupBase(BaseModel):
  id: int

class GroupRead(GroupBase):
  pass

class GroupCreate(GroupBase):
  pass
