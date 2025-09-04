from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.api.calendary import router as api_router

app = FastAPI(
    title="calendary-service",
    description="Сервис для управления расписанием занятий",
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
    return {"message": "Calendar Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "calendar-service"}

# Подключаем API роутеры
app.include_router(api_router)
