import aio_pika
import json
import logging
from aiogram import Bot
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TelegramConsumer:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.connection = None
        self.channel = None
        self.connection_string = "amqp://admin:admin123@rabbitmq:5672/"
        self.max_retries = 30
        self.retry_delay = 5

    async def connect(self):
        """Подключение к RabbitMQ и начало потребления сообщений"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries})")
                self.connection = await aio_pika.connect_robust(self.connection_string)
                self.channel = await self.connection.channel()

                # Устанавливаем QoS для обработки одного сообщения за раз
                await self.channel.set_qos(prefetch_count=1)

                # Объявляем exchange и очередь
                exchange = await self.channel.declare_exchange(
                    "notifications",
                    aio_pika.ExchangeType.DIRECT,
                    durable=True
                )

                queue = await self.channel.declare_queue(
                    "telegram_notifications",
                    durable=True
                )

                # Привязываем очередь к exchange с routing_key "telegram"
                await queue.bind(exchange, routing_key="telegram")

                logger.info("Connected to RabbitMQ successfully, starting to consume messages...")

                # Начинаем потребление сообщений
                await queue.consume(self.process_message)
                return

            except Exception as e:
                logger.warning(f"Failed to connect to RabbitMQ (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    import asyncio
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All connection attempts to RabbitMQ failed")
                    raise

    async def process_message(self, message: aio_pika.IncomingMessage):
        """Обработка входящих сообщений из RabbitMQ"""
        async with message.process():
            try:
                notification_data = json.loads(message.body.decode())
                await self.send_telegram_message(notification_data)
                logger.info(f"Successfully processed notification: {notification_data.get('notification_id')}")

            except Exception as e:
                logger.error(f"Failed to process message: {e}")
                # Можно добавить логику для dead letter queue или повторной обработки

    async def send_telegram_message(self, data: Dict[str, Any]):
        """Отправка сообщения через Telegram Bot API"""
        try:
            chat_id = data.get("chat_id")
            title = data.get("title", "")
            message_text = data.get("message", "")
            notification_id = data.get("notification_id")

            if not chat_id:
                logger.error("No chat_id in notification data")
                return

            # Форматируем сообщение
            text = f"<b>{title}</b>\n\n{message_text}"

            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML"
            )

            logger.info(f"Telegram message sent to chat {chat_id} for notification {notification_id}")

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            # Обработка различных ошибок Telegram API
            if "chat not found" in str(e).lower():
                logger.warning(f"Chat {chat_id} not found, user might have blocked the bot")
            elif "bot was blocked" in str(e).lower():
                logger.warning(f"Bot was blocked by user {chat_id}")

    async def close(self):
        """Закрытие соединения"""
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")
