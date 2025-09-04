# Telegram Bot с Web App - Микросервисная архитектура

Образовательная платформа для изучения языков с Telegram ботом и веб-приложением, построенная на микросервисной архитектуре.

## Архитектура

Система состоит из следующих микросервисов:

### 🏗️ Микросервисы

1. **Auth Service** - Аутентификация и управление пользователями
2. **Teachers Service** - Профили преподавателей и их специализация
3. **Students Service** - Профили студентов и их прогресс
4. **Groups Service** - Управление группами студентов
5. **Calendar Service** - Расписание занятий и управление временем
6. **Notifications Service** - Система уведомлений
7. **BFF (Backend for Frontend)** - Агрегация данных для фронтенда
8. **Telegram Bot** - Бот для Telegram
9. **Frontend** - Vue.js веб-приложение

### 🗄️ Базы данных

Каждый микросервис имеет свою собственную базу данных PostgreSQL:

- `auth_service` - пользователи и аутентификация
- `teachers_service` - профили преподавателей
- `students_service` - профили студентов
- `groups_service` - группы и участники
- `calendar_service` - расписание занятий
- `notifications_service` - уведомления

### 🔗 Связи между сервисами

Все сервисы связаны через `telegram_id` пользователя, который является уникальным идентификатором в Telegram. BFF сервис агрегирует данные из всех микросервисов для фронтенда.

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Node.js 18+ (для разработки фронтенда)
- Python 3.9+ (для разработки бэкенда)

### Развертывание

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd tgBotWithWebApp
```

2. **Настройка переменных окружения**
```bash
# Создайте .env файлы для каждого сервиса
cp auth-service/.env.example auth-service/.env
cp teachers-service/.env.example teachers-service/.env
# ... и так далее для всех сервисов
```

3. **Запуск всех сервисов**
```bash
docker-compose up -d
```

4. **Применение миграций**
```bash
# Для каждого сервиса
docker-compose exec auth-service alembic upgrade head
docker-compose exec teachers-service alembic upgrade head
docker-compose exec students-service alembic upgrade head
docker-compose exec groups-service alembic upgrade head
docker-compose exec calendar-service alembic upgrade head
docker-compose exec notifications-service alembic upgrade head
```

5. **Проверка работы**
- Frontend: http://localhost:3000
- BFF API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

## Структура проекта

```
tgBotWithWebApp/
├── auth-service/          # Сервис аутентификации
├── teachers-service/      # Сервис преподавателей
├── students-service/      # Сервис студентов
├── groups-service/        # Сервис групп
├── calendar-service/      # Сервис расписания
├── notifications-service/ # Сервис уведомлений
├── bff/                  # Backend for Frontend
├── tgBot-services/       # Telegram бот
├── frontend/             # Vue.js приложение
├── infrastructure/       # Nginx, Prometheus, Grafana
└── docs/                 # Документация
```

## API Endpoints

### BFF API (основной интерфейс)

- `GET /api/integration/user/profile/{telegram_id}` - Полный профиль пользователя
- `GET /api/integration/teacher/{telegram_id}/dashboard` - Дашборд преподавателя
- `GET /api/integration/student/{telegram_id}/dashboard` - Дашборд студента
- `GET /api/integration/group/{group_id}/details` - Детали группы
- `GET /api/integration/lessons/schedule` - Расписание занятий
- `GET /api/integration/dashboard/overview` - Обзор дашборда

### Микросервисы API

Каждый микросервис предоставляет REST API для своей предметной области:

- **Auth Service**: `/users/`, `/auth/`
- **Teachers Service**: `/teachers/`, `/teacher-languages/`
- **Students Service**: `/students/`, `/student-languages/`
- **Groups Service**: `/groups/`, `/group-members/`
- **Calendar Service**: `/lessons/`, `/teacher-schedules/`
- **Notifications Service**: `/notifications/`, `/templates/`

## Схема базы данных

### Основные принципы

1. **Разделение ответственности** - каждый сервис отвечает за свою область
2. **Связь через telegram_id** - все сервисы используют telegram_id как ключ связи
3. **Независимость БД** - каждый сервис может использовать свою СУБД
4. **Согласованность через BFF** - Backend for Frontend обеспечивает согласованность

### Ключевые таблицы

#### Auth Service
- `users` - основная таблица пользователей с telegram_id

#### Teachers Service
- `teachers` - профили преподавателей
- `teacher_languages` - языки преподавателей

#### Students Service
- `students` - профили студентов
- `student_languages` - языки студентов
- `group_enrollments` - зачисления в группы

#### Groups Service
- `groups` - группы
- `group_members` - участники групп
- `group_invitations` - приглашения

#### Calendar Service
- `lessons` - занятия
- `lesson_participants` - участники занятий
- `lesson_attendance` - посещаемость
- `teacher_schedules` - расписание преподавателей

#### Notifications Service
- `notifications` - уведомления
- `notification_templates` - шаблоны
- `user_notification_settings` - настройки пользователей

## Разработка

### Добавление нового поля в БД

1. **Обновите модель** в соответствующем сервисе
2. **Создайте миграцию**:
```bash
docker-compose exec <service-name> alembic revision --autogenerate -m "Add new field"
```
3. **Примените миграцию**:
```bash
docker-compose exec <service-name> alembic upgrade head
```

### Добавление нового API endpoint

1. **Создайте роутер** в соответствующем сервисе
2. **Добавьте схему** в schemas/
3. **Обновите BFF** если нужно агрегировать данные
4. **Обновите документацию**

### Тестирование

```bash
# Запуск тестов для всех сервисов
docker-compose exec auth-service pytest
docker-compose exec teachers-service pytest
# ... и так далее

# E2E тесты
npm run test:e2e
```

## Мониторинг

### Prometheus
- Метрики производительности
- Мониторинг сервисов
- Алерты

### Grafana
- Дашборды для мониторинга
- Визуализация метрик
- Отчеты

### Логирование
- Централизованное логирование через ELK Stack
- Структурированные логи в JSON формате
- Трейсинг запросов между сервисами

## Безопасность

1. **Аутентификация** - JWT токены
2. **Авторизация** - роли и права доступа
3. **Валидация данных** - Pydantic схемы
4. **Шифрование** - HTTPS, шифрование чувствительных данных
5. **Аудит** - логирование всех операций

## Масштабирование

### Горизонтальное масштабирование
```bash
# Масштабирование сервиса
docker-compose up -d --scale teachers-service=3
```

### Вертикальное масштабирование
- Увеличение ресурсов контейнеров
- Оптимизация запросов к БД
- Кэширование через Redis

## Развертывание в продакшене

1. **Подготовка серверов**
2. **Настройка CI/CD**
3. **Настройка мониторинга**
4. **Резервное копирование БД**
5. **SSL сертификаты**
6. **Доменные имена**

## Поддержка

- Документация API: `/docs` (Swagger UI)
- Логи: `docker-compose logs <service-name>`
- Мониторинг: Grafana дашборды
- Issues: GitHub Issues

## Лицензия

MIT License
