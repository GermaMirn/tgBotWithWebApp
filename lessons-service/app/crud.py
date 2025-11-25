# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, exists, or_
from datetime import datetime, timezone, date as date_cls
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import aliased, selectinload

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
async def create_session(db: AsyncSession, data: schemas.LessonSessionCreate) -> schemas.LessonSessionResponse:
  lesson = await get_lesson(db, data.lesson_id)
  if not lesson:
    raise ValueError("Lesson not found")

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

  await db.refresh(obj, attribute_names=["lesson"])

  return schemas.LessonSessionResponse(
    id=obj.id,
    lesson_id=obj.lesson_id,
    start_time=obj.start_time,
    end_time=obj.end_time,
    status=obj.status,
    booked=False,
    booked_by=None,
    lesson={
        "id": obj.lesson.id,
        "title": obj.lesson.title,
        "description": obj.lesson.description,
        "lesson_type": obj.lesson.lesson_type.value,
        "language": obj.lesson.language,
        "level": obj.lesson.level,
        "teacher_telegram_id": obj.lesson.teacher_telegram_id
    } if obj.lesson else None
  )

async def get_session(db: AsyncSession, session_id: int) -> Optional[models.LessonSession]:
  result = await db.execute(select(models.LessonSession).where(models.LessonSession.id == session_id))
  return result.scalar_one_or_none()

async def list_sessions_by_teacher_and_range(
    db: AsyncSession, teacher_telegram_id: int, start, end
) -> List[dict]:
    start_dt = (
        datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)
        if isinstance(start, date_cls) and not isinstance(start, datetime)
        else start
    )
    end_dt = (
        datetime.combine(end, datetime.max.time(), tzinfo=timezone.utc)
        if isinstance(end, date_cls) and not isinstance(end, datetime)
        else end
    )

    LP = aliased(models.LessonParticipant)

    # Подзапрос: есть ли бронирование
    booked_exists = (
        select(1)
        .where(
            and_(
                LP.lesson_id == models.LessonSession.lesson_id,
                or_(LP.student_id.isnot(None), LP.group_id.isnot(None)),
            )
        )
        .limit(1)
        .correlate(models.LessonSession)
    )

    # Основной запрос
    stmt = (
        select(
            models.LessonSession,
            exists(booked_exists).label("booked"),
            LP.student_id,
            LP.group_id,
        )
        .join(models.Lesson, models.Lesson.id == models.LessonSession.lesson_id)
        .outerjoin(LP, LP.lesson_id == models.LessonSession.lesson_id)
        .options(selectinload(models.LessonSession.lesson))
        .where(
            models.LessonSession.start_time < end_dt,
            models.LessonSession.end_time > start_dt,
            models.Lesson.teacher_telegram_id == teacher_telegram_id,
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    sessions = []
    for session, booked, student_id, group_id in rows:
        booked_by = None
        if booked:
            if student_id is not None:
                booked_by = {"type": "student", "id": str(student_id)}
            elif group_id is not None:
                booked_by = {"type": "group", "id": group_id}

        sessions.append({
            "id": session.id,
            "lesson_id": session.lesson_id,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat(),
            "status": session.status.value,
            "booked": booked,
            "booked_by": booked_by,
            "lesson": {
                "id": session.lesson.id,
                "title": session.lesson.title,
                "description": session.lesson.description,
                "lesson_type": session.lesson.lesson_type.value,
                "language": session.lesson.language,
                "level": session.lesson.level,
                "teacher_telegram_id": session.lesson.teacher_telegram_id,
            } if session.lesson else None,
        })

    return sessions

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


# -------- ENROLLMENT --------
async def enroll_participant(db: AsyncSession, data: schemas.EnrollmentCreate) -> schemas.LessonParticipantResponse:
    """
    Записать студента или группу на занятие
    """
    # Проверяем, что урок существует
    lesson = await get_lesson(db, data.lesson_id)
    if not lesson:
        raise ValueError("Lesson not found")

    # Проверяем, что не дублируем запись
    stmt = select(models.LessonParticipant).where(
        models.LessonParticipant.lesson_id == data.lesson_id
    )

    if data.student_id:
        stmt = stmt.where(models.LessonParticipant.student_id == data.student_id)
    else:
        stmt = stmt.where(models.LessonParticipant.group_id == data.group_id)

    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise ValueError("Participant already enrolled in this lesson")

    # Создаем запись
    obj = models.LessonParticipant(
        lesson_id=data.lesson_id,
        student_id=data.student_id,
        group_id=data.group_id,
        is_confirmed=False,
        confirmation_date=None
    )

    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    # Возвращаем через схему ответа с конвертацией UUID в строку
    return schemas.LessonParticipantResponse(
        id=obj.id,
        lesson_id=obj.lesson_id,
        student_id=str(obj.student_id) if obj.student_id else None,
        group_id=obj.group_id,
        is_confirmed=obj.is_confirmed,
        confirmation_date=obj.confirmation_date
    )

async def get_lesson_participants(db: AsyncSession, lesson_id: int) -> List[models.LessonParticipant]:
    """
    Получить всех участников занятия
    """
    stmt = select(models.LessonParticipant).where(
        models.LessonParticipant.lesson_id == lesson_id
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_participant_by_lesson_and_student(
    db: AsyncSession,
    lesson_id: int,
    student_id: UUID
) -> Optional[models.LessonParticipant]:
    """
    Найти запись студента на конкретное занятие
    """
    stmt = select(models.LessonParticipant).where(
        and_(
            models.LessonParticipant.lesson_id == lesson_id,
            models.LessonParticipant.student_id == student_id
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_participant_by_lesson_and_group(
    db: AsyncSession,
    lesson_id: int,
    group_id: int
) -> Optional[models.LessonParticipant]:
    """
    Найти запись группы на конкретное занятие
    """
    stmt = select(models.LessonParticipant).where(
        and_(
            models.LessonParticipant.lesson_id == lesson_id,
            models.LessonParticipant.group_id == group_id
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
