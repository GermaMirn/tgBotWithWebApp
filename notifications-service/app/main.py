from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import AsyncSessionLocal
from app import models
from app.config import settings

async def get_db():
  async with AsyncSessionLocal() as session:
    yield session


app = FastAPI(
    title="Notifications Service",
    description="Сервис для управления уведомлениями",
    version="1.0.0"
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
    return {"status": "healthy", "service": "notifications-service"}

# Здесь будут импортироваться роутеры
# from app.api import notifications, settings, logs
# app.include_router(notifications.router, prefix="/api/v1")
# app.include_router(settings.router, prefix="/api/v1")
# app.include_router(logs.router, prefix="/api/v1")
