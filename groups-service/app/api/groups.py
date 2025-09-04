from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import crud
from app.schemas import GroupCreate, GroupRead, GroupUpdate, AddMemberRequest, InvitationCreateRequest, GetGroup
from typing import List
from app.utils.auth import get_current_user
import httpx

router = APIRouter()

STUDENTS_SERVICE_URL = "http://students-service:8004"

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
  if role != "teacher" and group.teacher_telegram_id != telegram_id:
    raise HTTPException(status_code=403, detail="No permission to invite")
  invitation = await crud.create_invitation(
    db, group, data.message, data.expires_in_hours, data.student_telegram_id
  )
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

  return {
    "message": "You have joined the group",
    "group_id": group.id,
    "student_telegram_id": invitation.student_telegram_id
  }

