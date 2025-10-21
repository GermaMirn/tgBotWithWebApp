import httpx
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    UserNotificationSettingsUpdate,
    UserNotificationSettingsResponse,
    ChatIdUpdate,
    NotificationSettingsStatus
)
from typing import List, Optional

NOTIFICATION_SERVICE_URL = "http://notifications-service:8007"

class NotificationService:
    def __init__(self):
        self.base_url = NOTIFICATION_SERVICE_URL

    async def create_notification(self, user_id: str, notification_data: NotificationCreate) -> NotificationResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/notifications/users/{user_id}",
                json=notification_data.dict()
            )
            response.raise_for_status()
            return response.json()

    async def send_notification(self, user_id: str, notification_data: NotificationCreate) -> dict:
        """Отправка уведомления пользователю через notification-service"""
        # Преобразуем данные в dict и конвертируем enum в строку
        data_dict = notification_data.dict()

        if 'user_id' in data_dict:
            data_dict['user_id'] = str(data_dict['user_id'])

        # Конвертируем NotificationType enum в строку
        if 'notification_type' in data_dict and hasattr(data_dict['notification_type'], 'value'):
            data_dict['notification_type'] = data_dict['notification_type'].value

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/notifications/users/{user_id}/notify",
                json=data_dict
            )
            response.raise_for_status()
            return response.json()

    async def get_user_notifications(self, user_id: str, skip: int = 0, limit: int = 100) -> List[NotificationResponse]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/notifications/users/{user_id}",
                params={"skip": skip, "limit": limit}
            )
            response.raise_for_status()
            return response.json()

    async def get_user_settings(self, user_id: str) -> UserNotificationSettingsResponse:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/notifications/users/{user_id}/settings"
            )
            response.raise_for_status()
            return response.json()

    async def update_user_settings(self, user_id: str, settings_update: UserNotificationSettingsUpdate) -> UserNotificationSettingsResponse:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/notifications/users/{user_id}/settings",
                json=settings_update.dict(exclude_unset=True)
            )
            response.raise_for_status()
            return response.json()

    async def set_user_chat_id(self, user_id: str, chat_id: int) -> UserNotificationSettingsResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/notifications/users/{user_id}/chat-id",
                json={"chat_id": chat_id}
            )
            response.raise_for_status()
            return response.json()

    async def get_notification_status(self, user_id: str) -> NotificationSettingsStatus:
        """Получить статус уведомлений для пользователя"""
        settings = await self.get_user_settings(user_id)
        return NotificationSettingsStatus(
            notifications_enabled=settings.telegram_enabled,
            has_chat_id=bool(settings.chat_id),
            settings=settings
        )

# Создаем экземпляр сервиса
notification_service = NotificationService()
