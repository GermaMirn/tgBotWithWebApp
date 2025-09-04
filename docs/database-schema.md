# Архитектура базы данных для микросервисов

## Обзор

Система построена на микросервисной архитектуре, где каждый сервис имеет свою собственную базу данных. Связь между сервисами осуществляется через `telegram_id` пользователя, который является уникальным идентификатором в Telegram.

## Принципы проектирования

1. **Разделение ответственности**: Каждый сервис отвечает за свою предметную область
2. **Связь через telegram_id**: Все сервисы используют `telegram_id` как ключ связи
3. **Независимость БД**: Каждый сервис может использовать свою СУБД
4. **Согласованность через BFF**: Backend for Frontend обеспечивает согласованность данных

## Схема сервисов

### 1. Auth Service (Пользователи)
**База данных**: PostgreSQL
**Ответственность**: Аутентификация и базовая информация о пользователях

#### Таблицы:
- `users` - основная таблица пользователей

#### Ключевые поля:
- `telegram_id` (BigInteger, уникальный) - основной ключ связи
- `role` - роль пользователя (student, teacher, admin)

### 2. Teachers Service (Преподаватели)
**База данных**: PostgreSQL
**Ответственность**: Профили преподавателей и их специализация

#### Таблицы:
- `teachers` - профили преподавателей
- `teacher_languages` - языки, которые преподает учитель
- `groups` - группы, созданные преподавателем

#### Связи:
- `teachers.telegram_id` → `users.telegram_id`

### 3. Students Service (Студенты)
**База данных**: PostgreSQL
**Ответственность**: Профили студентов и их прогресс

#### Таблицы:
- `students` - профили студентов
- `student_languages` - языки, которые изучает студент
- `group_enrollments` - зачисления в группы

#### Связи:
- `students.telegram_id` → `users.telegram_id`
- `group_enrollments.group_id` → `groups.id` (в groups-service)

### 4. Groups Service (Группы)
**База данных**: PostgreSQL
**Ответственность**: Управление группами студентов

#### Таблицы:
- `groups` - группы
- `group_members` - участники групп
- `group_invitations` - приглашения в группы
- `group_progress` - прогресс групп

#### Связи:
- `groups.teacher_telegram_id` → `teachers.telegram_id`
- `group_members.student_telegram_id` → `students.telegram_id`

### 5. Calendar Service (Расписание)
**База данных**: PostgreSQL
**Ответственность**: Управление расписанием занятий

#### Таблицы:
- `lessons` - занятия
- `lesson_participants` - участники занятий
- `lesson_attendance` - посещаемость
- `teacher_schedules` - расписание преподавателей
- `teacher_unavailable` - периоды недоступности

#### Связи:
- `lessons.teacher_telegram_id` → `teachers.telegram_id`
- `lessons.group_id` → `groups.id`
- `lesson_participants.student_telegram_id` → `students.telegram_id`

### 6. Notification Service (Уведомления)
**База данных**: PostgreSQL
**Ответственность**: Управление уведомлениями

#### Таблицы:
- `notifications` - уведомления
- `notification_templates` - шаблоны уведомлений
- `user_notification_settings` - настройки уведомлений пользователей
- `notification_logs` - логи уведомлений

#### Связи:
- `notifications.recipient_telegram_id` → `users.telegram_id`

## Схема связей

```
users (auth-service)
├── teachers (teachers-service) [telegram_id]
│   ├── groups (groups-service) [teacher_telegram_id]
│   │   ├── group_members (groups-service) [student_telegram_id]
│   │   └── lessons (calendar-service) [group_id]
│   └── lessons (calendar-service) [teacher_telegram_id]
├── students (students-service) [telegram_id]
│   ├── group_enrollments (students-service) [group_id]
│   └── lesson_participants (calendar-service) [student_telegram_id]
└── notifications (notification-service) [recipient_telegram_id]
```

## Стратегия связывания данных

### 1. Через BFF (Backend for Frontend)
BFF сервис выступает как точка интеграции для фронтенда:

```typescript
// Пример запроса в BFF
GET /api/user/profile/:telegram_id
{
  "user": { /* данные из auth-service */ },
  "teacher": { /* данные из teachers-service */ },
  "student": { /* данные из students-service */ },
  "groups": [ /* данные из groups-service */ ],
  "lessons": [ /* данные из calendar-service */ ]
}
```

### 2. Прямые вызовы между сервисами
Для операций, требующих данных из нескольких сервисов:

```python
# Пример в calendar-service
def create_lesson(teacher_telegram_id, group_id, student_telegram_ids):
    # Проверяем существование преподавателя
    teacher = teachers_service.get_teacher(teacher_telegram_id)

    # Проверяем существование группы
    group = groups_service.get_group(group_id)

    # Проверяем существование студентов
    students = students_service.get_students(student_telegram_ids)

    # Создаем занятие
    lesson = create_lesson_record(...)

    # Отправляем уведомления
    notification_service.send_lesson_notifications(...)
```

## Миграции и версионирование

Каждый сервис использует Alembic для управления миграциями:

```bash
# Создание миграции
alembic revision --autogenerate -m "Add new field"

# Применение миграций
alembic upgrade head
```

## Рекомендации по развертыванию

### 1. Базы данных
- Каждый сервис в отдельном контейнере
- Использование переменных окружения для конфигурации
- Резервное копирование каждой БД отдельно

### 2. Связи между сервисами
- Использование HTTP API для межсервисного взаимодействия
- Реализация retry механизмов
- Логирование всех межсервисных вызовов

### 3. Мониторинг
- Мониторинг каждой БД отдельно
- Метрики производительности запросов
- Алерты при недоступности сервисов

## Примеры запросов

### Получение профиля пользователя
```sql
-- В auth-service
SELECT * FROM users WHERE telegram_id = 123456789;

-- В teachers-service
SELECT * FROM teachers WHERE telegram_id = 123456789;

-- В students-service
SELECT * FROM students WHERE telegram_id = 123456789;
```

### Получение групп преподавателя
```sql
-- В groups-service
SELECT g.*, gm.student_telegram_id
FROM groups g
LEFT JOIN group_members gm ON g.id = gm.group_id
WHERE g.teacher_telegram_id = 123456789;
```

### Получение расписания студента
```sql
-- В calendar-service
SELECT l.*, lp.student_telegram_id
FROM lessons l
JOIN lesson_participants lp ON l.id = lp.lesson_id
WHERE lp.student_telegram_id = 123456789;
```

## Безопасность

1. **Изоляция данных**: Каждый сервис имеет доступ только к своей БД
2. **Валидация telegram_id**: Проверка существования пользователя перед операциями
3. **Аудит**: Логирование всех операций с данными
4. **Шифрование**: Чувствительные данные шифруются в БД