from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud, schemas
from app.utils.auth import get_current_user
from app.core.rabbitmq import rabbitmq_client
import secrets
from datetime import datetime, timedelta, timezone
from app.utils.auth import create_access_token
import os
import logging
import httpx

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/role")

def generate_token() -> str:
    """Генерирует уникальный токен для ссылки"""
    return secrets.token_urlsafe(32)

@router.post("/admin/role-switch-links", response_model=schemas.RoleSwitchLinkResponse)
async def create_role_switch_link(
    link_data: schemas.RoleSwitchLinkCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Создает ссылку для переключения роли (только для админов)
    """
    # Проверяем, что текущий пользователь - админ
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can create role switch links"
        )

    # Проверяем валидность целевой роли
    if link_data.target_role not in ["teacher", "student"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid target role. Must be 'teacher' or 'student'"
        )

    # Генерируем токен и время истечения
    token = generate_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=link_data.expires_in_hours)

    # Создаем ссылку
    link = await crud.create_role_switch_link(
        db=db,
        target_role=link_data.target_role,
        target_user_id=link_data.target_user_id,
        target_user_name=link_data.target_user_name,
        created_by=current_user.get("sub"),  # ID админа
        token=token,
        expires_at=expires_at
    )

    # Отправляем уведомление в Telegram, если создается ссылка для преподавателя
    if link_data.target_role == "teacher" and link_data.target_user_id:
        try:
            # Получаем пользователя для получения telegram_id
            target_user = await crud.get_user(db, link_data.target_user_id)
            if target_user and target_user.telegram_id:
                # Формируем URL ссылки
                frontend_url = os.getenv("FRONTEND_URL", "https://unseemly-adorable-razorbill.cloudpub.ru")
                switch_url = f"{frontend_url}/role-switch/{token}"

                # Формируем сообщение
                title = "🎓 Приглашение стать преподавателем"
                message = (
                    f"Здравствуйте, {target_user.full_name}!\n\n"
                    f"Ваша ссылка для того, чтобы стать преподавателем в нашей студии иностранных языков:\n"
                    f"{switch_url}\n\n"
                    f"Ссылка действительна для 1 перехода на страницу.\n"
                    f"Срок действия: {link_data.expires_in_hours} {'час' if link_data.expires_in_hours == 1 else 'часов'}"
                )

                # Отправляем уведомление через RabbitMQ
                notification_data = {
                    "chat_id": target_user.telegram_id,
                    "title": title,
                    "message": message,
                    "notification_type": "role_switch",
                    "user_id": str(target_user.id),
                    "telegram_id": target_user.telegram_id
                }

                await rabbitmq_client.publish_notification(notification_data, routing_key="telegram")
                logger.info(f"Role switch notification sent to user {target_user.telegram_id}")
        except Exception as e:
            # Логируем ошибку, но не прерываем создание ссылки
            logger.error(f"Failed to send role switch notification: {e}")

    return link

@router.get("/admin/role-switch-links", response_model=list[schemas.RoleSwitchLinkResponse])
async def get_role_switch_links(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Получает список всех ссылок для переключения ролей (только для админов)
    """
    # Проверяем, что текущий пользователь - админ
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can view role switch links"
        )

    links = await crud.get_all_role_switch_links(db)
    return links

@router.delete("/admin/role-switch-links/{link_id}")
async def delete_role_switch_link(
    link_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаляет ссылку для переключения роли (только для админов)
    """
    # Проверяем, что текущий пользователь - админ
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can delete role switch links"
        )

    # Удаляем ссылку
    await crud.delete_role_switch_link(db, link_id)
    return {"message": "Link deleted successfully"}

@router.post("/admin/switch-user-role")
async def switch_user_role(
    switch_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Прямое переключение роли пользователя (только для админов)
    """
    # Проверяем, что текущий пользователь - админ
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can switch user roles"
        )

    target_user_id = switch_data.get("target_user_id")
    target_role = switch_data.get("target_role")

    if not target_user_id or not target_role:
        raise HTTPException(
            status_code=400,
            detail="target_user_id and target_role are required"
        )

    # Получаем пользователя
    target_user = await crud.get_user(db, target_user_id)
    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="Target user not found"
        )

    # Проверяем, что пользователь не пытается переключиться на ту же роль
    if target_user.role == target_role:
        raise HTTPException(
            status_code=400,
            detail=f"User is already a {target_role}"
        )

    # Обновляем роль пользователя
    updated_user = await crud.update_user_role(
        db,
        target_user_id,
        target_role
    )

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Удаляем старый профиль при переключении ролей
    try:
        if target_role == 'teacher':
            # Если переключаемся на учителя, удаляем профиль студента
            await crud.delete_student_profile(db, target_user.telegram_id)
            # Создаем профиль учителя в teachers-service, если его еще нет
            await crud.create_teacher_profile_if_not_exists(db, target_user.telegram_id)
        elif target_role == 'student':
            # Если переключаемся на студента, удаляем профиль учителя
            await crud.delete_teacher_profile(db, target_user.telegram_id)
    except Exception as e:
        # Логируем ошибку, но не прерываем процесс
        print(f"Warning: Could not delete old profile or create teacher profile: {e}")

    return {
        "success": True,
        "message": f"Successfully switched {target_user.full_name} to {target_role} role",
        "user": {
            "id": str(target_user.id),
            "full_name": target_user.full_name,
            "role": target_role
        }
    }

