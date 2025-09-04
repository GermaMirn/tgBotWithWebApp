from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

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

class LessonSessionResponse(LessonSessionBase):
  id: int
  status: LessonStatus
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
