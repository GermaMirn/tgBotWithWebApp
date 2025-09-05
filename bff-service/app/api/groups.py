from datetime import date, datetime
from fastapi import APIRouter, Header, HTTPException, Depends
from app.core.auth import get_current_user, get_current_user_telegram_id
from app.services.auth_service import get_user_by_id
from app.schemas.group import GroupRead, GroupCreate, GroupUpdate
import httpx
from typing import Optional

router = APIRouter()

GROUPS_SERVICE_URL = "http://groups-service:8005"
STUDENTS_SERVICE_URL = "http://students-service:8004"
AUTH_SERVICE_URL = "http://auth-service:8002"

async def get_token_from_header(authorization: str):
  if not authorization or not authorization.startswith("Bearer "):
    raise HTTPException(status_code=401, detail="Authorization header required")
  return authorization[7:]  # Убираем "Bearer "

@router.get("/teacher")
async def get_teacher_groups(authorization: str = Header(None)):
  token = await get_token_from_header(authorization)

  async with httpx.AsyncClient() as client:
    try:
      response = await client.get(
        f"{GROUPS_SERVICE_URL}/groups/teacher",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
      )
      if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
      elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
      return response.json()
    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"groups-service error: {str(e)}")

@router.get("/student")
async def get_student_groups(authorization: str = Header(None)):
  token = await get_token_from_header(authorization)

  async with httpx.AsyncClient() as client:
    try:
      response = await client.get(
        f"{GROUPS_SERVICE_URL}/groups/student",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
      )
      if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
      elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
      return response.json()
    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"groups-service error: {str(e)}")

@router.post("", response_model=GroupRead)
async def create_group(
  group_data: GroupCreate,
  current_user: dict = Depends(get_current_user)
):
  role = current_user.get('role')

  if role not in ("teacher", "admin"):
    raise HTTPException(status_code=403, detail="Недостаточно прав для создания группы")

  async with httpx.AsyncClient() as client:
    try:
      data = group_data.model_dump()
      # Преобразуем даты в ISO строки, если они есть
      if data.get("start_date") and isinstance(data["start_date"], (date, datetime)):
        data["start_date"] = data["start_date"].isoformat()
      if data.get("end_date") and isinstance(data["end_date"], (date, datetime)):
        data["end_date"] = data["end_date"].isoformat()

      response = await client.post(
        f"{GROUPS_SERVICE_URL}/groups",
        headers={"Authorization": f"Bearer {current_user.get('token')}"},
        json=data,
        timeout=10
      )
      if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
      elif response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.text)
      return response.json()
    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"groups-service error: {str(e)}")

@router.get("/{group_id}", response_model=GroupRead)
async def get_group_by_id(
  group_id: int,
  current_user: dict = Depends(get_current_user)
):
  token = current_user.get("token")
  headers = {"Authorization": f"Bearer {token}"}

  async with httpx.AsyncClient() as client:
    try:
      # 1. Получаем данные самой группы
      group_resp = await client.get(
        f"{GROUPS_SERVICE_URL}/groups/{group_id}",
        headers=headers,
        timeout=10
      )
      if group_resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
      elif group_resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Group not found")
      elif group_resp.status_code != 200:
        raise HTTPException(status_code=group_resp.status_code, detail=group_resp.text)

      group_data = group_resp.json()

      # 2. Получаем учителя (по telegram_id)
      teacher = await get_user_by_id(group_data.get("teacher_telegram_id"))

      # 3. Получаем студентов этой группы
      students_resp = await client.get(
        f"{STUDENTS_SERVICE_URL}/groups/{group_id}/students",
        headers=headers,
        timeout=10
      )
      students = students_resp.json() if students_resp.status_code == 200 else []

      if isinstance(students, dict) and "students" in students:
        students = students["students"]
      elif isinstance(students, list):
        students = students
      else:
          students = []

      # 4. Собираем все telegram_id студентов
      student_ids = [s["telegram_id"] for s in students]

      # 5. Получаем пользователей из auth-service
      users_resp = await client.post(
        f"{AUTH_SERVICE_URL}/auth/users/by-ids",
        headers=headers,
        json=student_ids,
        timeout=10
      )

      users_map = {}
      if users_resp.status_code == 200:
        users = users_resp.json()
        # создаём словарь по telegram_id
        users_map = {u["telegram_id"]: u for u in users}

      # 6. Обогащаем студентов
      enriched_students = []
      for s in students:
        user_info = users_map.get(s["telegram_id"], {})
        enriched_students.append({
          **s,
          "full_name": user_info.get("full_name"),
          "username": user_info.get("username")
        })

      # 7. Склеиваем итоговый ответ
      group_data["teacher"] = teacher
      group_data["students"] = enriched_students

      return group_data

    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"groups-service error: {str(e)}")

