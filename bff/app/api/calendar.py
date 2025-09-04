from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import List
from datetime import date, datetime, timedelta, timezone
from dateutil.parser import isoparse
import httpx

from ..schemas import calendar as schemas
from ..core.auth import get_current_user_telegram_id

router = APIRouter()

CALENDARY_SERVICE_URL = "http://calendary-service:8006"
LESSONS_SERVICE_URL = "http://lessons-service:8008"

# ---------- Teacher Weekly Schedule ----------
@router.post("/teacher-schedule", response_model=schemas.TeacherScheduleResponse)
async def create_teacher_schedule_bff(
    schedule: schemas.TeacherScheduleCreate,
    authorization: str = Header(None)
):
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-schedule",
                json=schedule.dict(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")


@router.get("/teacher-schedule/{teacher_telegram_id}", response_model=List[schemas.TeacherScheduleResponse])
async def get_teacher_schedules_bff(
    teacher_telegram_id: int,
    authorization: str = Header(None)
):
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-schedule/{teacher_telegram_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")


@router.get("/teacher-schedule/{teacher_telegram_id}/{day_of_week}", response_model=schemas.TeacherScheduleResponse)
async def get_teacher_schedule_bff(
    teacher_telegram_id: int,
    day_of_week: int,
    authorization: str = Header(None)
):
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-schedule/{teacher_telegram_id}/{day_of_week}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Schedule not found")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")


@router.put("/teacher-schedule/{teacher_telegram_id}/{day_of_week}", response_model=schemas.TeacherScheduleResponse)
async def update_teacher_schedule_bff(
    teacher_telegram_id: int,
    day_of_week: int,
    schedule_update: schemas.TeacherScheduleUpdate,
    authorization: str = Header(None)
):
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-schedule/{teacher_telegram_id}/{day_of_week}",
                json=schedule_update.dict(exclude_unset=True),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Schedule not found")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")


# ---------- Teacher Special Day ----------
@router.post("/teacher-special-day", response_model=schemas.TeacherSpecialDayResponse)
async def create_teacher_special_day_bff(
    special_day: schemas.TeacherSpecialDayCreate,
    authorization: str = Header(None)
):
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = special_day.dict()
    if isinstance(payload.get("date"), (date, datetime)):
        payload["date"] = payload["date"].isoformat()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-special-day",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")



@router.get("/teacher-special-day/{teacher_telegram_id}", response_model=List[schemas.TeacherSpecialDayResponse])
async def get_teacher_special_days_bff(
    teacher_telegram_id: int,
    start: date = Query(...),
    end: date = Query(...),
    authorization: str = Header(None)
):
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-special-day/{teacher_telegram_id}",
                params={"start": start, "end": end},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")


# ---------- Full Schedule ----------
@router.post("/teacher-schedule/{teacher_telegram_id}/full", response_model=schemas.CalendarResponse)
async def get_teacher_full_schedule_bff(
    teacher_telegram_id: str,
    req: schemas.FullScheduleRequest,
    authorization: str = Header(None)
):
    print(req)
    # Авторизация
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        # 1. Берём данные из calendary-service
        try:
            response = await client.post(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-schedule/{teacher_telegram_id}/full",
                json={
                    "start": req.start.isoformat(),
                    "end": req.end.isoformat()
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            print("Calendary-service response:", data)
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")

        start_date = req.start.isoformat()
        end_date = req.end.isoformat()

        # 2. Берём сессии (уроки) из lessons-service
        try:
            lessons_resp = await client.post(
                f"{LESSONS_SERVICE_URL}/lessons/sessions/by-teacher",
                json={
                    "teacher_telegram_id": teacher_telegram_id,
                    "start": start_date,
                    "end": end_date
                },
                timeout=10
            )
            lessons_resp.raise_for_status()
            sessions = lessons_resp.json()
            print("Lessons-service response:", sessions)
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Lessons service error: {str(e)}")

    # 3. Группируем уроки по дате
    sessions_by_date = {}
    for s in sessions:
        start_dt = isoparse(s["start_time"])
        end_dt = isoparse(s["end_time"])
        day_key = start_dt.date().isoformat()

        slot_str = f"{start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}"
        if day_key not in sessions_by_date:
            sessions_by_date[day_key] = []
        sessions_by_date[day_key].append(slot_str)

    print("Grouped sessions by date:", sessions_by_date)

    # 4. Формируем календарь
    days = []
    start_date = req.start
    end_date = req.end
    delta = end_date - start_date

    weekly_schedules = data.get("weekly_schedules", [])
    special_days = {sd["date"]: sd for sd in data.get("special_days", [])}
    unavailable_periods = data.get("unavailable_periods", [])

    for i in range(delta.days + 1):
        day_date = start_date + timedelta(days=i)
        day_iso = day_date.isoformat()
        day_of_week = day_date.weekday()  # 0=Пн, 6=Вс

        if day_iso in special_days:
            sd = special_days[day_iso]
            is_active = True
            start_time = sd["start_time"]
            end_time = sd["end_time"]
        else:
            schedule_for_weekday = next(
                (s for s in weekly_schedules if s["day_of_week"] == day_of_week),
                None
            )
            if schedule_for_weekday:
                is_active = schedule_for_weekday["is_available"]
                start_time = schedule_for_weekday["start_time"]
                end_time = schedule_for_weekday["end_time"]
            else:
                is_active = False
                start_time = None
                end_time = None

        # Проверка unavailable_periods
        for up in unavailable_periods:
            up_start = isoparse(up["start_time"])
            up_end = isoparse(up["end_time"])
            if up_start.date() <= day_date <= up_end.date():
                is_active = False

        # booked_slots = спецдень + сессии из lessons-service
        booked_slots = []
        if day_iso in special_days:
            booked_slots.extend(special_days[day_iso].get("booked_slots", []))
        if day_iso in sessions_by_date:
            booked_slots.extend(sessions_by_date[day_iso])

        day_info = {
            "date": day_iso,
            "is_active": is_active,
            "start_time": start_time,
            "end_time": end_time,
            "booked_slots": booked_slots
        }
        print("Day info:", day_info)
        days.append(day_info)

    print("Final calendar:", days)
    return schemas.CalendarResponse(
        teacher_telegram_id=int(teacher_telegram_id),
        days=days
    )


# ---------- Teacher Special Day (update, delete) ----------
@router.put("/teacher-special-day/{special_day_id}", response_model=schemas.TeacherSpecialDayResponse)
async def update_teacher_special_day_bff(
    special_day_id: int,
    special_day_update: schemas.TeacherSpecialDayUpdate,
    authorization: str = Header(None)
):
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-special-day/{special_day_id}",
                json=special_day_update.dict(exclude_unset=True),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Special day not found")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")


@router.delete("/teacher-special-day/{special_day_id}", response_model=dict)
async def delete_teacher_special_day_bff(
    special_day_id: int,
    authorization: str = Header(None)
):
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-special-day/{special_day_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Special day not found")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")
