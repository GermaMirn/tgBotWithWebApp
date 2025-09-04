from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import enum

class NotificationType(str, enum.Enum):
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

class NotificationStatus(str, enum.Enum):
  PENDING = "pending"
  SENT = "sent"
  DELIVERED = "delivered"
  READ = "read"
  FAILED = "failed"

class NotificationChannel(str, enum.Enum):
  TELEGRAM = "telegram"
  EMAIL = "email"
  SMS = "sms"
  PUSH = "push"

class NotificationBase(BaseModel):
  id: int
  recipient_telegram_id: int
  notification_type: NotificationType
  status: NotificationStatus
  channel: NotificationChannel
  title: str
  message: str
  data: Optional[Dict[str, Any]] = None
  scheduled_at: Optional[datetime] = None
  sent_at: Optional[datetime] = None
  delivered_at: Optional[datetime] = None
  read_at: Optional[datetime] = None
  created_at: datetime
  updated_at: Optional[datetime] = None
  lesson_id: Optional[int] = None
  group_id: Optional[int] = None
  sender_telegram_id: Optional[int] = None

class NotificationCreate(BaseModel):
  recipient_telegram_id: int
  notification_type: NotificationType
  channel: NotificationChannel = NotificationChannel.TELEGRAM
  title: str
  message: str
  data: Optional[Dict[str, Any]] = None
  scheduled_at: Optional[datetime] = None
  lesson_id: Optional[int] = None
  group_id: Optional[int] = None
  sender_telegram_id: Optional[int] = None

class UserNotificationSettings(BaseModel):
  id: int
  user_telegram_id: int
  telegram_enabled: bool = True
  email_enabled: bool = False
  sms_enabled: bool = False
  push_enabled: bool = False
  lesson_reminders: bool = True
  group_notifications: bool = True
  system_messages: bool = True
  marketing_messages: bool = False
  quiet_hours_start: Optional[str] = None
  quiet_hours_end: Optional[str] = None
  created_at: datetime
  updated_at: Optional[datetime] = None

class NotificationSettingsUpdate(BaseModel):
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
