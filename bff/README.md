# BFF (Backend for Frontend)

Сервис-агрегатор API для Telegram Mini App, обеспечивающий единую точку входа для фронтенда.

## 🎯 Назначение

- Агрегация запросов к различным микросервисам
- Единая точка входа для фронтенда
- Трансформация данных между сервисами
- Управление аутентификацией и авторизацией

## 🚀 Запуск

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервиса
uvicorn app.main:app --reload --port 8000
```

### Docker

```bash
# Сборка образа
docker build -t bff-service .

# Запуск контейнера
docker run -p 8000:8000 bff-service
```

## 🔌 API Endpoints

### Аутентификация

#### POST /api/auth/miniapp
Вход через Telegram Mini App

**Request:**
```json
{
  "id": 123456789,
  "username": "username",
  "first_name": "First",
  "last_name": "Last"
}
```

**Response:**
```json
{
  "access_token": "jwt_token_here"
}
```

#### POST /api/auth/login
Альтернативный вход (дублирует miniapp)

#### GET /api/auth/me
Получение данных текущего пользователя

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "telegram_id": 123456789,
    "username": "username",
    "full_name": "Full Name"
  }
}
```

## 🏗️ Архитектура

```
app/
├── main.py              # FastAPI приложение
├── core/
│   ├── auth.py          # Аутентификация
│   └── config.py        # Конфигурация
├── api/
│   └── auth.py          # Auth endpoints
├── services/
│   └── auth_service.py  # Клиент для auth-service
└── schemas/
    └── telegram.py      # Pydantic схемы
```

## 🔗 Интеграции

### Auth Service
- **URL**: `http://auth-service:8002`
- **Endpoints**:
  - `POST /login` - аутентификация
  - `GET /auth/user` - получение пользователя
