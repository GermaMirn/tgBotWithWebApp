import httpx
from typing import Optional

STUDENTS_SERVICE_URL = "http://students-service:8004/students"

async def create_student_if_not_exists(telegram_id: int) -> Optional[dict]:
  """
  Создает студента, если он еще не существует
  """
  try:
      async with httpx.AsyncClient() as client:
          # Проверяем, существует ли уже студент
          response = await client.get(
              f"{STUDENTS_SERVICE_URL}/by-telegram/{telegram_id}",
              timeout=10
          )

          # Если студент уже существует, возвращаем его данные
          if response.status_code == 200:
              return response.json()

          # Если студент не найден, создаем нового
          if response.status_code == 404:
              create_response = await client.post(
                  f"{STUDENTS_SERVICE_URL}/",
                  json={
                      "telegram_id": telegram_id,
                      "level": "beginner",  # По умолчанию начальный уровень
                      "preferred_languages": [],  # Пустой список языков
                      "study_goals": None  # Цели обучения не указаны
                  },
                  timeout=10
              )
              create_response.raise_for_status()
              return create_response.json()

          response.raise_for_status()
          return response.json()

  except Exception as e:
      # Логируем ошибку, но не прерываем процесс аутентификации
      print(f"Error creating student: {str(e)}")
      return None

async def get_student_by_telegram_id(telegram_id: int) -> Optional[dict]:
  """
  Получает данные студента по telegram_id
  """
  try:
      async with httpx.AsyncClient() as client:
          response = await client.get(
              f"{STUDENTS_SERVICE_URL}/by-telegram/{telegram_id}",
              timeout=10
          )
          response.raise_for_status()
          return response.json()
  except Exception as e:
      print(f"Error getting student: {str(e)}")
      return None

async def update_student(telegram_id: int, student_data: dict) -> Optional[dict]:
  """
  Обновляет данные студента
  """
  try:
      async with httpx.AsyncClient() as client:
          response = await client.put(
              f"{STUDENTS_SERVICE_URL}/by-telegram/{telegram_id}",
              json=student_data,
              timeout=10
          )
          response.raise_for_status()
          return response.json()
  except Exception as e:
      print(f"Error updating student: {str(e)}")
      return None
