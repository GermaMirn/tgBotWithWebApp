import httpx
from typing import Optional

TEACHERS_SERVICE_URL = "http://teachers-service:8003/teachers"

async def create_teacher_if_not_exists(telegram_id: int) -> Optional[dict]:
    """
    Создает преподавателя, если он еще не существует
    """
    try:
        async with httpx.AsyncClient() as client:
            # Проверяем, существует ли уже преподаватель
            response = await client.get(
                f"{TEACHERS_SERVICE_URL}/by-telegram/{telegram_id}",
                timeout=10
            )

            # Если преподаватель уже существует, возвращаем его данные
            if response.status_code == 200:
                return response.json()

            # Если преподаватель не найден, создаем нового
            if response.status_code == 404:
                create_response = await client.post(
                    f"{TEACHERS_SERVICE_URL}/",
                    json={
                        "telegram_id": telegram_id,
                        "bio": None,
                        "specialization": None,
                        "experience_years": 0,
                        "education": None,
                        "certificates": None,
                        "hourly_rate": None
                    },
                    timeout=10
                )
                create_response.raise_for_status()
                return create_response.json()

            response.raise_for_status()
            return response.json()

    except Exception as e:
        # Логируем ошибку, но не прерываем процесс аутентификации
        print(f"Error creating teacher: {str(e)}")
        return None

async def get_teacher_by_telegram_id(telegram_id: int) -> Optional[dict]:
    """
    Получает данные преподавателя по telegram_id
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TEACHERS_SERVICE_URL}/by-telegram/{telegram_id}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error getting teacher: {str(e)}")
        return None

async def update_teacher(telegram_id: int, teacher_data: dict) -> Optional[dict]:
    """
    Обновляет данные преподавателя
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{TEACHERS_SERVICE_URL}/by-telegram/{telegram_id}",
                json=teacher_data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error updating teacher: {str(e)}")
        return None