# Нужно сделать batch на 3 шаге (удаления students из students-service)
@router.delete("/{group_id}")
async def delete_group(
  group_id: int,
  current_user: dict = Depends(get_current_user)
):
  role = current_user.get('role')
  token = current_user.get('token')

  if role not in ("teacher", "admin"):
    raise HTTPException(status_code=403, detail="Недостаточно прав для удаления группы")

  async with httpx.AsyncClient() as client:
    # 1. Удаляем группу в groups-service
    resp = await client.delete(
      f"{GROUPS_SERVICE_URL}/groups/{group_id}",
      headers={"Authorization": f"Bearer {token}"},
      timeout=10
    )
    if resp.status_code == 404:
      raise HTTPException(status_code=404, detail="Group not found")
    elif resp.status_code == 403:
      raise HTTPException(status_code=403, detail="No permission to delete this group")
    elif resp.status_code != 200:
      raise HTTPException(status_code=resp.status_code, detail=resp.text)

    # 2. Получаем список студентов из students-service
    students_resp = await client.get(
      f"{STUDENTS_SERVICE_URL}/groups/{group_id}/students",
      headers={"Authorization": f"Bearer {token}"},
      timeout=10
    )
    students = students_resp.json() if students_resp.status_code == 200 else []

    # 3. Удаляем их из students-service
    for s in students:
      await client.delete(
        f"{STUDENTS_SERVICE_URL}/groups/students/{s['telegram_id']}/groups/{group_id}",
        timeout=10
      )

  return {"message": "Group deleted and students removed from group"}

@router.delete("/{group_id}/members/{student_telegram_id}")
async def remove_member_by_teacher(
  group_id: int,
  student_telegram_id: int,
  authorization: str = Header(None)
):
  token = await get_token_from_header(authorization)

  async with httpx.AsyncClient() as client:
    # 1️) Удаляем участника из группы в groups-service
    resp = await client.delete(
      f"{GROUPS_SERVICE_URL}/groups/{group_id}/members/{student_telegram_id}",
      headers={"Authorization": f"Bearer {token}"},
      timeout=10,
    )
    if resp.status_code == 404:
      raise HTTPException(status_code=404, detail="Member or group not found")
    elif resp.status_code == 403:
      raise HTTPException(status_code=403, detail="No permission to remove member")
    elif resp.status_code != 200:
      raise HTTPException(status_code=resp.status_code, detail=resp.text)

    # 2️) Разрываем связь в students-service напрямую по telegram_id
    del_resp = await client.delete(
      f"{STUDENTS_SERVICE_URL}/groups/students/{student_telegram_id}/groups/{group_id}",
      timeout=10
    )
    if del_resp.status_code not in (200, 204):
      raise HTTPException(status_code=502, detail=f"students-service error: {del_resp.status_code}")

  return {"message": "Member removed from group in all services"}

