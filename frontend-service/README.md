# Frontend - Telegram Mini App

Vue 3 приложение для Telegram Mini App с TypeScript и PrimeVue.

## 🎯 Назначение

- Telegram Mini App интерфейс
- Аутентификация через Telegram
- Управление состоянием пользователя
- Современный UI с PrimeVue компонентами

## 🚀 Запуск

### Локальная разработка

```bash
# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev

# Сборка для продакшена
npm run build

# Предпросмотр сборки
npm run preview
```

### Docker

```bash
# Сборка образа
docker build -t frontend .

# Запуск контейнера
docker run -p 5173:5173 frontend
```

## 🛠️ Технологии

- **Vue 3** - JavaScript фреймворк
- **TypeScript** - Типизация
- **Vite** - Сборщик
- **PrimeVue 3** - UI компоненты
- **Pinia** - State management
- **Axios** - HTTP клиент

## 🏗️ Архитектура

```
src/
├── main.ts              # Точка входа
├── App.vue              # Корневой компонент
├── router/              # Vue Router
├── stores/              # Pinia stores
│   └── user.ts          # User state
├── services/            # API сервисы
│   └── api/             # API клиенты
├── components/          # Vue компоненты
│   └── LoadingSpinner.vue
├── views/               # Страницы
│   └── Home.vue         # Главная страница
└── types/               # TypeScript типы
```

## 🔌 API Интеграция

### Конфигурация

```typescript
// services/api/axios.ts
export const api = axios.create({
  baseURL: "https://invitingly-dazzling-lyrebird.cloudpub.ru/api",
  headers: {
    "Content-Type": "application/json",
  },
});
```

### Endpoints

- `POST /auth/miniapp` - Вход через Mini App
- `POST /auth/login` - Альтернативный вход
- `GET /auth/me` - Получение пользователя

## 🔐 Аутентификация

### Flow

1. **Инициализация** - Получение данных из `window.Telegram.WebApp`
2. **Login** - Отправка данных в BFF
3. **Token Storage** - Сохранение JWT в localStorage
4. **State Management** - Обновление Pinia store

### Telegram Integration

```typescript
// Инициализация Telegram Mini App
window.Telegram.WebApp.ready();
window.Telegram.WebApp.expand();

// Получение данных пользователя
const user = window.Telegram.WebApp.initDataUnsafe.user;
```

## 📱 Telegram Mini App

### Конфигурация

```typescript
// main.ts
function initTelegramApp() {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.ready();
    window.Telegram.WebApp.expand();
  }
}
```

## 🚀 Развертывание

### Production Build

```bash
# Сборка
npm run build

# Результат в dist/
```

### Docker Production

```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```
