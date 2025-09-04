from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import groups

app = FastAPI(
    title="groups-service",
    description="Сервис для управления группами",
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
    return {"message": "Groups Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "groups-service"}

# Подключаем роутеры
app.include_router(groups.router, prefix="/groups", tags=["groups"])
