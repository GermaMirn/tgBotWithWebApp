# Groups Service

Сервис для управления группами студентов в образовательной платформе.

## Описание

Этот микросервис отвечает за:
- Создание и управление группами
- Участников групп
- Зачисления в группы
- Приглашения в группы
- Прогресс групп

## Запуск

### Локально
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

### Docker
```bash
docker build -t groups-service .
docker run -p 8005:8005 groups-service
```

## API Endpoints

- `GET /` - Статус сервиса
- `GET /health` - Проверка здоровья сервиса

## База данных

- PostgreSQL
- Порт: 5443
- База данных: groups_service

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных
- `REDIS_URL` - URL подключения к Redis