# Notifications Service

Сервис для управления уведомлениями в образовательной платформе.

## Описание

Этот микросервис отвечает за:
- Отправку уведомлений
- Настройки уведомлений пользователей
- Логи уведомлений
- Различные каналы доставки (Telegram, Email, SMS)

## Запуск

### Локально
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload
```

### Docker
```bash
docker build -t notifications-service .
docker run -p 8007:8007 notifications-service
```

## API Endpoints

- `GET /` - Статус сервиса
- `GET /health` - Проверка здоровья сервиса

## База данных

- PostgreSQL
- Порт: 5445
- База данных: notifications_service

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных
- `REDIS_URL` - URL подключения к Redis