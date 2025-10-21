from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from sqlalchemy.dialects.postgresql import UUID

class NotificationType(enum.Enum):
  LESSON_REMINDER = "lesson_reminder"
  LESSON_CANCELLED = "lesson_cancelled"
  LESSON_RESCHEDULED = "lesson_rescheduled"
  GROUP_INVITATION = "group_invitation"
  GROUP_JOINED = "group_joined"
  GROUP_LEFT = "group_left"
  ASSIGNMENT_DUE = "assignment_due"
  GRADE_RECEIVED = "grade_received"
  SYSTEM_MESSAGE = "system_message"
  TEACHER_MESSAGE = "teacher_message"

class NotificationStatus(enum.Enum):
  PENDING = "pending"
  SENT = "sent"
  DELIVERED = "delivered"
  READ = "read"
  FAILED = "failed"

class NotificationChannel(enum.Enum):
  TELEGRAM = "telegram"
  EMAIL = "email"
  SMS = "sms"
  PUSH = "push"

class Notification(Base):
  __tablename__ = "notifications"

  id = Column(Integer, primary_key=True, index=True)

  # Получатель
  user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

  # Тип и статус
  notification_type = Column(Enum(NotificationType), nullable=False)
  status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
  channel = Column(Enum(NotificationChannel), default=NotificationChannel.TELEGRAM)

  # Содержание
  title = Column(String(255), nullable=False)
  message = Column(Text, nullable=False)
  data = Column(JSON, nullable=True)  # Дополнительные данные

  # Время
  scheduled_at = Column(DateTime(timezone=True), nullable=True)
  sent_at = Column(DateTime(timezone=True), nullable=True)
  delivered_at = Column(DateTime(timezone=True), nullable=True)
  read_at = Column(DateTime(timezone=True), nullable=True)

  # Временные метки
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())

  # Связи с другими сервисами
  lesson_id = Column(Integer, nullable=True)  # ID занятия (если связано с занятием)
  group_id = Column(Integer, nullable=True)  # ID группы (если связано с группой)
  sender_telegram_id = Column(BigInteger, nullable=True)  # ID отправителя

class UserNotificationSettings(Base):
  __tablename__ = "user_notification_settings"

  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
  chat_id = Column(BigInteger, nullable=True, index=True)

  # Настройки по каналам
  telegram_enabled = Column(Boolean, default=True)
  email_enabled = Column(Boolean, default=False)
  sms_enabled = Column(Boolean, default=False)
  push_enabled = Column(Boolean, default=False)

  # Настройки по типам уведомлений
  lesson_reminders = Column(Boolean, default=True)
  group_notifications = Column(Boolean, default=True)
  system_messages = Column(Boolean, default=True)
  marketing_messages = Column(Boolean, default=False)

  # Время тишины
  quiet_hours_start = Column(String(5), nullable=True)  # "22:00"
  quiet_hours_end = Column(String(5), nullable=True)  # "08:00"

  # Временные метки
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class NotificationLog(Base):
  __tablename__ = "notification_logs"

  id = Column(Integer, primary_key=True, index=True)
  notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)

  # Лог события
  event = Column(String(50), nullable=False)  # "sent", "delivered", "read", "failed"
  details = Column(Text, nullable=True)  # Детали события
  error_message = Column(Text, nullable=True)  # Сообщение об ошибке

  # Временные метки
  created_at = Column(DateTime(timezone=True), server_default=func.now())
