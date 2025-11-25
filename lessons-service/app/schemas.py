from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, model_validator, field_validator
from enum import Enum
from uuid import UUID

class LessonStatus(str, Enum):
  scheduled = "SCHEDULED"
  in_progress = "IN_PROGRESS"
  completed = "COMPLETED"
  cancelled = "CANCELLED"

class LessonType(str, Enum):
  individual = "INDIVIDUAL"
  group = "GROUP"
  trial = "TRIAL"

# ---- Lesson ----
class LessonBase(BaseModel):
  title: str
  description: Optional[str] = None
  lesson_type: LessonType
  language: str
  level: str
  teacher_telegram_id: int

class LessonCreate(LessonBase):
  pass

class LessonUpdate(BaseModel):
  title: Optional[str] = None
  description: Optional[str] = None
  lesson_type: Optional[LessonType] = None
  language: Optional[str] = None
  level: Optional[str] = None

class LessonResponse(LessonBase):
  id: int
  class Config:
      orm_mode = True

# ---- LessonSession ----
class LessonSessionBase(BaseModel):
  lesson_id: int
  start_time: datetime
  end_time: datetime

class LessonSessionCreate(LessonSessionBase):
  status: Optional[LessonStatus] = LessonStatus.scheduled

class LessonSessionUpdate(BaseModel):
  start_time: Optional[datetime] = None
  end_time: Optional[datetime] = None
  status: Optional[LessonStatus] = None

class BookedBy(BaseModel):
  type: str
  id: str

class LessonShort(BaseModel):
  id: int
  title: str
  description: Optional[str] = None
  lesson_type: str
  language: str
  level: str
  teacher_telegram_id: int

  class Config:
    orm_mode = True

class LessonSessionResponse(LessonSessionBase):
  id: int
  status: LessonStatus
  booked: bool
  booked_by: Optional[BookedBy] = None
  lesson: Optional[LessonShort] = None

  class Config:
    orm_mode = True

# ---- LessonParticipant ----
class LessonParticipantBase(BaseModel):
  lesson_id: int
  student_id: Optional[str] = None   # UUID (str)
  group_id: Optional[int] = None
  is_confirmed: bool = False

class LessonParticipantCreate(LessonParticipantBase):
  pass

class LessonParticipantUpdate(BaseModel):
  is_confirmed: Optional[bool] = None

class LessonParticipantResponse(BaseModel):
  id: int
  lesson_id: int
  student_id: Optional[str] = None
  group_id: Optional[int] = None
  is_confirmed: bool
  confirmation_date: Optional[datetime] = None

  model_config = {
      "from_attributes": True
  }

  @classmethod
  def from_orm(cls, obj):
    data = {
      "id": obj.id,
      "lesson_id": obj.lesson_id,
      "student_id": str(obj.student_id) if obj.student_id else None,
      "group_id": obj.group_id,
      "is_confirmed": obj.is_confirmed,
      "confirmation_date": obj.confirmation_date
    }
    return cls(**data)

# ---- LessonAttendance ----
class LessonAttendanceBase(BaseModel):
  lesson_id: int
  student_id: str  # UUID

class LessonAttendanceCreate(LessonAttendanceBase):
  status: str  # "present" | "absent" | "late"
  join_time: Optional[datetime] = None
  leave_time: Optional[datetime] = None

class LessonAttendanceResponse(LessonAttendanceCreate):
  id: int
  created_at: datetime
  class Config:
      orm_mode = True

# ---- Slots/availability ----
class TimeSlot(BaseModel):
  start: datetime
  end: datetime
  available: bool

class FreeSlotsResponse(BaseModel):
  teacher_telegram_id: int
  date: str
  slots: List[TimeSlot]

class TeacherSessionsRequest(BaseModel):
  teacher_telegram_id: int
  start: date
  end: date

class EnrollmentCreate(BaseModel):
  lesson_id: int
  student_id: Optional[UUID] = None
  group_id: Optional[int] = None

  class Config:
    json_schema_extra = {
      "example": {
        "lesson_id": 1,
        "student_id": "123e4567-e89b-12d3-a456-426614174000",
        "group_id": None
      }
    }

  @model_validator(mode='after')
  def validate_student_or_group(self):
    if self.student_id is None and self.group_id is None:
      raise ValueError('Either student_id or group_id must be provided')
    if self.student_id is not None and self.group_id is not None:
      raise ValueError('Provide either student_id OR group_id, not both')
    return self
