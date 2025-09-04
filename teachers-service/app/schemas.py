from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class TeacherBase(BaseModel):
    bio: Optional[str] = Field(None, description="Биография преподавателя", example="Опытный преподаватель английского языка с 5-летним стажем")
    specialization: Optional[str] = Field(None, description="Специализация", example="Английский язык")
    experience_years: int = Field(default=0, description="Годы опыта", example=5)
    education: Optional[str] = Field(None, description="Образование", example="Высшее педагогическое образование")
    certificates: Optional[List[str]] = Field(None, description="Сертификаты")
    hourly_rate: Optional[float] = Field(None, description="Почасовая ставка", example=25.0)

class TeacherCreate(TeacherBase):
    telegram_id: int = Field(..., description="Telegram ID пользователя")

class TeacherUpdate(TeacherBase):
    pass

class TeacherResponse(TeacherBase):
    id: UUID
    telegram_id: int

    class Config:
        from_attributes = True
