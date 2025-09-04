# app/services/availability.py
from datetime import datetime, timedelta, date
from typing import List, Tuple
import httpx
from ..schemas import TimeSlot

CALENDARY_SERVICE_URL = "http://calendary-service:8006"

async def get_week_schedule(self, teacher_telegram_id: int, day_of_week: int):
  url = f"{CALENDARY_SERVICE_URL}/calendary/teacher-schedule/{teacher_telegram_id}/{day_of_week}"
  async with httpx.AsyncClient(timeout=5.0) as client:
    r = await client.get(url)
    if r.status_code == 404:
      return None
    r.raise_for_status()
    return r.json()  # {start_time: "09:00", end_time: "18:00", is_available: true}

async def get_unavailable(self, teacher_telegram_id: int, day_start: datetime, day_end: datetime):
  # реализуй у себя ручку в calendary-service: /unavailable?from=&to=&teacher=
  url = f"{CALENDARY_SERVICE_URL}/calendary/unavailable"
  params = {
  "teacher_telegram_id": teacher_telegram_id,
  "from_ts": day_start.isoformat(),
  "to_ts": day_end.isoformat(),
  }
  async with httpx.AsyncClient(timeout=5.0) as client:
    r = await client.get(url, params=params)
    r.raise_for_status()
    return r.json()  # список интервалов [{start_time, end_time, ...}]

def _hours_range(start_hm: str, end_hm: str, the_date: date) -> Tuple[datetime, datetime]:
  sh, sm = map(int, start_hm.split(":"))
  eh, em = map(int, end_hm.split(":"))
  start = datetime(the_date.year, the_date.month, the_date.day, sh, sm)
  end = datetime(the_date.year, the_date.month, the_date.day, eh, em)
  return start, end

def _subtract_busy(base_intervals: List[Tuple[datetime, datetime]],
                  busy_intervals: List[Tuple[datetime, datetime]]) -> List[Tuple[datetime, datetime]]:
  # наивный вычитатель занятостей (можно улучшать)
  result = base_intervals[:]
  for b_start, b_end in busy_intervals:
    new_res = []
    for a_start, a_end in result:
      if b_end <= a_start or b_start >= a_end:
        new_res.append((a_start, a_end))
      else:
        if a_start < b_start:
          new_res.append((a_start, b_start))
        if b_end < a_end:
          new_res.append((b_end, a_end))
    result = new_res
  return result

async def compute_free_slots(
  *,
  teacher_telegram_id: int,
  the_date: date,
  existing_sessions: List[Tuple[datetime, datetime]],
) -> List[TimeSlot]:
  # 1) недельное окно
  dow = the_date.weekday()  # 0-6
  ws = await get_week_schedule(teacher_telegram_id, dow)
  if not ws or not ws.get("is_available"):
    return []

  day_start, day_end = _hours_range(ws["start_time"], ws["end_time"], the_date)
  base = [(day_start, day_end)]

  # 2) недоступности
  unavailable = await get_unavailable(teacher_telegram_id, day_start, day_end)
  busy_from_unavail = [(datetime.fromisoformat(x["start_time"]), datetime.fromisoformat(x["end_time"])) for x in unavailable]

  # 3) занятые сессии
  busy_from_sessions = existing_sessions

  # 4) вычитаем занятости
  free_intervals = _subtract_busy(base, busy_from_unavail + busy_from_sessions)

  # 5) собираем поквартально/почасово — для простоты почасовые слоты
  slots: List[TimeSlot] = []
  for start, end in free_intervals:
    cur = start
    while cur + timedelta(hours=1) <= end:
      slots.append(TimeSlot(start=cur, end=cur + timedelta(hours=1), available=True))
      cur += timedelta(hours=1)
  return slots
