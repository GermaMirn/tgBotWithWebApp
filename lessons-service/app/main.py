from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import lessons
from app.core.rabbitmq import rabbitmq_client
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lessons Service",
    description="Сервис для управления уроками",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
async def root():
    return {"message": "Lessons Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "lossons-service"}


# Подключаем роутеры
app.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
