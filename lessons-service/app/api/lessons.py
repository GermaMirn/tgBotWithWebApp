# app/api/lessons.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from typing import List, Optional

from ..database import get_async_db
from .. import crud, schemas
from ..services.availability import compute_free_slots

router = APIRouter()

# ---- LESSON ----
@router.post("", response_model=schemas.LessonResponse)
async def create_lesson(payload: schemas.LessonCreate, db: AsyncSession = Depends(get_async_db)):
  return await crud.create_lesson(db, payload)

@router.get("/{lesson_id}", response_model=schemas.LessonResponse)
async def get_lesson(lesson_id: int, db: AsyncSession = Depends(get_async_db)):
  obj = await crud.get_lesson(db, lesson_id)
  if not obj:
    raise HTTPException(404, "Lesson not found")
  return obj

@router.get("", response_model=List[schemas.LessonResponse])
async def list_lessons(teacher_telegram_id: Optional[int] = None, db: AsyncSession = Depends(get_async_db)):
  return await crud.list_lessons(db, teacher_telegram_id)

@router.put("/{lesson_id}", response_model=schemas.LessonResponse)
async def update_lesson(lesson_id: int, payload: schemas.LessonUpdate, db: AsyncSession = Depends(get_async_db)):
  obj = await crud.get_lesson(db, lesson_id)
  if not obj:
    raise HTTPException(404, "Lesson not found")
  return await crud.update_lesson(db, obj, payload)

@router.delete("/{lesson_id}", status_code=204)
async def delete_lesson(lesson_id: int, db: AsyncSession = Depends(get_async_db)):
  obj = await crud.get_lesson(db, lesson_id)
  if not obj:
    raise HTTPException(404, "Lesson not found")
  await crud.delete_lesson(db, obj)
  return None


# ---- SESSION ----
@router.post("/sessions", response_model=schemas.LessonSessionResponse)
async def create_session(payload: schemas.LessonSessionCreate, db: AsyncSession = Depends(get_async_db)):
  try:
    return await crud.create_session(db, payload)
  except ValueError as e:
    raise HTTPException(400, str(e))

@router.get("/sessions/{session_id}", response_model=schemas.LessonSessionResponse)
async def get_session(session_id: int, db: AsyncSession = Depends(get_async_db)):
  obj = await crud.get_session(db, session_id)
  if not obj:
    raise HTTPException(404, "Session not found")
  return obj

@router.post("/sessions/by-teacher", response_model=List[schemas.LessonSessionResponse])
async def list_sessions_by_teacher(
  req: schemas.TeacherSessionsRequest,
  db: AsyncSession = Depends(get_async_db)
):
  return await crud.list_sessions_by_teacher_and_range(
    db, req.teacher_telegram_id, req.start, req.end
  )

@router.put("/sessions/{session_id}", response_model=schemas.LessonSessionResponse)
async def update_session(session_id: int, payload: schemas.LessonSessionUpdate, db: AsyncSession = Depends(get_async_db)):
  obj = await crud.get_session(db, session_id)
  if not obj:
    raise HTTPException(404, "Session not found")
  return await crud.update_session(db, obj, payload)

@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: int, db: AsyncSession = Depends(get_async_db)):
  obj = await crud.get_session(db, session_id)
  if not obj:
    raise HTTPException(404, "Session not found")
  await crud.delete_session(db, obj)
  return None


# ---- PARTICIPANTS ----
@router.post("/participants", response_model=schemas.LessonParticipantResponse)
async def add_participant(payload: schemas.LessonParticipantCreate, db: AsyncSession = Depends(get_async_db)):
  try:
    return await crud.add_participant(db, payload)
  except ValueError as e:
    raise HTTPException(400, str(e))

@router.put("/participants/{participant_id}", response_model=schemas.LessonParticipantResponse)
async def set_participant_confirmation(participant_id: int, confirmed: bool, db: AsyncSession = Depends(get_async_db)):
  obj = await crud.get_participant(db, participant_id)
  if not obj:
    raise HTTPException(404, "Participant not found")
  return await crud.set_participant_confirmed(db, obj, confirmed)

@router.delete("/participants/{participant_id}", status_code=204)
async def remove_participant(participant_id: int, db: AsyncSession = Depends(get_async_db)):
  obj = await crud.get_participant(db, participant_id)
  if not obj:
    raise HTTPException(404, "Participant not found")
  await crud.remove_participant(db, obj)
  return None


# ---- ATTENDANCE ----
@router.post("/attendance", response_model=schemas.LessonAttendanceResponse)
async def add_attendance(payload: schemas.LessonAttendanceCreate, db: AsyncSession = Depends(get_async_db)):
  return await crud.add_attendance(db, payload)

@router.get("/attendance/{lesson_id}", response_model=List[schemas.LessonAttendanceResponse])
async def list_attendance(lesson_id: int, db: AsyncSession = Depends(get_async_db)):
  return await crud.list_attendance(db, lesson_id)


# ---- FREE SLOTS ----
@router.get("/free-slots", response_model=schemas.FreeSlotsResponse)
async def free_slots(
  teacher_telegram_id: int,
  the_date: date = Query(..., description="YYYY-MM-DD"),
  calendary_base_url: str = Query("http://calendary-service:8000", description="URL calendary-service"),
  db: AsyncSession = Depends(get_async_db)
):
  day_start = datetime(the_date.year, the_date.month, the_date.day, 0, 0, 0)
  day_end = datetime(the_date.year, the_date.month, the_date.day, 23, 59, 59)

  sessions = await crud.list_sessions_by_teacher_and_range(db, teacher_telegram_id, day_start, day_end)
  existing = [(s.start_time, s.end_time) for s in sessions]

  slots = await compute_free_slots(
    teacher_telegram_id=teacher_telegram_id,
    the_date=the_date,
    existing_sessions=existing
  )
  return schemas.FreeSlotsResponse(
    teacher_telegram_id=teacher_telegram_id,
    date=the_date.isoformat(),
    slots=slots
  )
