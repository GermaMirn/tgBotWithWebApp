from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date, datetime, timedelta
import json

from . import models, schemas

# CRUD для TeacherSchedule (недельное расписание)
def get_teacher_schedule(db: Session, teacher_telegram_id: int, day_of_week: int) -> Optional[models.TeacherSchedule]:
    return db.query(models.TeacherSchedule).filter(
        and_(
            models.TeacherSchedule.teacher_telegram_id == teacher_telegram_id,
            models.TeacherSchedule.day_of_week == day_of_week
        )
    ).first()

def get_teacher_schedules(db: Session, teacher_telegram_id: int) -> List[models.TeacherSchedule]:
    return db.query(models.TeacherSchedule).filter(
        models.TeacherSchedule.teacher_telegram_id == teacher_telegram_id
    ).all()

def create_teacher_schedule(db: Session, schedule: schemas.TeacherScheduleCreate) -> models.TeacherSchedule:
    db_schedule = models.TeacherSchedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_teacher_schedule(
    db: Session,
    teacher_telegram_id: int,
    day_of_week: int,
    schedule_update: schemas.TeacherScheduleUpdate
) -> Optional[models.TeacherSchedule]:
    db_schedule = get_teacher_schedule(db, teacher_telegram_id, day_of_week)
    if not db_schedule:
        return None

    update_data = schedule_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_schedule, field, value)

    db_schedule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def generate_time_slots(
    start_time: str,
    end_time: str,
    booked_slots: List[str]
) -> List[schemas.TimeSlotResponse]:
    """Генерирует временные слоты для указанного времени работы"""
    slots = []

    # Парсим время
    start_hour, start_minute = map(int, start_time.split(':'))
    end_hour, end_minute = map(int, end_time.split(':'))

    current_hour = start_hour
    while current_hour < end_hour:
        time_str = f"{current_hour:02d}:00"
        is_booked = time_str in booked_slots

        slots.append(schemas.TimeSlotResponse(
            time=time_str,
            available=not is_booked,
            booked=is_booked,
            unavailable=False
        ))

        current_hour += 1

    return slots

def create_teacher_special_day(db: Session, special_day: schemas.TeacherSpecialDayCreate):
    db_day = models.TeacherSpecialDay(**special_day.dict())
    db.add(db_day)
    db.commit()
    db.refresh(db_day)
    return db_day

def get_teacher_special_days(db: Session, teacher_telegram_id: int, start: date, end: date):
    return db.query(models.TeacherSpecialDay).filter(
        models.TeacherSpecialDay.teacher_telegram_id == teacher_telegram_id,
        models.TeacherSpecialDay.date >= start,
        models.TeacherSpecialDay.date <= end
    ).all()

def update_teacher_special_day(
    db: Session, special_day_id: int, special_day_update: schemas.TeacherSpecialDayUpdate
):
    db_day = db.query(models.TeacherDaySchedule).filter(models.TeacherDaySchedule.id == special_day_id).first()
    if not db_day:
        return None

    if special_day_update.start_time is not None:
        db_day.start_time = special_day_update.start_time
    if special_day_update.end_time is not None:
        db_day.end_time = special_day_update.end_time
    if special_day_update.is_active is not None:
        db_day.is_active = special_day_update.is_active

    db.commit()
    db.refresh(db_day)
    return db_day


def delete_teacher_special_day(db: Session, special_day_id: int):
    db_day = db.query(models.TeacherDaySchedule).filter(models.TeacherDaySchedule.id == special_day_id).first()
    if not db_day:
        return False

    db.delete(db_day)
    db.commit()
    return True

def get_teacher_full_schedule(
    db: Session,
    teacher_telegram_id: int,
    start: date,
    end: date
) -> dict:
    # 1. Недельное расписание
    weekly_schedules = db.query(models.TeacherSchedule).filter(
        models.TeacherSchedule.teacher_telegram_id == teacher_telegram_id
    ).all()

    # 2. Разовые рабочие дни
    special_days = db.query(models.TeacherSpecialDay).filter(
        models.TeacherSpecialDay.teacher_telegram_id == teacher_telegram_id,
        models.TeacherSpecialDay.date >= start,
        models.TeacherSpecialDay.date <= end
    ).all()

    # 3. Не рабочие периоды
    unavailable_periods = db.query(models.TeacherUnavailable).filter(
        models.TeacherUnavailable.teacher_telegram_id == teacher_telegram_id,
        models.TeacherUnavailable.end_time >= start,
        models.TeacherUnavailable.start_time <= end
    ).all()

    return {
        "weekly_schedules": weekly_schedules,
        "special_days": special_days,
        "unavailable_periods": unavailable_periods
    }

