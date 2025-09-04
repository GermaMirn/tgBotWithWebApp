from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt
from jwt import PyJWTError
from app.utils.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Декодирование токена
def decode_token(token: str = Depends(oauth2_scheme)):
  try:
    payload = jwt.decode(
      token,
      settings.SECRET_KEY,
      algorithms=[settings.ALGORITHM]
    )
    return payload
  except PyJWTError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid or expired token",
      headers={"WWW-Authenticate": "Bearer"},
    )

# Генерация токена
def create_access_token(data: dict, role: str = "student"):
  expires = datetime.now(timezone.utc) + timedelta(minutes=30)
  return jwt.encode(
    {**data, "role": role, "exp": expires},
    settings.SECRET_KEY,
    algorithm=settings.ALGORITHM
  )

# Получение текущего пользователя
def get_current_user(token: str = Depends(oauth2_scheme)):
  return decode_token(token)
