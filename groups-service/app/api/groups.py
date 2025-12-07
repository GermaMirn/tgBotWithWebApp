from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud
from app.schemas import GroupCreate, GroupRead, GroupUpdate, AddMemberRequest, InvitationCreateRequest, GetGroup
from typing import List, Optional
from app.utils.auth import get_current_user
from app.core.rabbitmq import rabbitmq_client
from app.models import GroupInvitation
from sqlalchemy import select
from datetime import datetime, timezone
import httpx
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

STUDENTS_SERVICE_URL = "http://students-service:8004"
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8002")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://unseemly-adorable-razorbill.cloudpub.ru")

@router.post("", response_model=GroupRead, status_code=201)
async def create_group(
  group: GroupCreate,
  db: AsyncSession = Depends(get_db),
  current_user=Depends(get_current_user)
):
  telegram_id = current_user["telegram_id"]
  # Создаём группу в своей БД
  new_group = await crud.create_group(db, group, telegram_id)

  # Теперь уведомляем students-service
  try:
    async with httpx.AsyncClient() as client:
      await client.post(
        f"{STUDENTS_SERVICE_URL}/groups",
        json={"id": new_group.id},
        timeout=5.0
      )
  except Exception as e:
    print(f"Failed to notify students-service: {e}")

  return new_group

@router.get("", response_model=List[GroupRead])
async def get_groups(db: AsyncSession = Depends(get_db)):
  return await crud.get_groups(db)

