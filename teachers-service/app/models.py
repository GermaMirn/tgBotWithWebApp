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
