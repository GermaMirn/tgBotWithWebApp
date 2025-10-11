from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import List
from datetime import date, datetime, timedelta
from dateutil.parser import isoparse
from collections import defaultdict
import httpx

from ..schemas import calendar as schemas
from ..core.auth import get_current_user_telegram_id

router = APIRouter()

CALENDARY_SERVICE_URL = "http://calendary-service:8006"
LESSONS_SERVICE_URL = "http://lessons-service:8008"
GROUPS_SERVICE_URL = "http://groups-service:8005"
AUTH_SERVICE_URL = "http://auth-service:8002"

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
    current_user_id = await get_current_user_telegram_id(authorization)
    if not current_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async with httpx.AsyncClient() as client:
        # --- 1. Календарь из calendary-service ---
        try:
            response = await client.post(
                f"{CALENDARY_SERVICE_URL}/calendary/teacher-schedule/{teacher_telegram_id}/full",
                json={"start": req.start.isoformat(), "end": req.end.isoformat()},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Calendar service error: {str(e)}")

        # --- 2. Сессии из lessons-service ---
        try:
            lessons_resp = await client.post(
                f"{LESSONS_SERVICE_URL}/lessons/sessions/by-teacher",
                json={
                    "teacher_telegram_id": int(teacher_telegram_id),
                    "start": req.start.isoformat(),
                    "end": req.end.isoformat()
                },
                timeout=10
            )
            lessons_resp.raise_for_status()
            sessions = lessons_resp.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Lessons service error: {str(e)}")

        # --- 3. Подтягиваем имена студентов / групп ---
        for s in sessions:
            booked_by = s.get("booked_by")
            if not booked_by:
                continue

            try:
                if booked_by.get("type") == "student" and booked_by.get("id"):
                    resp = await client.get(f"{AUTH_SERVICE_URL}/auth/user-by-uuid/{booked_by['id']}", timeout=5)
                    if resp.status_code == 200:
                        student = resp.json()
                        s["booked_by"]["name"] = student.get("full_name")
                    else:
                        s["booked_by"]["name"] = ""

                elif booked_by.get("type") == "group" and booked_by.get("id"):
                    resp = await client.get(f"{GROUPS_SERVICE_URL}/groups/{booked_by['id']}", timeout=5)
                    if resp.status_code == 200:
                        group = resp.json()
                        s["booked_by"]["name"] = group.get("group_name")
                    else:
                        s["booked_by"]["name"] = ""
            except Exception as e:
                s["booked_by"]["name"] = ""

    # --- 4. Сортируем и собираем по дням ---
    sessions_by_date: dict[str, list] = defaultdict(list)
    for s in sessions:
        if not s.get("start_time"):
            continue
        try:
            start_dt = isoparse(s["start_time"])
        except Exception:
            continue
        day_key = start_dt.date().isoformat()

        session_obj = {
            "id": s.get("id"),
            "lesson_id": s.get("lesson_id"),
            "start_time": s.get("start_time"),
            "end_time": s.get("end_time"),
            "status": s.get("status"),
            "booked": s.get("booked", False),
            "booked_by": s.get("booked_by"),
            "lesson": s.get("lesson"),
        }
        sessions_by_date[day_key].append(session_obj)

    for dk in sessions_by_date:
        sessions_by_date[dk].sort(key=lambda x: isoparse(x["start_time"]))

    # --- 5. Генерим календарь по дням ---
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
        day_of_week = day_date.weekday()

        if day_iso in special_days:
            sd = special_days[day_iso]
            is_active = bool(sd.get("is_active", True))
            start_time = sd.get("start_time")
            end_time = sd.get("end_time")
        else:
            schedule_for_weekday = next((s for s in weekly_schedules if s["day_of_week"] == day_of_week), None)
            if schedule_for_weekday:
                is_active = bool(schedule_for_weekday.get("is_available", False))
                start_time = schedule_for_weekday.get("start_time")
                end_time = schedule_for_weekday.get("end_time")
            else:
                is_active = False
                start_time = None
                end_time = None

        for up in unavailable_periods:
            try:
                up_start = isoparse(up["start_time"]).date()
                up_end = isoparse(up["end_time"]).date()
                if up_start <= day_date <= up_end:
                    is_active = False
            except Exception:
                continue

        lessons: list = []

        # special days with booked/unavailable
        if day_iso in special_days:
            for b in special_days[day_iso].get("booked_slots", []):
                if isinstance(b, dict):
                    lessons.append(b)
                elif isinstance(b, str):
                    try:
                        start_str, end_str = b.split("-")
                        start_iso = f"{day_iso}T{start_str}:00+00:00"
                        end_iso = f"{day_iso}T{end_str}:00+00:00"
                        placeholder = {
                            "id": None,
                            "lesson_id": None,
                            "start_time": start_iso,
                            "end_time": end_iso,
                            "status": "UNAVAILABLE",
                            "lesson": None
                        }
                        lessons.append(placeholder)
                    except Exception:
                        continue

        if day_iso in sessions_by_date:
            lessons.extend(sessions_by_date[day_iso])

        days.append({
            "date": day_date,
            "is_active": is_active,
            "start_time": start_time,
            "end_time": end_time,
            "lessons": lessons
        })
    print(days)
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
