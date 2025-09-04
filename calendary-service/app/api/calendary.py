from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/calendary")

@router.post("/teacher-schedule/{teacher_telegram_id}/full", response_model=schemas.TeacherScheduleFullResponse)
def get_teacher_full_schedule_endpoint(
    teacher_telegram_id: str,
    req: schemas.FullScheduleRequest,
    db: Session = Depends(get_db)
):
    """Возвращает полное расписание учителя на диапазон дат"""
    start = req.start
    end = req.end
    teacher_telegram_id = int(teacher_telegram_id)

    data = crud.get_teacher_full_schedule(db, teacher_telegram_id, start, end)
    return schemas.TeacherScheduleFullResponse(**data)


# Endpoints для TeacherSchedule (недельное расписание)
@router.post("/teacher-schedule", response_model=schemas.TeacherScheduleResponse)
def create_teacher_schedule(
    schedule: schemas.TeacherScheduleCreate,
    db: Session = Depends(get_db)
):
    """Создать недельное расписание учителя"""
    # Проверяем, не существует ли уже расписание на этот день недели
    existing = crud.get_teacher_schedule(
        db, schedule.teacher_telegram_id, schedule.day_of_week
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Расписание на этот день недели уже существует"
        )

    return crud.create_teacher_schedule(db, schedule)

@router.get("/teacher-schedule/{teacher_telegram_id}", response_model=List[schemas.TeacherScheduleResponse])
def get_teacher_schedules(
    teacher_telegram_id: int,
    db: Session = Depends(get_db)
):
    """Получить все недельные расписания учителя"""
    return crud.get_teacher_schedules(db, teacher_telegram_id)

@router.get("/teacher-schedule/{teacher_telegram_id}/{day_of_week}", response_model=schemas.TeacherScheduleResponse)
def get_teacher_schedule(
    teacher_telegram_id: int,
    day_of_week: int,
    db: Session = Depends(get_db)
):
    """Получить недельное расписание учителя на конкретный день недели"""
    schedule = crud.get_teacher_schedule(db, teacher_telegram_id, day_of_week)
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    return schedule

@router.put("/teacher-schedule/{teacher_telegram_id}/{day_of_week}", response_model=schemas.TeacherScheduleResponse)
def update_teacher_schedule(
    teacher_telegram_id: int,
    day_of_week: int,
    schedule_update: schemas.TeacherScheduleUpdate,
    db: Session = Depends(get_db)
):
    """Обновить недельное расписание учителя"""
    schedule = crud.update_teacher_schedule(
        db, teacher_telegram_id, day_of_week, schedule_update
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Расписание не найдено")
    return schedule

@router.post("/teacher-special-day", response_model=schemas.TeacherSpecialDayResponse)
def create_teacher_special_day_endpoint(
    special_day: schemas.TeacherSpecialDayCreate,
    db: Session = Depends(get_db)
):
    """Создать разовый рабочий день учителя"""
    return crud.create_teacher_special_day(db, special_day)


@router.get("/teacher-special-day/{teacher_telegram_id}", response_model=List[schemas.TeacherSpecialDayResponse])
def get_teacher_special_days_endpoint(
    teacher_telegram_id: int,
    start: date = Query(...),
    end: date = Query(...),
    db: Session = Depends(get_db)
):
    """Получить разовые рабочие дни учителя в диапазоне дат"""
    return crud.get_teacher_special_days(db, teacher_telegram_id, start, end)

@router.put("/teacher-special-day/{special_day_id}", response_model=schemas.TeacherSpecialDayResponse)
def update_teacher_special_day_endpoint(
    special_day_id: int,
    special_day_update: schemas.TeacherSpecialDayUpdate,
    db: Session = Depends(get_db)
):
    """Обновить разовый рабочий день учителя"""
    updated = crud.update_teacher_special_day(db, special_day_id, special_day_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Разовый рабочий день не найден")
    return updated

@router.delete("/teacher-special-day/{special_day_id}", response_model=dict)
def delete_teacher_special_day_endpoint(
    special_day_id: int,
    db: Session = Depends(get_db)
):
    """Удалить разовый рабочий день учителя"""
    deleted = crud.delete_teacher_special_day(db, special_day_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Разовый рабочий день не найден")
    return {"status": "deleted"}
