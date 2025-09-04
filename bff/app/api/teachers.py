from fastapi import APIRouter, HTTPException, Depends, Header
from app.core.auth import get_current_user
from app.schemas.teacher import TeacherCreate, TeacherResponse, TeacherUpdate
import httpx

router = APIRouter(tags=["teachers"])

TEACHERS_SERVICE_URL = "http://teachers-service:8003/teachers"

@router.get("/", response_model=list[TeacherResponse])
async def get_teachers():
    """
    Получение списка всех преподавателей с полными данными пользователей
    """
    try:
        async with httpx.AsyncClient() as client:
            # Получаем данные преподавателей
            response = await client.get(
                f"{TEACHERS_SERVICE_URL}/",
                timeout=10
            )
            if response.status_code != 200:
                error_text = await response.text()
                raise HTTPException(status_code=response.status_code, detail=error_text)

            teachers = response.json()

            # Для каждого преподавателя получаем полные данные пользователя из auth-service
            enriched_teachers = []
            for teacher in teachers:
                try:
                    # Получаем данные пользователя из auth-service
                    auth_response = await client.get(
                        f"http://auth-service:8002/auth/user-by-telegram/{teacher['telegram_id']}",
                        timeout=10
                    )

                    if auth_response.status_code == 200:
                        user_data = auth_response.json()
                        teacher['full_name'] = user_data.get('full_name', f'Преподаватель {teacher["id"][:8]}')
                    else:
                        teacher['full_name'] = f'Преподаватель {teacher["id"][:8]}'

                except Exception as e:
                    teacher['full_name'] = f'Преподаватель {teacher["id"][:8]}'

                # Обрабатываем сертификаты - если это строка, разбиваем по запятой
                if teacher.get('certificates') and isinstance(teacher['certificates'], str):
                    certificates = teacher['certificates'].split(',')
                    teacher['certificates'] = [cert.strip() for cert in certificates if cert.strip()]
                elif not teacher.get('certificates'):
                    teacher['certificates'] = []

                enriched_teachers.append(teacher)

            return enriched_teachers
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"teachers-service error: {str(e)}")

@router.post("/", response_model=TeacherResponse)
async def create_teacher(
    teacher_data: TeacherCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Создание преподавателя (с авторизацией)
    """
    try:
        async with httpx.AsyncClient() as client:
            teacher_payload = {
                "telegram_id": current_user.get("telegram_id"),
                "bio": teacher_data.bio,
                "specialization": teacher_data.specialization,
                "experience_years": teacher_data.experience_years,
                "education": teacher_data.education,
                "certificates": teacher_data.certificates,
                "hourly_rate": teacher_data.hourly_rate
            }
            teacher_payload = {k: v for k, v in teacher_payload.items() if v is not None}

            response = await client.post(
                f"{TEACHERS_SERVICE_URL}/",
                json=teacher_payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"teachers-service error: {str(e)}")

@router.post("/create-without-auth", response_model=TeacherResponse)
async def create_teacher_without_auth(
    teacher_data: TeacherCreate
):
    """
    Создание преподавателя без авторизации (для переключения ролей)
    """
    try:
        if not teacher_data.telegram_id:
            raise HTTPException(status_code=400, detail="telegram_id is required")

        async with httpx.AsyncClient() as client:
            teacher_payload = {
                "telegram_id": teacher_data.telegram_id,
                "bio": teacher_data.bio,
                "specialization": teacher_data.specialization,
                "experience_years": teacher_data.experience_years,
                "education": teacher_data.education,
                "certificates": teacher_data.certificates,
                "hourly_rate": teacher_data.hourly_rate
            }
            teacher_payload = {k: v for k, v in teacher_payload.items() if v is not None}

            response = await client.post(
                f"{TEACHERS_SERVICE_URL}/create-without-auth",
                json=teacher_payload,
                timeout=10
            )

            if response.status_code != 201:
                error_text = await response.text()
                raise HTTPException(status_code=response.status_code, detail=error_text)

            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"teachers-service error: {str(e)}")

@router.get("/me", response_model=TeacherResponse)
async def get_current_teacher(
    current_user: dict = Depends(get_current_user)
):
    """
    Получение данных текущего преподавателя
    """
    try:
        telegram_id = current_user.get('telegram_id')

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TEACHERS_SERVICE_URL}/by-telegram/{telegram_id}",
                timeout=10
            )

            if response.status_code != 200:
                error_text = await response.text()
                raise HTTPException(status_code=response.status_code, detail=error_text)

            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"teachers-service error: {str(e)}")

@router.put("/me", response_model=TeacherResponse)
async def update_current_teacher(
    teacher_data: TeacherUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Обновление данных текущего преподавателя
    """
    print(teacher_data)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{TEACHERS_SERVICE_URL}/by-telegram/{current_user.get('telegram_id')}",
                json={
                    "bio": teacher_data.bio,
                    "specialization": teacher_data.specialization,
                    "experience_years": teacher_data.experience_years,
                    "education": teacher_data.education,
                    "certificates": teacher_data.certificates,
                    "hourly_rate": teacher_data.hourly_rate
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"teachers-service error: {str(e)}")
