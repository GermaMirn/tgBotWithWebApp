from aiogram import Router, types
from aiogram.filters import Command
from src.bot.keyboard.webapp import get_webapp_keyboard

router = Router()

@router.message(Command(commands=["start", "help"]))
async def send_welcome(message: types.Message):
    welcome_text = (
        "Привет! Нажми кнопку ниже, чтобы открыть Mini App 🚀\n\n"
        "💡 Для получения уведомлений используйте команду /notification"
    )

    await message.answer(
        welcome_text,
        reply_markup=get_webapp_keyboard()
    )
