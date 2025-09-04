from fastapi import FastAPI
from app.database import AsyncSessionLocal
from app.api import role_switch, auth

app = FastAPI(
  title="auth-service",
  docs_url="/docs",
  openapi_url="/openapi.json"
)

# Подключаем роутеры
app.include_router(auth.router, tags=["auth"])
app.include_router(role_switch.router, tags=["role-switch"])
