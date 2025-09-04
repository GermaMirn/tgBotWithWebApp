# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт (если нужно)
EXPOSE 8002

# Запускаем alembic миграции и приложение
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8002
