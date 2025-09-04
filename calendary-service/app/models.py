from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, Date
from sqlalchemy.sql import func
from app.database import Base

class TeacherSchedule(Base):
  __tablename__ = "teacher_schedules"

  id = Column(Integer, primary_key=True, index=True)
  teacher_telegram_id = Column(BigInteger, nullable=False)

  day_of_week = Column(Integer, nullable=False)  # 0-6 (пн-вск)
  start_time = Column(String(5), nullable=False)  # "09:00"
  end_time = Column(String(5), nullable=False)  # "18:00"

  is_available = Column(Boolean, default=True)

  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TeacherUnavailable(Base):
  __tablename__ = "teacher_unavailable"

  id = Column(Integer, primary_key=True, index=True)
  teacher_telegram_id = Column(BigInteger, nullable=False)

  start_time = Column(DateTime(timezone=True), nullable=False)
  end_time = Column(DateTime(timezone=True), nullable=False)

  reason = Column(String(255), nullable=True)

  created_at = Column(DateTime(timezone=True), server_default=func.now())

class TeacherSpecialDay(Base):
  __tablename__ = "teacher_special_days"

  id = Column(Integer, primary_key=True, index=True)
  teacher_telegram_id = Column(BigInteger, nullable=False)

  date = Column(Date, nullable=False)  # конкретная дата
  start_time = Column(String(5), nullable=False)  # "10:00"
  end_time = Column(String(5), nullable=False)    # "14:00"

  created_at = Column(DateTime(timezone=True), server_default=func.now())
