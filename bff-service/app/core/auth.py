from fastapi import Header, HTTPException
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

def get_current_user(authorization: str = Header(...)):
  try:
    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
      raise HTTPException(status_code=401, detail="Invalid auth scheme")

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    payload["token"] = token

    return payload
  except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="Token has expired")
  except jwt.InvalidTokenError:
    raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user_telegram_id(authorization: str = Header(None)):
  """Получить telegram_id текущего пользователя из токена"""
  if not authorization:
    return None

  try:
    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
      return None

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    telegram_id = payload.get('telegram_id')
    return telegram_id
  except Exception as e:
    return None
