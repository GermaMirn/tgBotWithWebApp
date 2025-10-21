import aio_pika
import json
import asyncio
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connection_string = "amqp://admin:admin123@rabbitmq:5672/"
        self.max_retries = 30  # Максимальное количество попыток
        self.retry_delay = 5   # Задержка между попытками в секундах
        self.is_connected = False

    async def connect(self):
        """Установка соединения с RabbitMQ с повторными попытками"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries})")
                self.connection = await aio_pika.connect_robust(self.connection_string)
                self.channel = await self.connection.channel()

                # Объявляем только exchange для отправки
                self.notifications_exchange = await self.channel.declare_exchange(
                    "notifications",
                    aio_pika.ExchangeType.DIRECT,
                    durable=True
                )

                self.is_connected = True
                logger.info("Connected to RabbitMQ successfully")
                return  # Успешное подключение

            except Exception as e:
                logger.warning(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All connection attempts failed")
                    self.is_connected = False
                    # Не поднимаем исключение, чтобы приложение могло работать без RabbitMQ
                    # Можно добавить fallback логику

    async def publish_notification(self, notification_data: Dict[str, Any], routing_key: str):
        """Публикация уведомления в очередь"""
        if not self.is_connected:
            logger.warning("Cannot publish notification: not connected to RabbitMQ")
            return False

        try:
            message_body = json.dumps(notification_data).encode()
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
            # При ошибке публикации можно попытаться восстановить соединение
            await self.reconnect()
            return False

    async def reconnect(self):
        """Повторное подключение при разрыве соединения"""
        logger.info("Attempting to reconnect to RabbitMQ...")
        self.is_connected = False
        await self.connect()

    async def close(self):
        """Закрытие соединения"""
        if self.connection:
            await self.connection.close()
            self.is_connected = False

# Глобальный экземпляр клиента
rabbitmq_client = RabbitMQClient()
