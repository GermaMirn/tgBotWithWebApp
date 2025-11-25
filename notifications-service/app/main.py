from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import AsyncSessionLocal
from app.config import settings
from app.api.notifications import router
from app.core.rabbitmq import rabbitmq_client
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем подключение к RabbitMQ в фоне, не блокируя запуск приложения
    asyncio.create_task(rabbitmq_client.connect())
    yield
    await rabbitmq_client.close()

app = FastAPI(
    title="Notifications Service",
    description="Сервис для управления уведомлениями",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Notifications Service is running"}

@app.get("/health")
async def health_check():
    rabbitmq_status = "connected" if rabbitmq_client.is_connected else "disconnected"
    return {
        "status": "healthy",
        "service": "notifications-service",
        "rabbitmq": rabbitmq_status
    }

app.include_router(router)
