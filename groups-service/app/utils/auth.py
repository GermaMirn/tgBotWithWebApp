from fastapi import Header, HTTPException, status, Depends
from typing import Optional
import httpx

AUTH_SERVICE_URL = "http://auth-service:8002/auth/user"

async def get_current_user(
  authorization: Optional[str] = Header(None)
):
  if not authorization or not authorization.startswith("Bearer "):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header required")

  token = authorization[7:]  # убираем "Bearer "

  async with httpx.AsyncClient() as client:
    try:
      response = await client.get(
        AUTH_SERVICE_URL,
        headers={"Authorization": f"Bearer {token}"}
      )
    except httpx.RequestError as e:
      raise HTTPException(status_code=502, detail=f"Auth service request error: {str(e)}")

  if response.status_code == 401:
    raise HTTPException(status_code=401, detail="Invalid or expired token")
  elif response.status_code != 200:
    raise HTTPException(status_code=response.status_code, detail="Auth service error")

  user_data = response.json()
  if not user_data.get("id"):
    raise HTTPException(status_code=401, detail="Invalid user data received")

  return user_data
