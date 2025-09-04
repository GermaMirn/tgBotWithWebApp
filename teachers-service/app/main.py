from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.config import settings
from app.api import teachers
from app.database import get_db


app = FastAPI(
  title="teachers-service",
  description="Сервис для управления преподавателями",
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
  return {"message": "Teachers Service is running"}

@app.get("/health")
async def health_check():
  return {"status": "healthy", "service": "teachers-service"}

# Подключаем роутеры
app.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
