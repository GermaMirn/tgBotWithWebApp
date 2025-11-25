from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import NotificationCRUD
from app.schemas import NotificationCreate, NotificationResponse, UserNotificationSettingsUpdate, ChatIdUpdate, UserNotificationSettingsResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/users/{user_id}", response_model=NotificationResponse)
async def create_notification_by_user_id(
    user_id: str,
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    crud = NotificationCRUD(db)
    return await crud.create_notification(notification_data)

@router.get("/users/{user_id}", response_model=list[NotificationResponse])
async def get_notifications_by_user_id(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    crud = NotificationCRUD(db)
    return await crud.get_user_notifications(user_id, skip, limit)

@router.get("/users/{user_id}/settings", response_model=UserNotificationSettingsResponse)
async def get_notification_settings(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Получение настроек уведомлений пользователя"""
    crud = NotificationCRUD(db)
    return await crud.get_or_create_user_settings(user_id)

@router.patch("/users/{user_id}/settings")
async def update_notification_settings(
    user_id: str,
    settings_update: UserNotificationSettingsUpdate,
    db: AsyncSession = Depends(get_db)
):
    crud = NotificationCRUD(db)
    return await crud.update_user_settings(user_id, settings_update)

@router.post("/users/{user_id}/chat-id")
async def set_user_chat_id(
    user_id: str,
    chat_data: ChatIdUpdate,
    db: AsyncSession = Depends(get_db)
):
    crud = NotificationCRUD(db)
    return await crud.set_user_chat_id(user_id, chat_data.chat_id)

@router.post("/users/{user_id}/notify")
async def create_user_notification(
    user_id: str,
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    """ Создание и отправка уведомления пользователю """
    service = NotificationService(db)

    # Получаем chat_id пользователя
    chat_id = await service.get_user_chat_id(notification_data.user_id)

    if not chat_id:
        raise HTTPException(status_code=400, detail="User chat_id not found")

    # Создаем полные данные уведомления с user_id из URL
    full_notification_data = NotificationCreate(
        **notification_data.dict()
    )

    # Создаем и отправляем уведомление
    notification = await service.create_and_send_notification(full_notification_data, chat_id)

    return {
        "message": "Notification created and sent to queue",
        "notification_id": notification.id,
        "chat_id": chat_id
    }
