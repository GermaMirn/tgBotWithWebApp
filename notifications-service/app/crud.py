from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Notification, UserNotificationSettings
from app.schemas import NotificationCreate, UserNotificationSettingsUpdate

class NotificationCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(self, notification_data: NotificationCreate) -> Notification:
        notification = Notification(**notification_data.dict())
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_user_notifications(self, user_id: str, skip: int = 0, limit: int = 100):
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Notification.created_at.desc())
        )
        return result.scalars().all()

    async def get_or_create_user_settings(self, user_id: str) -> UserNotificationSettings:
        result = await self.db.execute(
            select(UserNotificationSettings)
            .where(UserNotificationSettings.user_id == user_id)
        )
        settings = result.scalar_one_or_none()

        if not settings:
            settings = UserNotificationSettings(user_id=user_id)
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)

        return settings

    async def update_user_settings(self, user_id: str, settings_update: UserNotificationSettingsUpdate) -> UserNotificationSettings:
        settings = await self.get_or_create_user_settings(user_id)

        for field, value in settings_update.dict(exclude_unset=True).items():
            setattr(settings, field, value)

        await self.db.commit()
        await self.db.refresh(settings)
        return settings

    async def set_user_chat_id(self, user_id: str, chat_id: int) -> UserNotificationSettings:
        settings = await self.get_or_create_user_settings(user_id)
        settings.chat_id = chat_id
        await self.db.commit()
        await self.db.refresh(settings)
        return settings
