from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.teacher import TeacherResponse
from app.schemas.student import StudentWithUserDataResponse

class GroupType(str, Enum):
  REGULAR = "REGULAR"
  INTENSIVE = "INTENSIVE"
  CONVERSATION = "CONVERSATION"
  GRAMMAR = "GRAMMAR"

  @classmethod
  def _missing_(cls, value):
    if isinstance(value, str):
      value_upper = value.upper()
      for member in cls:
        if member.value == value_upper:
          return member
    return None

class GroupStatus(str, Enum):
  ACTIVE = "ACTIVE"
  INACTIVE = "INACTIVE"
  FULL = "FULL"
  WAITLIST = "WAITLIST"

  @classmethod
  def _missing_(cls, value):
    if isinstance(value, str):
      value_upper = value.upper()
      for member in cls:
        if member.value == value_upper:
          return member
    return None

class GroupBase(BaseModel):
  name: str
  description: Optional[str] = None
  group_type: Optional[GroupType] = GroupType.REGULAR
  max_students: Optional[int] = 10
  language: str
  level: str
  start_date: Optional[datetime] = None
  end_date: Optional[datetime] = None

class GroupCreate(GroupBase):
  pass

class GroupUpdate(GroupBase):
  pass

class GroupRead(GroupBase):
  id: int
  teacher_telegram_id: int
  current_students: int
  status: GroupStatus
  is_active: bool

  teacher: Optional[TeacherResponse] = None
  students: List[StudentWithUserDataResponse] = []

  class Config:
    orm_mode = True

class AddMemberRequest(BaseModel):
  group_id: int

class InvitationCreateRequest(BaseModel):
  group_id: int
  expires_in_hours: Optional[int] = Field(default=24, gt=0)
  message: Optional[str]
