from aiogram import Dispatcher
from bot.handlers import start

def register_routers(dp: Dispatcher):
  dp.include_router(start.router)
