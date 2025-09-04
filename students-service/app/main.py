from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import students, groups

app = FastAPI(
  title="students-service",
  description="Сервис для управления студентами",
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

# Подключаем роутеры
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(groups.router, prefix="/groups", tags=["groups"])

@app.get("/")
async def root():
  return {"message": "Students Service is running"}

@app.get("/health")
async def health_check():
  return {"status": "healthy", "service": "students-service"}
