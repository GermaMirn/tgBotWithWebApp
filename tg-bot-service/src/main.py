import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from src.config import Config
from src.bot.routers.routers import register_routers
from src.bot.consumers.telegram_consumer import TelegramConsumer

bot = Bot(
  token=Config.BOT_TOKEN,
  default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def main():
  register_routers(dp)
  await bot.delete_webhook(drop_pending_updates=True)

  consumer = TelegramConsumer(bot)

  try:
    # Запускаем подключение к RabbitMQ
    await consumer.connect()

    # Запускаем поллинг бота и consumer параллельно
    await asyncio.gather(
        dp.start_polling(bot),
        # Держим consumer активным
        asyncio.create_task(asyncio.sleep(float('inf')))
    )
  except Exception as e:
    print(f"Error in main: {e}")
  finally:
    await consumer.close()

if __name__ == '__main__':
  asyncio.run(main())
