from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any
from uuid import UUID
import enum

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

class NotificationBase(BaseModel):
    user_id: UUID
    notification_type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None
    lesson_id: Optional[int] = None
    group_id: Optional[int] = None
    sender_telegram_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    status: NotificationStatus
    channel: NotificationChannel
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserNotificationSettingsBase(BaseModel):
    chat_id: Optional[int] = None
    telegram_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    lesson_reminders: Optional[bool] = None
    group_notifications: Optional[bool] = None
    system_messages: Optional[bool] = None
    marketing_messages: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

class UserNotificationSettingsCreate(BaseModel):
    user_id: UUID
    chat_id: Optional[int] = None

class UserNotificationSettingsUpdate(UserNotificationSettingsBase):
    pass

class UserNotificationSettingsResponse(UserNotificationSettingsBase):
    id: int
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ChatIdUpdate(BaseModel):
    chat_id: int

class NotificationLogBase(BaseModel):
    event: str
    details: Optional[str] = None
    error_message: Optional[str] = None

class NotificationLogCreate(NotificationLogBase):
    notification_id: int

class NotificationLogResponse(NotificationLogBase):
    id: int
    notification_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Схемы для API ответов
class NotificationSettingsStatus(BaseModel):
    notifications_enabled: bool
    has_chat_id: bool
    settings: UserNotificationSettingsResponse

class NeedChatIdResponse(BaseModel):
    status: str = "need_chat_id"
    message: str = "Сначала напишите боту для активации уведомлений"

class SuccessResponse(BaseModel):
    status: str = "success"
