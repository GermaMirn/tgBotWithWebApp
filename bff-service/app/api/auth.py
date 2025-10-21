from fastapi import APIRouter, Depends, HTTPException, Header
from app.core.auth import get_current_user
from app.schemas.telegram import TelegramMiniAppPayload
from app.services.auth_service import login_or_register, login_user, get_user_by_token, get_user_by_id
from app.services.student_service import create_student_if_not_exists
from app.services.notification_service import notification_service
import httpx

router = APIRouter()

# URL для auth-service
AUTH_SERVICE_URL = "http://auth-service:8002"

@router.post("/miniapp")
async def miniapp_entry(data: TelegramMiniAppPayload):
    try:
        access_token = await login_or_register(data)
        if not access_token:
            raise HTTPException(status_code=500, detail="No access token returned from auth-service")

        # Автоматически создаем студента при первом входе
        await create_student_if_not_exists(data.id)

        if data.chat_id:
            try:
                user_id = await get_user_by_id(data.id)
                if user_id:
                    await notification_service.set_user_chat_id(user_id["id"], data.chat_id)
                    print('chat_id registered: success')
            except Exception as e:
                print(f"Warning: Chat registration failed: {e}")

        return {"access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.post("/login")
async def login(data: TelegramMiniAppPayload):
    try:
        access_token = await login_user(data)
        if not access_token:
            raise HTTPException(status_code=500, detail="No access token returned from auth-service")
        return {"access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.get("/me")
async def get_me(authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization[7:]  # Убираем "Bearer "
        user_data = await get_user_by_token(token)
        return {"user": user_data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.get("/user")
async def get_user(authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization[7:]  # Убираем "Bearer "
        user_data = await get_user_by_token(token)
        return {"user": user_data}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.get("/users")
async def get_users(
    role: str = None,
    authorization: str = Header(None)
):
    """Получает список пользователей с фильтрацией по роли"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header required")

        token = authorization[7:]  # Убираем "Bearer "

        async with httpx.AsyncClient() as client:
            url = f"{AUTH_SERVICE_URL}/auth/users"
            if role:
                url += f"?role={role}"

            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            elif response.status_code == 403:
                raise HTTPException(status_code=403, detail="Only admins can view users")
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/update-profile")
async def update_profile(
    profile_data: dict,
    authorization: str = Header(None)
):
    """Обновляет профиль пользователя (phone_number, email)"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header required")

        token = authorization[7:]  # Убираем "Bearer "

        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{AUTH_SERVICE_URL}/auth/update-profile",
                json=profile_data,
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
