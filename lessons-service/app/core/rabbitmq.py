import aio_pika
import json
import asyncio
from typing import Any, Dict, Optional
import logging
import os
import httpx

logger = logging.getLogger(__name__)

NOTIFICATIONS_SERVICE_URL = os.getenv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8007")

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connection_string = os.getenv(
            "RABBITMQ_URL",
            "amqp://admin:admin123@rabbitmq:5672/"
        )
        self.max_retries = 30
        self.retry_delay = 5
        self.is_connected = False
        self.notifications_exchange = None

    async def connect(self):
        """Установка соединения с RabbitMQ с повторными попытками"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries})")
                self.connection = await aio_pika.connect_robust(self.connection_string)
                self.channel = await self.connection.channel()

                # Объявляем exchange для отправки уведомлений
                self.notifications_exchange = await self.channel.declare_exchange(
                    "notifications",
                    aio_pika.ExchangeType.DIRECT,
                    durable=True
                )

                self.is_connected = True
                logger.info("Connected to RabbitMQ successfully")
                return

            except Exception as e:
                logger.warning(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All connection attempts failed")
                    self.is_connected = False

    async def _check_notification_enabled(self, user_id: Optional[str]) -> bool:
        """Проверяет, включены ли уведомления для пользователя"""
        if not user_id:
            logger.warning(f"Empty user_id provided, skipping notification check")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{NOTIFICATIONS_SERVICE_URL}/notifications/users/{user_id}/settings",
                    timeout=5
                )
                if response.status_code == 200:
                    settings = response.json()
                    telegram_enabled = settings.get("telegram_enabled", True)
                    logger.info(f"Notification check for user {user_id}: telegram_enabled={telegram_enabled}")
                    return telegram_enabled
                else:
                    logger.warning(f"Could not get notification settings for user {user_id}, status={response.status_code}, defaulting to disabled")
                    return False
        except httpx.HTTPError as e:
            logger.error(f"HTTP error checking notification settings for user {user_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to check notification settings for user {user_id}: {e}")
            return False

    async def publish_notification(self, notification_data: Dict[str, Any], routing_key: str = "telegram", check_enabled: bool = True):
        """Публикация уведомления в очередь с проверкой настроек"""
        # Проверяем настройки уведомлений перед отправкой
        if check_enabled:
            user_id = notification_data.get("user_id") or notification_data.get("teacher_telegram_id")
            if user_id:
                # Если user_id - это telegram_id, нужно получить user_id из auth-service
                if isinstance(user_id, int) or (isinstance(user_id, str) and user_id.isdigit()):
                    # Это telegram_id, нужно получить user_id
                    try:
                        async with httpx.AsyncClient() as client:
                            auth_url = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8002")
                            response = await client.get(
                                f"{auth_url}/auth/user-by-telegram/{user_id}",
                                timeout=5
                            )
                            if response.status_code == 200:
                                user_data = response.json()
                                user_id = str(user_data.get("id"))
                            else:
                                logger.warning(f"Could not get user_id for telegram_id {user_id}")
                                return False
                    except Exception as e:
                        logger.error(f"Failed to get user_id for telegram_id {user_id}: {e}")
                        return False

                notifications_enabled = await self._check_notification_enabled(str(user_id))
                if not notifications_enabled:
                    logger.info(f"Notifications disabled for user {user_id}, skipping notification publish")
                    return False

        if not self.is_connected:
            logger.warning("Cannot publish notification: not connected to RabbitMQ")
            # Пытаемся переподключиться
            await self.connect()
            if not self.is_connected:
                return False

        try:
            message_body = json.dumps(notification_data, ensure_ascii=False).encode('utf-8')
            message = aio_pika.Message(
                body=message_body,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await self.notifications_exchange.publish(
                message,
                routing_key=routing_key
            )
            logger.info(f"Notification published to {routing_key} queue")
            return True
        except Exception as e:
            logger.error(f"Failed to publish notification: {e}")
            return False

    async def close(self):
        """Закрытие соединения"""
        if self.connection:
            await self.connection.close()
            self.is_connected = False

# Глобальный экземпляр клиента
rabbitmq_client = RabbitMQClient()

