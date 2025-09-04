from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime, time
from enum import Enum

# Схемы для TeacherSchedule (недельное расписание)
class TeacherScheduleBase(BaseModel):
    teacher_telegram_id: int
    day_of_week: int = Field(..., ge=0, le=6)  # 0-6 (понедельник-воскресенье)
    start_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    end_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    is_available: bool = True

class TeacherScheduleCreate(TeacherScheduleBase):
    pass

class TeacherScheduleUpdate(BaseModel):
    start_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    end_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    is_available: Optional[bool] = None

class TeacherScheduleResponse(TeacherScheduleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Схемы для запросов календаря
class CalendarRequest(BaseModel):
    teacher_telegram_id: int
    start_date: date
    end_date: date

class CalendarDayResponse(BaseModel):
    date: date
    is_active: bool
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    booked_slots: List[str] = []

class CalendarResponse(BaseModel):
    teacher_telegram_id: int
    days: List[CalendarDayResponse]

# Схемы для временных слотов
class TimeSlotResponse(BaseModel):
    time: str
    available: bool
    booked: bool
    unavailable: bool

class TeacherSpecialDayCreate(BaseModel):
    teacher_telegram_id: int
    date: date
    start_time: str
    end_time: str

class TeacherSpecialDayResponse(TeacherSpecialDayCreate):
    id: int
    is_active: bool = True

class TeacherUnavailableResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    reason: str | None = None

class TeacherScheduleFullResponse(BaseModel):
    weekly_schedules: List[TeacherScheduleResponse]
    special_days: List[TeacherSpecialDayResponse]
    unavailable_periods: List[TeacherUnavailableResponse]

class FullScheduleRequest(BaseModel):
    start: date
    end: date

class TeacherSpecialDayUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_active: Optional[bool] = None
