from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class GroupStatus(enum.Enum):
  ACTIVE = "active"
  INACTIVE = "inactive"
  FULL = "full"
  WAITLIST = "waitlist"

class GroupType(enum.Enum):
  REGULAR = "regular"
  INTENSIVE = "intensive"
  CONVERSATION = "conversation"
  GRAMMAR = "grammar"

class Group(Base):
  __tablename__ = "groups"

  id = Column(Integer, primary_key=True, index=True)

  # Основная информация
  name = Column(String(255), nullable=False)
  description = Column(Text, nullable=True)

  # Связь с преподавателем
  teacher_telegram_id = Column(BigInteger, nullable=False)

  # Настройки группы
  group_type = Column(Enum(GroupType), default=GroupType.REGULAR)
  max_students = Column(Integer, default=10)
  current_students = Column(Integer, default=0)

  # Язык и уровень
  language = Column(String(50), nullable=False)
  level = Column(String(20), nullable=False)  # "beginner", "intermediate", "advanced"

  # Статус
  status = Column(Enum(GroupStatus), default=GroupStatus.ACTIVE)
  is_active = Column(Boolean, default=True)

  # Дополнительная информация
  materials = Column(Text, nullable=True)  # JSON с материалами курса
  requirements = Column(Text, nullable=True)  # Требования к студентам

  # Временные метки
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())
  start_date = Column(DateTime(timezone=True), nullable=True)
  end_date = Column(DateTime(timezone=True), nullable=True)

  # Связи
  members = relationship("GroupMember", back_populates="group")
  enrollments = relationship("GroupEnrollment", back_populates="group")

class GroupMember(Base):
  __tablename__ = "group_members"

  id = Column(Integer, primary_key=True, index=True)
  group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
  student_telegram_id = Column(BigInteger, nullable=False)

  # Статус в группе
  status = Column(String(20), default='active')  # "active", "inactive", "waitlist"
  role = Column(String(20), default='student')  # "student", "assistant"

  # Даты
  joined_at = Column(DateTime(timezone=True), server_default=func.now())
  left_at = Column(DateTime(timezone=True), nullable=True)

  # Дополнительная информация
  notes = Column(Text, nullable=True)  # Заметки о студенте

  # Связи
  group = relationship("Group", back_populates="members")

class GroupEnrollment(Base):
  __tablename__ = "group_enrollments"

  id = Column(Integer, primary_key=True, index=True)
  group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
  student_telegram_id = Column(BigInteger, nullable=False)

  # Статус зачисления
  status = Column(String(20), default='active')  # "active", "inactive", "waitlist"
  enrollment_date = Column(DateTime(timezone=True), server_default=func.now())

  # Связи
  group = relationship("Group", back_populates="enrollments")

class GroupInvitation(Base):
  __tablename__ = "group_invitations"

  id = Column(Integer, primary_key=True, index=True)
  group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
  student_telegram_id = Column(BigInteger, nullable=False)
  invite_token = Column(String, nullable=False, unique=True)

  # Статус приглашения
  status = Column(String(20), default='pending')  # "pending", "accepted", "declined", "expired"

  # Временные метки
  sent_at = Column(DateTime(timezone=True), server_default=func.now())
  responded_at = Column(DateTime(timezone=True), nullable=True)
  expires_at = Column(DateTime(timezone=True), nullable=True)

  # Дополнительная информация
  message = Column(Text, nullable=True)  # Персональное сообщение с приглашением

class GroupProgress(Base):
  __tablename__ = "group_progress"

  id = Column(Integer, primary_key=True, index=True)
  group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)

  # Прогресс группы
  current_lesson = Column(Integer, default=1)
  total_lessons = Column(Integer, default=0)
  completion_percentage = Column(Integer, default=0)

  # Статистика
  average_attendance = Column(Integer, default=0)  # Процент посещаемости

  # Временные метки
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())
