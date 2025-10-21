from app.core.rabbitmq import rabbitmq_client
from app.crud import NotificationCRUD
from app.schemas import NotificationCreate

class NotificationService:
    def __init__(self, db):
        self.db = db
        self.crud = NotificationCRUD(db)

    async def create_and_send_notification(self, notification_data: NotificationCreate, user_chat_id: int = None):
        """Создает уведомление и отправляет в RabbitMQ"""
        # Сохраняем уведомление в БД
        notification = await self.crud.create_notification(notification_data)

        # Получаем настройки пользователя для проверки telegram_enabled
        user_settings = await self.crud.get_or_create_user_settings(str(notification.user_id))

        # Проверяем, включены ли уведомления в Telegram и есть ли chat_id
        if user_chat_id and user_settings and user_settings.telegram_enabled:
            message_data = {
                "notification_id": notification.id,
                "user_id": str(notification.user_id),
                "chat_id": user_chat_id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type.value,
                "created_at": notification.created_at.isoformat()
            }

            await rabbitmq_client.publish_notification(message_data, routing_key="telegram")
            print(f"Notification {notification.id} published to RabbitMQ for user {user_chat_id}")
        else:
            if not user_chat_id:
                print(f"Notification {notification.id} not sent: no chat_id for user {notification.user_id}")
            elif not user_settings or not user_settings.telegram_enabled:
                print(f"Notification {notification.id} not sent: telegram notifications disabled for user {notification.user_id}")

        return notification

    async def get_user_chat_id(self, user_id: str) -> int:
        """Получает chat_id пользователя для отправки уведомлений"""
        settings = await self.crud.get_or_create_user_settings(user_id)
        return settings.chat_id if settings else None
