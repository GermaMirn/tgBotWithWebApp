# Telegram Bot Service

Python сервис для Telegram бота с интеграцией Mini App.

## 🎯 Назначение

- Обработка команд Telegram бота
- Интеграция с Telegram Mini App
- Управление пользователями
- Отправка уведомлений

## 🚀 Запуск

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp .env.example .env
# Отредактируйте .env файл

# Запуск бота
python main.py
```

### Docker

```bash
# Сборка образа
docker build -t tg-bot .

# Запуск контейнера
docker run --env-file .env tg-bot
```

## ⚙️ Конфигурация

### Переменные окружения (.env)

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Получение Telegram Bot Token

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен

### Команды бота

- `/start` - Приветствие и информация о боте
- `/help` - Справка по командам


## 🏗️ Архитектура

```
tgBot-services/
├── main.py              # Основной файл бота
├── bot/                 # Модули бота
│   ├── handlers.py      # Обработчики команд
│   └── utils.py         # Утилиты
├── api/                 # API клиенты
│   └── bff_client.py    # Клиент для BFF
├── config.py              # Конфигурация
└── requirements.txt     # Зависимости
```

