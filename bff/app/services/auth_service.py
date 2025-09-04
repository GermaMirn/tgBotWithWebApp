import httpx
from app.schemas.telegram import TelegramMiniAppPayload
from typing import Optional

AUTH_SERVICE_URL = "http://auth-service:8002"

async def login_or_register(payload: TelegramMiniAppPayload) -> Optional[str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json={
                "telegram_id": payload.id,
                "username": payload.username,
                "full_name": payload.full_name
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get("access_token")

async def login_user(payload: TelegramMiniAppPayload) -> Optional[str]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/auth/login",
            json={
                "telegram_id": payload.id,
                "username": payload.username,
                "full_name": payload.full_name
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get("access_token")

async def get_user_by_token(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AUTH_SERVICE_URL}/auth/user",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()

async def get_user_by_id(telegram_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{AUTH_SERVICE_URL}/auth/user-by-telegram/{telegram_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
