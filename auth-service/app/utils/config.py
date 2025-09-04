from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  SECRET_KEY: str
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
  POSTGRES_USER: str
  POSTGRES_PASSWORD: str
  POSTGRES_DB: str
  DB_HOST: str
  ADMIN_TELEGRAM_IDS: str = ""  # Список telegram_id админов через запятую

  @property
  def DATABASE_URL(self) -> str:
    return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:5432/{self.POSTGRES_DB}"

  def is_admin(self, telegram_id: int) -> bool:
    """Проверяет, является ли пользователь с данным telegram_id админом"""
    if not self.ADMIN_TELEGRAM_IDS:
      return False
    admin_ids = [int(id.strip()) for id in self.ADMIN_TELEGRAM_IDS.split(',') if id.strip()]
    return telegram_id in admin_ids

  class Config:
    env_file = ".env"
    env_file_encoding = 'utf-8'

settings = Settings()
