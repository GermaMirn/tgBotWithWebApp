from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, Enum, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base

class LessonStatus(enum.Enum):
  SCHEDULED = "SCHEDULED"
  IN_PROGRESS = "IN_PROGRESS"
  COMPLETED = "COMPLETED"
  CANCELLED = "CANCELLED"

class LessonType(enum.Enum):
  INDIVIDUAL = "INDIVIDUAL"
  GROUP = "GROUP"
  TRIAL = "TRIAL"

class Lesson(Base):
  __tablename__ = "lessons"

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String(255), nullable=False)
  description = Column(Text, nullable=True)
  lesson_type = Column(Enum(LessonType, name="lessontype", native_enum=False), nullable=False)
  language = Column(String(50), nullable=False)
  level = Column(String(20), nullable=False)
  teacher_telegram_id = Column(BigInteger, nullable=False)

  sessions = relationship("LessonSession", back_populates="lesson")
  participants = relationship("LessonParticipant", back_populates="lesson")
  attendance = relationship("LessonAttendance", back_populates="lesson")

class LessonSession(Base):
  __tablename__ = "lesson_sessions"

  id = Column(Integer, primary_key=True, index=True)
  lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
  start_time = Column(DateTime(timezone=True), nullable=False)
  end_time = Column(DateTime(timezone=True), nullable=False)
  status = Column(Enum(LessonStatus), default=LessonStatus.SCHEDULED)

  created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

  lesson = relationship("Lesson", back_populates="sessions")

class LessonParticipant(Base):
  __tablename__ = "lesson_participants"

  id = Column(Integer, primary_key=True, index=True)
  lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
  student_id = Column(UUID(as_uuid=True), nullable=True)
  group_id = Column(Integer, nullable=True)
  is_confirmed = Column(Boolean, default=False)
  confirmation_date = Column(DateTime(timezone=True))

  lesson = relationship("Lesson", back_populates="participants")

  __table_args__ = (
    CheckConstraint(
      "(student_id IS NOT NULL OR group_id IS NOT NULL)",
      name="check_student_or_group_not_null"
    ),
    CheckConstraint(
      "NOT (student_id IS NOT NULL AND group_id IS NOT NULL)",
      name="check_student_and_group_mutually_exclusive"
    ),
  )

class LessonAttendance(Base):
  __tablename__ = "lesson_attendance"

  id = Column(Integer, primary_key=True, index=True)
  lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
  student_id = Column(UUID(as_uuid=True), nullable=False)

  status = Column(String(20), nullable=False)  # "present", "absent", "late"
  join_time = Column(DateTime(timezone=True), nullable=True)
  leave_time = Column(DateTime(timezone=True), nullable=True)

  created_at = Column(DateTime(timezone=True), server_default=func.now())

  lesson = relationship("Lesson", back_populates="attendance")