@router.post("/role-switch", response_model=schemas.RoleSwitchResponse)
async def switch_role(
    switch_data: schemas.RoleSwitchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Переключает роль пользователя по токену ссылки
    """
    # Получаем ссылку по токену
    link = await crud.get_role_switch_link_by_token(db, switch_data.token)

    if not link:
        raise HTTPException(
            status_code=404,
            detail="Invalid or expired link"
        )

    # Проверяем, не использована ли уже ссылка
    if link.is_used:
        raise HTTPException(
            status_code=400,
            detail="Link has already been used"
        )

    # Проверяем, не истекла ли ссылка
    if datetime.now(timezone.utc) > link.expires_at:
        raise HTTPException(
            status_code=400,
            detail="Link has expired"
        )

    # Проверяем, что ссылка предназначена для конкретного пользователя
    if not link.target_user_id:
        raise HTTPException(
            status_code=400,
            detail="Link is not associated with a specific user"
        )

    # Получаем пользователя, которому нужно изменить роль
    target_user = await crud.get_user(db, link.target_user_id)
    if not target_user:
        raise HTTPException(
            status_code=404,
            detail="Target user not found"
        )

    # Проверяем, что пользователь не пытается переключиться на ту же роль
    if target_user.role == link.target_role:
        raise HTTPException(
            status_code=400,
            detail=f"User is already a {link.target_role}"
        )

    # Обновляем роль целевого пользователя
    updated_user = await crud.update_user_role(
        db,
        link.target_user_id,
        link.target_role
    )

    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Удаляем старый профиль (учителя или студента) при переключении ролей
    try:
        if link.target_role == 'teacher':
            # Если переключаемся на учителя, удаляем профиль студента
            await crud.delete_student_profile(db, target_user.telegram_id)
            # Создаем профиль учителя в teachers-service, если его еще нет
            await crud.create_teacher_profile_if_not_exists(db, target_user.telegram_id)
        elif link.target_role == 'student':
            # Если переключаемся на студента, удаляем профиль учителя
            await crud.delete_teacher_profile(db, target_user.telegram_id)
    except Exception as e:
        print(f"Warning: Could not delete old profile or create teacher profile: {e}")

    # Отмечаем ссылку как использованную
    await crud.mark_role_switch_link_as_used(
        db,
        str(link.id),
        str(link.target_user_id)
    )

    # Создаем новый JWT токен с обновленной ролью для целевого пользователя
    new_token = create_access_token(
        data={"sub": str(link.target_user_id), "telegram_id": target_user.telegram_id},
        role=link.target_role
    )

    return schemas.RoleSwitchResponse(
        success=True,
        message=f"Successfully switched {target_user.full_name} to {link.target_role} role",
        new_role=link.target_role,
        access_token=new_token
    )

@router.get("/role-switch/validate/{token}")
async def validate_role_switch_link(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Проверяет валидность ссылки для переключения роли
    """
    link = await crud.get_role_switch_link_by_token(db, token)

    if not link:
        raise HTTPException(
            status_code=404,
            detail="Invalid link"
        )

    if link.is_used:
        raise HTTPException(
            status_code=400,
            detail="Link has already been used"
        )

    if datetime.now(timezone.utc) > link.expires_at:
        raise HTTPException(
            status_code=400,
            detail="Link has expired"
        )

    return {
        "valid": True,
        "target_role": link.target_role,
        "expires_at": link.expires_at.isoformat()
    }