@router.get("/teacher", response_model=List[GroupRead])
async def get_teacher_groups(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
  telegram_id = current_user["telegram_id"]
  groups = await crud.get_groups_by_teacher(db, telegram_id)
  return groups

@router.get("/student", response_model=List[GroupRead])
async def get_student_groups(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
  telegram_id = current_user["telegram_id"]
  groups = await crud.get_groups_by_student(db, telegram_id)
  return groups

@router.get("/{group_id}", response_model=GetGroup)
async def get_group_by_id(group_id: int, db: AsyncSession = Depends(get_db)):
  group = await crud.get_group(db, group_id)
  if not group:
    raise HTTPException(status_code=404, detail="Group not found")
  return group

@router.delete("/{group_id}")
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
  role = current_user["role"]
  telegram_id = current_user["telegram_id"]
  group = await crud.get_group(db, group_id)
  if not group:
    raise HTTPException(status_code=404, detail="Group not found")
  if role not in ("teacher", "admin") or (role == "teacher" and group.teacher_telegram_id != telegram_id):
    raise HTTPException(status_code=403, detail="No permission to delete this group")
  await crud.deactivate_group(db, group)
  return {"message": "Group deleted"}

@router.patch("/{group_id}", response_model=GroupRead)
async def update_group(group_id: int, group_update: GroupUpdate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
  role = current_user["role"]
  telegram_id = current_user["telegram_id"]

  if role not in ("teacher", "admin"):
    raise HTTPException(status_code=403, detail="Недостаточно прав для обновления группы")

  group = await crud.get_group(db, group_id)
  if not group:
    raise HTTPException(status_code=404, detail="Group not found")
  if role == "teacher" and group.teacher_telegram_id != telegram_id:
    raise HTTPException(status_code=403, detail="Можно редактировать только свои группы")

  return await crud.update_group(db, group, group_update)

@router.delete("/{group_id}/members/{student_telegram_id}")
async def remove_member(
  group_id: int,
  student_telegram_id: int,
  db: AsyncSession = Depends(get_db),
  current_user=Depends(get_current_user)
):
  role = current_user["role"]
  telegram_id = current_user["telegram_id"]

  group = await crud.get_group(db, group_id)
  if not group:
    raise HTTPException(status_code=404, detail="Group not found")

  if role not in ("teacher", "admin") or (role == "teacher" and group.teacher_telegram_id != telegram_id):
    raise HTTPException(status_code=403, detail="No permission to remove members")

  member = await crud.remove_member(db, group_id, student_telegram_id)
  if not member:
    raise HTTPException(status_code=404, detail="Member not found in group")

  # Отправляем уведомление студенту о том, что его удалили из группы
  try:
    # Получаем данные студента из auth-service
    student_name = "Студент"
    student_user_id = None
    async with httpx.AsyncClient() as client:
      try:
        user_response = await client.get(
          f"{AUTH_SERVICE_URL}/auth/user-by-telegram/{student_telegram_id}",
          timeout=10
        )
        if user_response.status_code == 200:
          user_data = user_response.json()
          student_name = user_data.get("full_name", "Студент")
          student_user_id = str(user_data.get("id"))
      except Exception as e:
        logger.error(f"Failed to get student data from auth-service: {e}")

    title = "❌ Вас удалили из группы"
    message = (
      f"Здравствуйте, {student_name}!\n\n"
      f"Вас удалили из группы:\n"
      f"📚 <b>Группа:</b> {group.name}\n"
      f"🌐 <b>Язык:</b> {group.language}\n"
      f"📊 <b>Уровень:</b> {group.level}"
    )

    notification_data = {
      "chat_id": student_telegram_id,
      "title": title,
      "message": message,
      "notification_type": "group_member_removed",
      "user_id": student_user_id,
      "telegram_id": student_telegram_id,
      "group_id": group.id,
      "group_name": group.name
    }

    await rabbitmq_client.publish_notification(notification_data, routing_key="telegram")
    logger.info(f"Group member removed notification sent to student {student_telegram_id}")
  except Exception as e:
    logger.error(f"Failed to send group member removed notification: {e}")

  return {"message": f"Member {student_telegram_id} removed from group {group_id}"}

@router.delete("/{group_id}/leave")
async def leave_group_endpoint(
  group_id: int,
  db: AsyncSession = Depends(get_db),
  current_user=Depends(get_current_user)
):
  telegram_id = current_user["telegram_id"]

  group = await crud.get_group(db, group_id)
  if not group:
    raise HTTPException(status_code=404, detail="Group not found")

  member = await crud.leave_group(db, group_id, telegram_id)
  if not member:
    raise HTTPException(status_code=404, detail="You are not a member of this group")

  return {"message": f"You have left the group {group_id}"}

@router.post("/invitations")
async def create_invitation(data: InvitationCreateRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
  role = current_user["role"]
  telegram_id = current_user["telegram_id"]

  if role not in ("teacher", "admin"):
    raise HTTPException(status_code=403, detail="Недостаточно прав для обновления группы")

  group = await crud.get_group(db, data.group_id)
  if not group:
    raise HTTPException(status_code=404, detail="Group not found")
  if role == "teacher" and group.teacher_telegram_id != telegram_id:
    raise HTTPException(status_code=403, detail="No permission to invite")
  
  # Если student_telegram_id не указан, используем 0 для общего приглашения
  student_telegram_id = data.student_telegram_id if data.student_telegram_id else 0
  
  invitation = await crud.create_invitation(
    db, group, data.message, data.expires_in_hours, student_telegram_id
  )
  
  # Отправляем уведомление студенту, если он указан
  if data.student_telegram_id:
    try:
      # Получаем данные студента из auth-service
      student_name = "Студент"
      student_user_id = None
      async with httpx.AsyncClient() as client:
        try:
          user_response = await client.get(
            f"{AUTH_SERVICE_URL}/auth/user-by-telegram/{data.student_telegram_id}",
            timeout=10
          )
          if user_response.status_code == 200:
            user_data = user_response.json()
            student_name = user_data.get("full_name", "Студент")
            student_user_id = str(user_data.get("id"))
        except Exception as e:
          logger.error(f"Failed to get student data from auth-service: {e}")

      frontend_url = os.getenv("FRONTEND_URL", "https://unseemly-adorable-razorbill.cloudpub.ru")
      invite_url = f"{frontend_url}/groups/invite/{invitation.invite_token}"

      title = "📩 Приглашение в группу"
      message_parts = [
        f"Здравствуйте, {student_name}!\n\n",
        f"Вас приглашают присоединиться к группе:\n",
        f"📚 <b>Группа:</b> {group.name}\n",
        f"🌐 <b>Язык:</b> {group.language}\n",
        f"📊 <b>Уровень:</b> {group.level}\n"
      ]
      
      if data.message:
        message_parts.append(f"\n💬 <b>Сообщение:</b>\n{data.message}\n")
      
      message_parts.append(f"\n🔗 <b>Ссылка для присоединения:</b>\n{invite_url}")
      
      message = "".join(message_parts)

      notification_data = {
        "chat_id": data.student_telegram_id,
        "title": title,
        "message": message,
        "notification_type": "group_invitation",
        "user_id": student_user_id,
        "telegram_id": data.student_telegram_id,
        "group_id": group.id,
        "group_name": group.name,
        "invite_token": invitation.invite_token
      }

      await rabbitmq_client.publish_notification(notification_data, routing_key="telegram")
      logger.info(f"Group invitation notification sent to student {data.student_telegram_id}")
    except Exception as e:
      logger.error(f"Failed to send group invitation notification: {e}")

  return {"invite_token": invitation.invite_token}

@router.get("/invitations/{invite_token}/get")
async def get_invitation(
  invite_token: str,
  db: AsyncSession = Depends(get_db)
):
  invitation = await crud.get_invitation_by_token(db, invite_token)
  if not invitation:
    raise HTTPException(status_code=404, detail="Invitation not found or expired")

  group = await crud.get_group(db, invitation.group_id)
  if not group:
    raise HTTPException(status_code=404, detail="Group not found")

  return group

@router.post("/invitations/{invite_token}/accept")
async def accept_invitation(
  invite_token: str,
  db: AsyncSession = Depends(get_db)
):
  invitation = await crud.get_invitation_by_token(db, invite_token)
  if not invitation:
    raise HTTPException(status_code=404, detail="Invitation not found or expired")

  group = await crud.get_group(db, invitation.group_id)
  if not group:
    raise HTTPException(status_code=404, detail="Group not found")

  try:
    await crud.accept_invitation(db, invitation, group)
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

  # Отправляем уведомление студенту о том, что он присоединился к группе
  if invitation.student_telegram_id:
    try:
      # Получаем данные студента из auth-service
      student_name = "Студент"
      student_user_id = None
      async with httpx.AsyncClient() as client:
        try:
          user_response = await client.get(
            f"{AUTH_SERVICE_URL}/auth/user-by-telegram/{invitation.student_telegram_id}",
            timeout=10
          )
          if user_response.status_code == 200:
            user_data = user_response.json()
            student_name = user_data.get("full_name", "Студент")
            student_user_id = str(user_data.get("id"))
        except Exception as e:
          logger.error(f"Failed to get student data from auth-service: {e}")

      title = "✅ Вы присоединились к группе"
      message_parts = [
        f"Поздравляем, {student_name}!\n\n",
        f"Вы успешно присоединились к группе:\n",
        f"📚 <b>Группа:</b> {group.name}\n",
        f"🌐 <b>Язык:</b> {group.language}\n",
        f"📊 <b>Уровень:</b> {group.level}\n",
        f"👥 <b>Участников:</b> {group.current_students}/{group.max_students}"
      ]
      
      # Добавляем сообщение из приглашения, если оно есть
      if invitation.message:
        message_parts.append(f"\n💬 <b>Сообщение от преподавателя:</b>\n{invitation.message}")
      
      message = "".join(message_parts)

      notification_data = {
        "chat_id": invitation.student_telegram_id,
        "title": title,
        "message": message,
        "notification_type": "group_invitation_accepted",
        "user_id": student_user_id,
        "telegram_id": invitation.student_telegram_id,
        "group_id": group.id,
        "group_name": group.name
      }

      await rabbitmq_client.publish_notification(notification_data, routing_key="telegram")
      logger.info(f"Group invitation accepted notification sent to student {invitation.student_telegram_id}")
    except Exception as e:
      logger.error(f"Failed to send group invitation accepted notification: {e}")

  return {
    "message": "You have joined the group",
    "group_id": group.id,
    "student_telegram_id": invitation.student_telegram_id
  }

@router.get("/invitations/student/{student_telegram_id}")
async def get_student_invitations(
  student_telegram_id: int,
  db: AsyncSession = Depends(get_db),
  current_user=Depends(get_current_user)
):
  """Получить список приглашений для студента"""
  role = current_user["role"]
  telegram_id = current_user["telegram_id"]

  # Проверяем права доступа
  if role not in ("teacher", "admin"):
    # Студент может видеть только свои приглашения
    if student_telegram_id != telegram_id:
      raise HTTPException(status_code=403, detail="No permission to view invitations")
  elif role == "teacher":
    # Учитель может видеть приглашения только для студентов своих групп
    # Для упрощения разрешаем учителям и админам видеть все приглашения
    pass

  result = await db.execute(
    select(GroupInvitation)
    .filter(GroupInvitation.student_telegram_id == student_telegram_id)
    .order_by(GroupInvitation.sent_at.desc())
  )
  invitations = result.scalars().all()

  # Получаем информацию о группах
  invitations_data = []
  for inv in invitations:
    group = await crud.get_group(db, inv.group_id)
    if group:
      now = datetime.now(timezone.utc)
      expires_at_utc = inv.expires_at.replace(tzinfo=timezone.utc) if inv.expires_at else None
      is_active = inv.status == "pending" and (expires_at_utc is None or expires_at_utc > now)
      invitations_data.append({
        "id": inv.id,
        "invite_token": inv.invite_token,
        "group_id": inv.group_id,
        "group_name": group.name,
        "status": inv.status,
        "is_active": is_active,
        "sent_at": inv.sent_at.isoformat() if inv.sent_at else None,
        "expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
        "message": inv.message,
        "invite_url": f"{FRONTEND_URL}/groups/invite/{inv.invite_token}"
      })

  return invitations_data

@router.delete("/invitations/{invitation_id}")
async def delete_invitation(
  invitation_id: int,
  db: AsyncSession = Depends(get_db),
  current_user=Depends(get_current_user)
):
  """Удалить приглашение"""
  role = current_user["role"]
  telegram_id = current_user["telegram_id"]

  invitation = await db.get(GroupInvitation, invitation_id)
  if not invitation:
    raise HTTPException(status_code=404, detail="Invitation not found")

  # Проверяем права доступа
  if role not in ("teacher", "admin"):
    raise HTTPException(status_code=403, detail="No permission to delete invitations")
  
  if role == "teacher":
    group = await crud.get_group(db, invitation.group_id)
    if group and group.teacher_telegram_id != telegram_id:
      raise HTTPException(status_code=403, detail="No permission to delete this invitation")

  await db.delete(invitation)
  await db.commit()

  return {"message": "Invitation deleted"}

