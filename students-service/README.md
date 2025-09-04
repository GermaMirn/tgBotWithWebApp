# Students Service

Сервис для управления студентами в образовательной платформе.

## Описание

Этот микросервис отвечает за:
- Профили студентов
- Языки, которые изучает студент
- Контактную информацию

## Запуск

### Локально
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

### Docker
```bash
docker build -t students-service .
docker run -p 8004:8004 students-service
```

## API Endpoints

- `GET /` - Статус сервиса
- `GET /health` - Проверка здоровья сервиса

## База данных

- PostgreSQL
- Порт: 5442
- База данных: students_service

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных
- `REDIS_URL` - URL подключения к Redis