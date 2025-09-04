from sqlalchemy import Column, String, BigInteger, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid

class User(Base):
  __tablename__ = "users"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
  telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
  username = Column(String(255), nullable=True)
  full_name = Column(String(255), nullable=False)
  phone_number = Column(String(20), nullable=True)
  email = Column(String(255), nullable=True)
  is_active = Column(Boolean, default=True)
  is_verified = Column(Boolean, default=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Время последнего входа

  # Роль пользователя (student, teacher, admin)
  role = Column(String(50), default='student')

  # Часовой пояс по умолчанию Калининград
  timezone = Column(String(50), default='Europe/Kaliningrad')


class RoleSwitchLink(Base):
  __tablename__ = "role_switch_links"

  id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
  token = Column(String(255), unique=True, index=True, nullable=False)  # Уникальный токен для ссылки
  target_role = Column(String(50), nullable=False)  # Целевая роль (teacher, student)
  target_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # ID пользователя, которому меняется роль
  target_user_name = Column(String(255), nullable=True)  # Имя пользователя, которому меняется роль
  created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Кто создал ссылку
  used_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Кто использовал ссылку
  is_used = Column(Boolean, default=False)  # Использована ли ссылка
  expires_at = Column(DateTime(timezone=True), nullable=False)  # Когда истекает ссылка
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  used_at = Column(DateTime(timezone=True), nullable=True)  # Когда была использована
