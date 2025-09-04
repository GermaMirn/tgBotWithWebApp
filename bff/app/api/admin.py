from fastapi import APIRouter, Depends, HTTPException, Header
from app.core.auth import get_current_user
import httpx
from typing import Optional

router = APIRouter()

# URL для auth-service
AUTH_SERVICE_URL = "http://auth-service:8002"

@router.post("/admin/role-switch-links")
async def create_role_switch_link(
    link_data: dict,
    authorization: str = Header(None)
):
    """Создает ссылку для переключения роли (только для админов)"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization[7:]  # Убираем "Bearer "

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/role/admin/role-switch-links",
                json=link_data,
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 403:
                raise HTTPException(status_code=403, detail="Only admins can create role switch links")
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.get("/admin/role-switch-links")
async def get_role_switch_links(
    authorization: str = Header(None)
):
    """Получает список всех ссылок для переключения ролей (только для админов)"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization[7:]  # Убираем "Bearer "

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/role/admin/role-switch-links",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 403:
                raise HTTPException(status_code=403, detail="Only admins can view role switch links")
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.delete("/admin/role-switch-links/{link_id}")
async def delete_role_switch_link(
    link_id: str,
    authorization: str = Header(None)
):
    """Удаляет ссылку для переключения роли (только для админов)"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization[7:]  # Убираем "Bearer "

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{AUTH_SERVICE_URL}/role/admin/role-switch-links/{link_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 403:
                raise HTTPException(status_code=403, detail="Only admins can delete role switch links")
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.patch("/admin/role-switch-links/{link_id}/deactivate")
async def deactivate_role_switch_link(
    link_id: str,
    authorization: str = Header(None)
):
    """Деактивирует ссылку для переключения роли (только для админов)"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization[7:]  # Убираем "Bearer "

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{AUTH_SERVICE_URL}/role/admin/role-switch-links/{link_id}/deactivate",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 403:
                raise HTTPException(status_code=403, detail="Only admins can deactivate role switch links")
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.post("/role-switch")
async def switch_role(
    switch_data: dict
):
    """Переключает роль пользователя по токену ссылки"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/role/role-switch",
                json=switch_data
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.get("/role-switch/validate/{token}")
async def validate_role_switch_link(token: str):
    """Проверяет валидность ссылки для переключения роли"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/role/role-switch/validate/{token}"
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")

@router.post("/admin/switch-user-role")
async def switch_user_role(
    switch_data: dict,
    authorization: str = Header(None)
):
    """Прямое переключение роли пользователя (только для админов)"""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")

        token = authorization[7:]  # Убираем "Bearer "

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/role/admin/switch-user-role",
                json=switch_data,
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 403:
                raise HTTPException(status_code=403, detail="Only admins can switch user roles")
            elif response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"auth-service error: {str(e)}")
