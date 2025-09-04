# Auth Service

Сервис аутентификации для Telegram Mini App с использованием JWT токенов и PostgreSQL.

## 🎯 Назначение

- Аутентификация пользователей Telegram Mini App
- Управление JWT токенами
- Хранение данных пользователей в PostgreSQL
- Синхронизация данных пользователей при изменениях в Telegram

## 🚀 Запуск

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл

# Запуск миграций
alembic upgrade head

# Запуск сервиса
uvicorn app.main:app --reload --port 8002
```

### Docker

```bash
# Сборка образа
docker build -t auth-service .

# Запуск контейнера
docker run -p 8002:8002 --env-file .env auth-service
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```bash
# База данных
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=auth_db
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Получение JWT_SECRET_KEY

```bash
# Генерация секретного ключа
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📊 База данных

### Схема

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR,
    full_name VARCHAR
);
```

### Миграции

```bash
# Создание новой миграции
alembic revision --autogenerate -m "description"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## 🔌 API Endpoints

### POST /login
Аутентификация пользователя Telegram Mini App

**Request:**
```json
{
  "telegram_id": 123456789,
  "username": "username",
  "full_name": "Full Name"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here",
  "token_type": "bearer"
}
```

### GET /auth/user
Получение данных текущего пользователя

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "username",
  "full_name": "Full Name"
}
```

### GET /users
Получение всех пользователей (для админов)

## 🏗️ Архитектура

```
app/
├── main.py              # FastAPI приложение
├── database.py          # Настройка БД
├── models.py            # SQLAlchemy модели
├── schemas.py           # Pydantic схемы
├── crud.py              # CRUD операции
├── auth.py              # JWT аутентификация
└── alembic/             # Миграции БД
```
