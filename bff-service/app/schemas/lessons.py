from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator, model_validator
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

class LessonSessionCreate(BaseModel):
  start_time: datetime
  end_time: datetime

class LessonSessionUpdate(BaseModel):
  start_time: Optional[datetime] = None
  end_time: Optional[datetime] = None
  status: Optional[LessonStatus] = None

class BookedByShort(BaseModel):
  type: str
  id: str
  name:  Optional[str] = None

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

class LessonParticipantResponse(LessonParticipantBase):
  id: int
  confirmation_date: Optional[datetime] = None
  class Config:
      orm_mode = True

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

class CreateFullLessonPayload(BaseModel):
  lesson: LessonCreate
  session: LessonSessionCreate
  teacher_telegram_id: int

class EnrollmentCreate(BaseModel):
  lesson_id: int
  student_id: Optional[UUID] = None
  group_id: Optional[int] = None

  model_config = {
    "json_schema_extra": {
      "example": {
        "lesson_id": 1,
        "student_id": "123e4567-e89b-12d3-a456-426614174000",
        "group_id": None
      }
    }
  }

  @model_validator(mode='after')
  def validate_student_or_group(self):
    if self.student_id is None and self.group_id is None:
      raise ValueError('Either student_id or group_id must be provided')
    if self.student_id is not None and self.group_id is not None:
      raise ValueError('Provide either student_id OR group_id, not both')
    return self

class BulkEnrollmentRequest(BaseModel):
  student_ids: List[UUID]
