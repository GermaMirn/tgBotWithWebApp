from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime

# Схемы для TeacherSchedule (недельное расписание)
class TeacherScheduleBase(BaseModel):
    teacher_telegram_id: int
    day_of_week: int = Field(..., ge=0, le=6)  # 0-6 (понедельник-воскресенье)
    start_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    end_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    is_available: bool = True

    model_config = ConfigDict(from_attributes=True)

class TeacherScheduleCreate(TeacherScheduleBase):
    model_config = ConfigDict(from_attributes=True)

class TeacherScheduleUpdate(BaseModel):
    start_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    end_time: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    is_available: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class TeacherScheduleResponse(TeacherScheduleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Схемы для запросов календаря
class CalendarRequest(BaseModel):
    teacher_telegram_id: int
    start_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)

class CalendarDayResponse(BaseModel):
    date: date
    is_active: bool
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    booked_slots: List[str] = []

    model_config = ConfigDict(from_attributes=True)

class CalendarResponse(BaseModel):
    teacher_telegram_id: int
    days: List[CalendarDayResponse]

    model_config = ConfigDict(from_attributes=True)

# Схемы для временных слотов
class TimeSlotResponse(BaseModel):
    time: str
    available: bool
    booked: bool
    unavailable: bool

    model_config = ConfigDict(from_attributes=True)

class TeacherSpecialDayCreate(BaseModel):
    teacher_telegram_id: int
    date: date
    start_time: str
    end_time: str

    model_config = ConfigDict(from_attributes=True)

class TeacherSpecialDayResponse(TeacherSpecialDayCreate):
    id: int
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)

class TeacherUnavailableResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TeacherSpecialDayUpdate(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class FullScheduleRequest(BaseModel):
    start: date
    end: date

    model_config = ConfigDict(from_attributes=True)

class TeacherScheduleFullResponse(BaseModel):
    weekly_schedules: List[TeacherScheduleResponse]
    special_days: List[TeacherSpecialDayResponse]
    unavailable_periods: List[TeacherUnavailableResponse]

    model_config = ConfigDict(from_attributes=True)