@router.delete("/{group_id}/leave")
async def leave_group(
  group_id: int,
  authorization: str = Header(...)
):
  student_telegram_id = await get_current_user_telegram_id(authorization)
  if not student_telegram_id:
    raise HTTPException(status_code=401, detail="Invalid or missing token")

  async with httpx.AsyncClient() as client:
    try:
      # 1) Удаляем в groups-service (внутренняя логика groups-service)
      groups_resp = await client.delete(
        f"{GROUPS_SERVICE_URL}/groups/{group_id}/leave",
        headers={"Authorization": authorization},
        timeout=10
      )
      if groups_resp.status_code == 404:
        raise HTTPException(status_code=404, detail="You are not a member of this group or group not found")
      if groups_resp.status_code != 200:
        raise HTTPException(status_code=groups_resp.status_code, detail=groups_resp.text)

      # 2) Разрываем связь в students-service
      students_resp = await client.delete(
        f"{STUDENTS_SERVICE_URL}/groups/students/{student_telegram_id}/groups/{group_id}",
        headers={"Authorization": authorization},
        timeout=10
      )

      if students_resp.status_code == 404:
        return {
          "message": "You left the group (groups-service OK). Student not found or not linked in students-service."
        }
      if students_resp.status_code not in (200, 204):
        # если students-service вернул что-то неожиданное — пробрасываем ошибку 502
        raise HTTPException(status_code=502, detail=f"students-service error: {students_resp.status_code} {students_resp.text}")

      # Всё успешно — вернём единый успешный ответ
      return {"message": "You have left the group"}

    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"network error: {str(e)}")

@router.patch("/{group_id}", response_model=GroupRead)
async def update_group(
  group_id: int,
  group_update: GroupUpdate,
  current_user: dict = Depends(get_current_user)
):
  role = current_user.get("role")
  if role not in ("teacher", "admin"):
    raise HTTPException(status_code=403, detail="Недостаточно прав для обновления группы")

  data = group_update.model_dump()

  if data.get("start_date") and isinstance(data["start_date"], (date, datetime)):
    data["start_date"] = data["start_date"].isoformat()
  if data.get("end_date") and isinstance(data["end_date"], (date, datetime)):
    data["end_date"] = data["end_date"].isoformat()

  async with httpx.AsyncClient() as client:
    try:
      response = await client.patch(
        f"{GROUPS_SERVICE_URL}/groups/{group_id}",
        headers={"Authorization": f"Bearer {current_user.get('token')}"},
        json=data,
        timeout=10
      )
      if response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
      elif response.status_code == 403:
        raise HTTPException(status_code=403, detail="No permission to update this group")
      elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="Group not found")
      elif response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
      return response.json()
    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"groups-service error: {str(e)}")

@router.post("/invitations")
async def create_invitation(
  payload: dict,
  authorization: Optional[str] = Header(None),
  current_user: dict = Depends(get_current_user)
):
  token = await get_token_from_header(authorization)
  async with httpx.AsyncClient() as client:
    try:
      resp = await client.post(
        f"{GROUPS_SERVICE_URL}/groups/invitations",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
      )
      if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
      if resp.status_code == 403:
        raise HTTPException(status_code=403, detail=resp.text)
      if resp.status_code not in (200, 201):
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
      return resp.json()
    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"groups-service error: {str(e)}")

@router.get("/invitations/{invite_token}/get")
async def get_invitation(
  invite_token: str,
):
  async with httpx.AsyncClient() as client:
    try:
      resp = await client.get(
        f"{GROUPS_SERVICE_URL}/groups/invitations/{invite_token}/get",
        timeout=10
      )
      if resp.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
      if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
      return resp.json()
    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"groups-service error: {str(e)}")

@router.post("/invitations/{invite_token}/accept")
async def accept_invitation(invite_token: str):
  async with httpx.AsyncClient() as client:
    # 1. Принять приглашение в group-service
    try:
      group_resp = await client.post(
        f"{GROUPS_SERVICE_URL}/groups/invitations/{invite_token}/accept",
        timeout=10
      )
      if group_resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Invitation or group not found")
      elif group_resp.status_code != 200:
        raise HTTPException(status_code=group_resp.status_code, detail=group_resp.text)
      group_data = group_resp.json()
    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"groups-service error: {str(e)}")

    # Проверяем наличие нужных полей
    group_id = group_data.get("group_id")
    student_telegram_id = group_data.get("student_telegram_id")
    if not group_id or not student_telegram_id:
      raise HTTPException(status_code=500, detail="Missing group_id or student_telegram_id in response")

    # 2. Создаем запись в students-service (присваиваем студента группе)
    try:
      await client.post(
        f"{STUDENTS_SERVICE_URL}/students/assign-group",
        json={"telegram_id": student_telegram_id, "group_id": group_id},
        timeout=10
      )
    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"students-service error: {str(e)}")

  return {
    "message": "You have joined the group",
    "group": group_data
  }
