export interface NotificationSettings {
  id: number;
  user_id: string;
  chat_id: number | null;
  telegram_enabled: boolean;
  email_enabled: boolean;
  sms_enabled: boolean;
  push_enabled: boolean;
  lesson_reminders: boolean;
  group_notifications: boolean;
  system_messages: boolean;
  marketing_messages: boolean;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface NotificationSettingsStatus {
  notifications_enabled: boolean;
  has_chat_id: boolean;
  settings: NotificationSettings;
}
