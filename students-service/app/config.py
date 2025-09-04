from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  POSTGRES_USER: str
  POSTGRES_PASSWORD: str
  POSTGRES_DB: str
  DB_HOST: str

  @property
  def DATABASE_URL(self) -> str:
    return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:5432/{self.POSTGRES_DB}"

  class Config:
    env_file = ".env"
    env_file_encoding = 'utf-8'

settings = Settings()
