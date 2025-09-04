from aiogram import Router, types
from aiogram.filters import Command
from bot.keyboard.webapp import get_webapp_keyboard

router = Router()

@router.message(Command(commands=["start", "help"]))
async def send_welcome(message: types.Message):
  await message.answer(
    "Привет! Нажми кнопку ниже, чтобы открыть Mini App 🚀",
    reply_markup=get_webapp_keyboard()
  )
