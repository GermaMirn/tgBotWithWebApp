from fastapi import APIRouter, HTTPException, Depends
from app.services.notification_service import notification_service
from app.core.auth import get_current_user, get_current_user_telegram_id
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    UserNotificationSettingsUpdate,
    UserNotificationSettingsResponse,
    ChatIdUpdate,
    NotificationSettingsStatus
)
from typing import List

router = APIRouter()

# Эндпоинты для уведомлений
@router.post("/users/{user_id}", response_model=NotificationResponse)
async def create_notification(
    user_id: str,
    notification_data: NotificationCreate,
    current_user: dict = Depends(get_current_user)
):
    """Создание уведомления для пользователя"""
    return await notification_service.create_notification(user_id, notification_data)

@router.get("/users/{user_id}", response_model=List[NotificationResponse])
async def get_user_notifications(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Получение уведомлений пользователя"""
    return await notification_service.get_user_notifications(user_id, skip, limit)

@router.get("/users/{user_id}/settings", response_model=UserNotificationSettingsResponse)
async def get_user_settings(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Получение настроек уведомлений пользователя"""
    return await notification_service.get_user_settings(user_id)

@router.patch("/users/{user_id}/settings", response_model=UserNotificationSettingsResponse)
async def update_user_settings(
    user_id: str,
    settings_update: UserNotificationSettingsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Обновление настроек уведомлений пользователя"""
    return await notification_service.update_user_settings(user_id, settings_update)

@router.post("/users/{user_id}/chat-id", response_model=UserNotificationSettingsResponse)
async def set_user_chat_id(
    user_id: str,
    chat_data: ChatIdUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Установка chat_id для пользователя"""
    return await notification_service.set_user_chat_id(user_id, chat_data.chat_id)

@router.get("/users/{user_id}/status", response_model=NotificationSettingsStatus)
async def get_notification_status(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Получение статуса уведомлений пользователя"""
    return await notification_service.get_notification_status(user_id)

# Специальные эндпоинты для бота и интеграций
@router.post("/register-chat")
async def register_chat_by_telegram(
    telegram_id: int,
    chat_id: int
):
    """Регистрация chat_id по telegram_id (для бота)"""
    try:
        # Получаем пользователя по telegram_id из auth-service
        user = await get_current_user_telegram_id(telegram_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Устанавливаем chat_id в notification-service
        return await notification_service.set_user_chat_id(user["id"], chat_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error registering chat: {str(e)}")

@router.post("/users/{user_id}/notify")
async def send_notification(
    user_id: str,
    notification_data: NotificationCreate,
    # current_user: dict = Depends(get_current_user)
):
    """Создание и отправка уведомления пользователю через RabbitMQ"""
    try:
        result = await notification_service.send_notification(user_id, notification_data)
        return {
            "message": "Notification sent successfully",
            "notification_id": result.get("notification_id"),
            "chat_id": result.get("chat_id")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")
