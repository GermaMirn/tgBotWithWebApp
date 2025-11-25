from fastapi import APIRouter, Header, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date
from fastapi.encoders import jsonable_encoder
import httpx
from uuid import UUID

from ..schemas import lessons
from ..core.auth import get_current_user_telegram_id

router = APIRouter()
LESSONS_SERVICE_URL = "http://lessons-service:8008"


# ---------------- LESSONS ----------------
@router.post("", response_model=lessons.LessonResponse)
async def create_lesson_bff(lesson: lessons.LessonCreate, authorization: str = Header(None)):
  teacher_id = await get_current_user_telegram_id(authorization)
  if not teacher_id:
    raise HTTPException(401, "Unauthorized")
  if lesson.teacher_telegram_id != teacher_id:
    raise HTTPException(403, "Can only create lessons for yourself")

  async with httpx.AsyncClient() as client:
    resp = await client.post(f"{LESSONS_SERVICE_URL}/lessons", json=lesson.dict(), timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.get("/{lesson_id}", response_model=lessons.LessonResponse)
async def get_lesson_bff(lesson_id: int, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    try:
      resp = await client.get(f"{LESSONS_SERVICE_URL}/lessons/{lesson_id}", timeout=10)
      resp.raise_for_status()
      return resp.json()
    except httpx.HTTPStatusError as e:
      if e.response.status_code == 404:
        raise HTTPException(404, "Lesson not found")
      raise HTTPException(e.response.status_code, e.response.text)


@router.put("/{lesson_id}", response_model=lessons.LessonResponse)
async def update_lesson_bff(lesson_id: int, lesson_update: lessons.LessonUpdate, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.put(f"{LESSONS_SERVICE_URL}/lessons/{lesson_id}", json=lesson_update.dict(exclude_unset=True), timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.delete("/{lesson_id}", response_model=dict)
async def delete_lesson_bff(lesson_id: int, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.delete(f"{LESSONS_SERVICE_URL}/lessons/{lesson_id}", timeout=10)
    resp.raise_for_status()
    return {"detail": "Lesson deleted"}


@router.get("", response_model=List[lessons.LessonResponse])
async def list_lessons_bff(
  language: Optional[str] = Query(None),
  level: Optional[str] = Query(None),
  teacher_id: Optional[int] = Query(None),
  authorization: str = Header(None)
):
  await get_current_user_telegram_id(authorization)
  params = {k: v for k, v in {"language": language, "level": level, "teacher_id": teacher_id}.items() if v is not None}
  async with httpx.AsyncClient() as client:
    resp = await client.get(f"{LESSONS_SERVICE_URL}/lessons", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


# ---------------- LESSON SESSIONS ----------------
@router.post("/sessions", response_model=lessons.LessonSessionResponse)
async def create_session_bff(session: lessons.LessonSessionCreate, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.post(f"{LESSONS_SERVICE_URL}/sessions", json=session.dict(), timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.get("/sessions/{session_id}", response_model=lessons.LessonSessionResponse)
async def get_session_bff(session_id: int, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.get(f"{LESSONS_SERVICE_URL}/sessions/{session_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.get("/sessions/by-teacher", response_model=List[lessons.LessonSessionResponse])
async def list_sessions_by_teacher_bff(
  teacher_telegram_id: int,
  start: datetime = Query(...),
  end: datetime = Query(...),
  authorization: str = Header(None)
):
  await get_current_user_telegram_id(authorization)
  params = {"teacher_telegram_id": teacher_telegram_id, "start": start.isoformat(), "end": end.isoformat()}
  async with httpx.AsyncClient() as client:
    resp = await client.get(f"{LESSONS_SERVICE_URL}/sessions/by-teacher", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.put("/sessions/{session_id}", response_model=lessons.LessonSessionResponse)
async def update_session_bff(session_id: int, session_update: lessons.LessonSessionUpdate, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.put(f"{LESSONS_SERVICE_URL}/sessions/{session_id}", json=session_update.dict(exclude_unset=True), timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session_bff(session_id: int, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.delete(f"{LESSONS_SERVICE_URL}/sessions/{session_id}", timeout=10)
    resp.raise_for_status()
    return None


# ---------------- PARTICIPANTS ----------------
@router.post("/participants", response_model=lessons.LessonParticipantResponse)
async def add_participant_bff(payload: lessons.LessonParticipantCreate, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.post(f"{LESSONS_SERVICE_URL}/participants", json=payload.dict(), timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.put("/participants/{participant_id}", response_model=lessons.LessonParticipantResponse)
async def set_participant_confirmation_bff(participant_id: int, confirmed: bool, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.put(f"{LESSONS_SERVICE_URL}/participants/{participant_id}?confirmed={confirmed}", timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.delete("/participants/{participant_id}", status_code=204)
async def remove_participant_bff(participant_id: int, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.delete(f"{LESSONS_SERVICE_URL}/participants/{participant_id}", timeout=10)
    resp.raise_for_status()
    return None


# ---------------- ATTENDANCE ----------------
@router.post("/attendance", response_model=lessons.LessonAttendanceResponse)
async def add_attendance_bff(payload: lessons.LessonAttendanceCreate, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.post(f"{LESSONS_SERVICE_URL}/attendance", json=payload.dict(), timeout=10)
    resp.raise_for_status()
    return resp.json()


@router.get("/attendance/{lesson_id}", response_model=List[lessons.LessonAttendanceResponse])
async def list_attendance_bff(lesson_id: int, authorization: str = Header(None)):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.get(f"{LESSONS_SERVICE_URL}/attendance/{lesson_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


# ---------------- FREE SLOTS ----------------
@router.get("/free-slots", response_model=lessons.FreeSlotsResponse)
async def free_slots_bff(
  teacher_telegram_id: int,
  the_date: date = Query(...),
  authorization: str = Header(None)
):
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    resp = await client.get(
      f"{LESSONS_SERVICE_URL}/free-slots",
      params={"teacher_telegram_id": teacher_telegram_id, "the_date": the_date.isoformat()},
      timeout=10
    )
    resp.raise_for_status()
    return resp.json()


@router.post("/create-full-lesson", response_model=lessons.LessonSessionResponse)
async def create_full_lesson_bff(payload: lessons.CreateFullLessonPayload, authorization: str = Header(None)):
  teacher_id = await get_current_user_telegram_id(authorization)
  if not teacher_id:
    raise HTTPException(401, "Unauthorized")
  if payload.teacher_telegram_id != teacher_id:
    raise HTTPException(403, "Can only create lessons for yourself")

  async with httpx.AsyncClient() as client:
    # 1. Создаем Lesson
    lesson_data = jsonable_encoder(payload.lesson)
    lesson_resp = await client.post(f"{LESSONS_SERVICE_URL}/lessons", json=lesson_data)
    lesson_resp.raise_for_status()
    lesson = lesson_resp.json()

    # 2. Создаем Session
    session_data = jsonable_encoder(payload.session)
    session_data["lesson_id"] = lesson["id"]
    print(session_data)
    session_resp = await client.post(f"{LESSONS_SERVICE_URL}/lessons/sessions", json=session_data)
    session_resp.raise_for_status()
    return session_resp.json()

@router.delete("/delete-full-lesson/{lesson_id}", status_code=204)
async def delete_full_lesson_bff(
  lesson_id: int,
  authorization: str = Header(None)
):
  teacher_id = await get_current_user_telegram_id(authorization)
  if not teacher_id:
    raise HTTPException(401, "Unauthorized")

  async with httpx.AsyncClient() as client:
    lesson_resp = await client.get(f"{LESSONS_SERVICE_URL}/lessons/{lesson_id}")
    if lesson_resp.status_code == 404:
      raise HTTPException(404, "Lesson not found")

    lesson = lesson_resp.json()

    if lesson["teacher_telegram_id"] != teacher_id:
      raise HTTPException(403, "You can delete only your own lessons")

    sessions_resp = await client.post(
      f"{LESSONS_SERVICE_URL}/lessons/sessions/by-teacher",
      json={
        "teacher_telegram_id": teacher_id,
        "start": "1970-01-01T00:00:00Z",
        "end": "2100-01-01T00:00:00Z"
      }
    )
    sessions_resp.raise_for_status()
    sessions = sessions_resp.json()

    for s in sessions:
      if s["lesson_id"] == lesson_id:
        await client.delete(f"{LESSONS_SERVICE_URL}/lessons/sessions/{s['id']}")

    del_resp = await client.delete(f"{LESSONS_SERVICE_URL}/lessons/{lesson_id}")
    del_resp.raise_for_status()

  return None

# ---------------- ENROLLMENT / ЗАПИСЬ НА ЗАНЯТИЯ ----------------
@router.post("/enroll", response_model=lessons.LessonParticipantResponse)
async def enroll_to_lesson_bff(
  payload: lessons.EnrollmentCreate,
  authorization: str = Header(None)
):
  """
  Записать студента или группу на занятие
  """
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    try:
      resp = await client.post(
        f"{LESSONS_SERVICE_URL}/lessons/enroll",
        json=jsonable_encoder(payload),
        timeout=10
      )
      resp.raise_for_status()
      return resp.json()
    except httpx.HTTPStatusError as e:
      if e.response.status_code == 400:
        raise HTTPException(400, e.response.json().get("detail", "Bad request"))
      raise HTTPException(e.response.status_code, e.response.text)

@router.get("/{lesson_id}/participants", response_model=List[lessons.LessonParticipantResponse])
async def get_lesson_participants_bff(
  lesson_id: int,
  authorization: str = Header(None)
):
  """
  Получить список участников занятия
  """
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    try:
      resp = await client.get(
        f"{LESSONS_SERVICE_URL}/lessons/{lesson_id}/participants",
        timeout=10
      )
      resp.raise_for_status()
      return resp.json()
    except httpx.HTTPStatusError as e:
      if e.response.status_code == 404:
        raise HTTPException(404, "No participants found for this lesson")
      raise HTTPException(e.response.status_code, e.response.text)

@router.delete("/{lesson_id}/participants/{student_id}", status_code=204)
async def remove_student_from_lesson_bff(
  lesson_id: int,
  student_id: UUID,
  authorization: str = Header(None)
):
  """
  Отписать студента от занятия
  """
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    try:
      resp = await client.delete(
        f"{LESSONS_SERVICE_URL}/lessons/{lesson_id}/participants/{student_id}",
        timeout=10
      )
      resp.raise_for_status()
      return None
    except httpx.HTTPStatusError as e:
      if e.response.status_code == 404:
        raise HTTPException(404, "Student not found in this lesson")
      raise HTTPException(e.response.status_code, e.response.text)

@router.delete("/{lesson_id}/participants/group/{group_id}", status_code=204)
async def remove_group_from_lesson_bff(
  lesson_id: int,
  group_id: int,
  authorization: str = Header(None)
):
  """
  Отписать группу от занятия
  """
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    try:
      resp = await client.delete(
        f"{LESSONS_SERVICE_URL}/lessons/{lesson_id}/participants/group/{group_id}",
        timeout=10
      )
      resp.raise_for_status()
      return None
    except httpx.HTTPStatusError as e:
      if e.response.status_code == 404:
        raise HTTPException(404, "Group not found in this lesson")
      raise HTTPException(e.response.status_code, e.response.text)

@router.post("/{lesson_id}/enroll-bulk", response_model=List[lessons.LessonParticipantResponse])
async def bulk_enroll_students_to_lesson_bff(
  lesson_id: int,
  student_ids: List[UUID],
  authorization: str = Header(None)
):
  """
  Массовая запись студентов на занятие
  """
  await get_current_user_telegram_id(authorization)
  async with httpx.AsyncClient() as client:
    try:
      resp = await client.post(
        f"{LESSONS_SERVICE_URL}/lessons/{lesson_id}/enroll-bulk",
        json=jsonable_encoder({"student_ids": student_ids}),
        timeout=10
      )
      resp.raise_for_status()
      return resp.json()
    except httpx.HTTPStatusError as e:
      if e.response.status_code == 400:
        raise HTTPException(400, e.response.json().get("detail", "Bad request"))
      raise HTTPException(e.response.status_code, e.response.text)
