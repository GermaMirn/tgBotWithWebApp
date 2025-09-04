import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import Config
from bot.routers.routers import register_routers

bot = Bot(
  token=Config.BOT_TOKEN,
  default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

async def main():
  register_routers(dp)
  await bot.delete_webhook(drop_pending_updates=True)
  await dp.start_polling(bot)

if __name__ == '__main__':
  asyncio.run(main())
