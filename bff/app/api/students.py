from fastapi import APIRouter, HTTPException, Depends
from app.core.auth import get_current_user
from app.schemas.student import StudentCreate, StudentResponse
import httpx

router = APIRouter(prefix="/students", tags=["students"])

STUDENTS_SERVICE_URL = "http://students-service:8004/students"

@router.post("/", response_model=StudentResponse)
async def create_student(
    student_data: StudentCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Создание студента (автоматически при первом входе)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{STUDENTS_SERVICE_URL}/",
                json={
                    "telegram_id": current_user.get("telegram_id"),
                    "level": student_data.level,
                    "preferred_languages": student_data.preferred_languages,
                    "study_goals": student_data.study_goals
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"students-service error: {str(e)}")

@router.get("", response_model=list[StudentResponse])
async def get_students():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{STUDENTS_SERVICE_URL}/",
                params={
                    "skip": 0,
                    "limit": 10000
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"students-service error: {str(e)}")

@router.get("/me", response_model=StudentResponse)
async def get_current_student(
    current_user: dict = Depends(get_current_user)
):
    """
    Получение данных текущего студента
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{STUDENTS_SERVICE_URL}/by-telegram/{current_user.get('telegram_id')}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"students-service error: {str(e)}")

@router.put("/me", response_model=StudentResponse)
async def update_current_student(
    student_data: StudentCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Обновление данных текущего студента
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{STUDENTS_SERVICE_URL}/by-telegram/{current_user.get('telegram_id')}",
                json={
                    "level": student_data.level,
                    "preferred_languages": student_data.preferred_languages,
                    "study_goals": student_data.study_goals
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"students-service error: {str(e)}")
