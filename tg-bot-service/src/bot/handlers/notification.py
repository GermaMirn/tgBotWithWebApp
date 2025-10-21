import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import os

router = Router()

# Используем имя сервиса в Docker сети
BFF_URL = os.getenv("BFF_URL", "http://bff-service:8000/api")

async def register_chat_for_notifications(telegram_id: int, chat_id: int, username: str = "", full_name: str = ""):
    """Регистрация chat_id для уведомлений через BFF"""
    try:
        async with aiohttp.ClientSession() as session:
            # Сначала пытаемся зарегистрировать пользователя через miniapp endpoint
            # Это создаст пользователя, если его нет, и установит chat_id
            miniapp_data = {
                "id": telegram_id,
                "username": username,
                "full_name": full_name,
                "chat_id": chat_id
            }

            async with session.post(f"{BFF_URL}/auth/miniapp", json=miniapp_data) as response:
                print(f"Miniapp registration response status: {response.status}")

                if response.status == 200:
                    response_data = await response.json()
                    print(f"Miniapp registration successful: {response_data}")
                    return True, response_data
                elif response.status == 502:
                    # Если пользователь уже существует, попробуем установить chat_id напрямую
                    try:
                        direct_response = await session.post(
                            f"{BFF_URL}/notification/register-chat",
                            params={"telegram_id": telegram_id, "chat_id": chat_id}
                        )
                        if direct_response.status == 200:
                            direct_data = await direct_response.json()
                            print(f"Direct chat_id registration successful: {direct_data}")
                            return True, direct_data
                        else:
                            error_text = await direct_response.text()
                            print(f"Direct registration failed: {direct_response.status}, Error: {error_text}")
                            return False, error_text
                    except Exception as direct_e:
                        print(f"Direct registration error: {direct_e}")
                        return False, str(direct_e)
                else:
                    error_text = await response.text()
                    print(f"Miniapp registration failed: {response.status}, Error: {error_text}")
                    return False, error_text

    except Exception as e:
        print(f"Error registering chat for notifications: {e}")
        import traceback
        traceback.print_exc()
        return False, str(e)

@router.message(Command(commands=["notification", "notifications"]))
async def handle_notification_command(message: types.Message):
    """Обработка команды /notification для регистрации уведомлений"""
    user = message.from_user

    # Регистрируем chat_id для уведомлений
    success, response_data = await register_chat_for_notifications(
        telegram_id=user.id,
        chat_id=message.chat.id,
        username=user.username or "",
        full_name=f"{user.first_name} {user.last_name or ''}".strip()
    )

    if success:
        response_text = (
            "🔔 <b>Уведомления активированы!</b>\n\n"
            "✅ Ваш чат зарегистрирован для получения уведомлений.\n"
            "📱 Теперь вы можете управлять настройками уведомлений в Mini App.\n\n"
            "💡 <i>Откройте Mini App, чтобы настроить типы уведомлений, которые вы хотите получать.</i>"
        )

        await message.answer(
            response_text,
            parse_mode="HTML"
        )
    else:
        response_text = (
            "❌ <b>Ошибка регистрации уведомлений</b>\n\n"
            f"Произошла ошибка: {response_data}\n\n"
            "Попробуйте позже или обратитесь в поддержку."
        )

        await message.answer(
            response_text,
            parse_mode="HTML"
        )

@router.message(Command(commands=["notifications_off", "stop_notifications"]))
async def handle_stop_notifications_command(message: types.Message):
  """Обработка команды для отключения уведомлений"""
  user = message.from_user

  try:
      async with aiohttp.ClientSession() as session:
          # Получаем настройки пользователя
          async with session.get(f"{BFF_URL}/notification/users/{user.id}/settings") as response:
              if response.status == 200:
                  settings = await response.json()

                  # Обновляем настройки, отключая уведомления
                  update_data = {
                      "telegram_enabled": False
                  }

                  async with session.patch(
                      f"{BFF_URL}/notification/users/{user.id}/settings",
                      json=update_data
                  ) as update_response:
                      if update_response.status == 200:
                        response_text = (
                          "🔕 <b>Уведомления отключены</b>\n\n"
                          "✅ Вы больше не будете получать уведомления в Telegram.\n"
                          "📱 Вы можете включить их снова в настройках Mini App."
                        )
                      else:
                        response_text = "❌ Ошибка при отключении уведомлений."
              else:
                  response_text = "❌ Пользователь не найден."

  except Exception as e:
    print(f"Error disabling notifications: {e}")
    response_text = "❌ Произошла ошибка при отключении уведомлений."

  await message.answer(response_text, parse_mode="HTML")
