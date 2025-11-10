from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Teacher(Base):
  __tablename__ = "teachers"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
  telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)  # Связь с auth-service

  # Профессиональная информация (специфичные данные преподавателя)
  bio = Column(Text, nullable=True)
  specialization = Column(String(255), nullable=True)  # например: "Английский язык"
  experience_years = Column(Integer, default=0)
  education = Column(Text, nullable=True)
  certificates = Column(Text, nullable=True)  # JSON строка с сертификатами
  hourly_rate = Column(Float, nullable=True)  # Почасовая ставка

class StudioLanguage(Base):
  __tablename__ = "studio_languages"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(100), nullable=False, unique=True)  # Название языка (например, "Английский")
  code = Column(String(10), nullable=False, unique=True)  # Код языка (например, "en", "chinese")
  is_active = Column(Boolean, default=True)  # Активен ли язык

  # Временные метки
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())
