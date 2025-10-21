from aiogram import Dispatcher
from src.bot.handlers import start, notification

def register_routers(dp: Dispatcher):
  dp.include_router(start.router)
  dp.include_router(notification.router)
