from fastapi import FastAPI
from app.database import AsyncSessionLocal
from app.api import role_switch, auth
from app.core.rabbitmq import rabbitmq_client
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
  title="auth-service",
  docs_url="/docs",
  openapi_url="/openapi.json"
)

# Подключаем роутеры
app.include_router(auth.router, tags=["auth"])
app.include_router(role_switch.router, tags=["role-switch"])

@app.on_event("startup")
async def startup_event():
    """Инициализация RabbitMQ при запуске приложения"""
    logger.info("Starting RabbitMQ connection...")
    asyncio.create_task(rabbitmq_client.connect())

@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие соединения с RabbitMQ при остановке"""
    logger.info("Closing RabbitMQ connection...")
    await rabbitmq_client.close()
