# Teachers Service

Сервис для управления преподавателями в образовательной платформе.

## Описание

Этот микросервис отвечает за:
- Профили преподавателей
- Языки, которые преподает учитель
- Профессиональную информацию

## Запуск

### Локально
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Docker
```bash
docker build -t teachers-service .
docker run -p 8003:8003 teachers-service
```

## API Endpoints

- `GET /` - Статус сервиса
- `GET /health` - Проверка здоровья сервиса

## База данных

- PostgreSQL
- Порт: 5441
- База данных: teachers_service

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных
- `REDIS_URL` - URL подключения к Redis