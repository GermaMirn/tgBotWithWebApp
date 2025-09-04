# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, date
from typing import List, Optional

from . import models, schemas

# -------- LESSON --------
async def create_lesson(db: AsyncSession, data: schemas.LessonCreate) -> models.Lesson:
  obj = models.Lesson(**data.dict())
  db.add(obj)
  await db.commit()
  await db.refresh(obj)
  return obj

async def get_lesson(db: AsyncSession, lesson_id: int) -> Optional[models.Lesson]:
  result = await db.execute(select(models.Lesson).where(models.Lesson.id == lesson_id))
  return result.scalar_one_or_none()

async def list_lessons(db: AsyncSession, teacher_telegram_id: Optional[int] = None) -> List[models.Lesson]:
  stmt = select(models.Lesson)
  if teacher_telegram_id:
    stmt = stmt.where(models.Lesson.teacher_telegram_id == teacher_telegram_id)
  result = await db.execute(stmt)
  return result.scalars().all()

async def update_lesson(db: AsyncSession, lesson: models.Lesson, data: schemas.LessonUpdate) -> models.Lesson:
  for k, v in data.dict(exclude_unset=True).items():
    setattr(lesson, k, v)
  await db.commit()
  await db.refresh(lesson)
  return lesson

async def delete_lesson(db: AsyncSession, lesson: models.Lesson) -> None:
  await db.delete(lesson)
  await db.commit()


# -------- SESSION --------
async def create_session(db: AsyncSession, data: schemas.LessonSessionCreate) -> models.LessonSession:
  lesson = await get_lesson(db, data.lesson_id)
  if not lesson:
    raise ValueError("Lesson not found")
  print(data)
  # Проверка пересечений
  stmt = select(models.LessonSession).join(models.Lesson).where(
    and_(
      models.Lesson.teacher_telegram_id == lesson.teacher_telegram_id,
      models.LessonSession.start_time < data.end_time,
      models.LessonSession.end_time > data.start_time
    )
  )
  result = await db.execute(stmt)
  overlap = result.scalar_one_or_none()
  if overlap:
    raise ValueError("Teacher already has a session in this time range")

  obj = models.LessonSession(
    lesson_id=data.lesson_id,
    start_time=data.start_time,
    end_time=data.end_time,
    status=data.status or schemas.LessonStatus.scheduled
  )
  db.add(obj)
  await db.commit()
  await db.refresh(obj)
  return obj

async def get_session(db: AsyncSession, session_id: int) -> Optional[models.LessonSession]:
  result = await db.execute(select(models.LessonSession).where(models.LessonSession.id == session_id))
  return result.scalar_one_or_none()

async def list_sessions_by_teacher_and_range(
  db: AsyncSession, teacher_telegram_id: int, start: date, end: date
) -> List[models.LessonSession]:

  stmt = select(models.LessonSession).join(models.Lesson).where(
    and_(
      models.Lesson.teacher_telegram_id == teacher_telegram_id,
      func.date(models.LessonSession.created_at) >= start,
      func.date(models.LessonSession.created_at) <= end
    )
  )
  result = await db.execute(stmt)
  return result.scalars().all()

async def update_session(db: AsyncSession, session: models.LessonSession, data: schemas.LessonSessionUpdate) -> models.LessonSession:
  for k, v in data.dict(exclude_unset=True).items():
    setattr(session, k, v)
  await db.commit()
  await db.refresh(session)
  return session

async def delete_session(db: AsyncSession, session: models.LessonSession) -> None:
  await db.delete(session)
  await db.commit()


# -------- PARTICIPANT --------
async def add_participant(db: AsyncSession, data: schemas.LessonParticipantCreate) -> models.LessonParticipant:
  if not (data.student_id or data.group_id):
    raise ValueError("Provide student_id or group_id")

  obj = models.LessonParticipant(
    lesson_id=data.lesson_id,
    student_id=data.student_id,
    group_id=data.group_id,
    is_confirmed=data.is_confirmed,
    confirmation_date=datetime.utcnow() if data.is_confirmed else None
  )
  db.add(obj)
  await db.commit()
  await db.refresh(obj)
  return obj

async def set_participant_confirmed(db: AsyncSession, participant: models.LessonParticipant, confirmed: bool) -> models.LessonParticipant:
  participant.is_confirmed = confirmed
  participant.confirmation_date = datetime.utcnow() if confirmed else None
  await db.commit()
  await db.refresh(participant)
  return participant

async def remove_participant(db: AsyncSession, participant: models.LessonParticipant) -> None:
  await db.delete(participant)
  await db.commit()

async def get_participant(db: AsyncSession, participant_id: int) -> Optional[models.LessonParticipant]:
  result = await db.execute(select(models.LessonParticipant).where(models.LessonParticipant.id == participant_id))
  return result.scalar_one_or_none()


# -------- ATTENDANCE --------
async def add_attendance(db: AsyncSession, data: schemas.LessonAttendanceCreate) -> models.LessonAttendance:
  obj = models.LessonAttendance(
    lesson_id=data.lesson_id,
    student_id=data.student_id,
    status=data.status,
    join_time=data.join_time,
    leave_time=data.leave_time
  )
  db.add(obj)
  await db.commit()
  await db.refresh(obj)
  return obj

async def list_attendance(db: AsyncSession, lesson_id: int) -> List[models.LessonAttendance]:
  stmt = select(models.LessonAttendance).where(models.LessonAttendance.lesson_id == lesson_id)
  result = await db.execute(stmt)
  return result.scalars().all()
