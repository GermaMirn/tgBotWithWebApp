# Calendar Service

Сервис для управления расписанием занятий в образовательной платформе.

## Описание

Этот микросервис отвечает за:
- Создание и управление занятиями
- Участников занятий
- Посещаемость
- Расписание преподавателей
- Периоды недоступности

## Запуск

### Локально
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload
```

### Docker
```bash
docker build -t calendar-service .
docker run -p 8006:8006 calendar-service
```

## API Endpoints

- `GET /` - Статус сервиса
- `GET /health` - Проверка здоровья сервиса

## База данных

- PostgreSQL
- Порт: 5444
- База данных: calendar_service

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных
- `REDIS_URL` - URL подключения к Redis