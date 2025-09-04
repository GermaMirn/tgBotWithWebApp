from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

def get_webapp_keyboard():
  return ReplyKeyboardMarkup(
    keyboard=[
      [KeyboardButton(
        text="Открыть Mini App 🚀",
        web_app=WebAppInfo(url="https://initially-heuristic-margay.cloudpub.ru/")
      )]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
  )
