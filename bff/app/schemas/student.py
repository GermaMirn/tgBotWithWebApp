from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class StudentBase(BaseModel):
    level: str = Field(..., description="Уровень студента", example="beginner")
    preferred_languages: List[str] = Field(default=[], description="Предпочитаемые языки", example=["английский", "испанский"])
    study_goals: Optional[str] = Field(None, description="Цели обучения", example="Подготовка к экзамену IELTS")

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    level: Optional[str] = Field(None, description="Уровень студента")
    preferred_languages: Optional[List[str]] = Field(None, description="Предпочитаемые языки")
    study_goals: Optional[str] = Field(None, description="Цели обучения")


class StudentWithUserDataResponse(StudentBase):
    id: UUID
    telegram_id: int
    username: Optional[str] = None
    full_name: str
    phone_number: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

class StudentResponse(StudentBase):
    id: UUID
    telegram_id: int

    class Config:
        from_attributes = True

class StudentLanguage(BaseModel):
    id: int
    student_id: UUID
    language: str
    current_level: str
    target_level: Optional[str] = None

    class Config:
        from_attributes = True
