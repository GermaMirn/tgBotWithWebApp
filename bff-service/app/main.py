from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, students, teachers, admin, calendar, groups, lessons, notification

app = FastAPI(
  title="BFF Server",
  root_path="/api",
  servers=[{"url": "/api", "description": "API Server"}],
  openapi_url="/api/openapi.json",
  docs_url="/api/docs"
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # поменять на свои домены в проде
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(students.router, tags=["students"])
app.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
app.include_router(admin.router, prefix="/role", tags=["admin"])
app.include_router(calendar.router, prefix="/calendary", tags=["calendar"])
app.include_router(groups.router, prefix="/groups", tags=["groups"])
app.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
app.include_router(notification.router, prefix="/notification", tags=["notification"])

@app.get("/")
async def root():
  return {"status": "ok"}
