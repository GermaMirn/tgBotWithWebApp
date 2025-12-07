import axios from "axios";

// Динамически определяем baseURL на основе текущего домена
const getBaseURL = () => {
  // В dev режиме используем переменную окружения или прямой URL к API
  const isDevMode = import.meta.env.VITE_APP_MODE === 'dev';
  const devApiUrl = import.meta.env.VITE_API_URL;

  if (isDevMode && devApiUrl) {
    // Если указан URL API для dev режима, используем его
    return devApiUrl.endsWith('/api') ? devApiUrl : `${devApiUrl}/api`;
  }

  if (isDevMode) {
    // В dev режиме без переменной окружения используем прокси через Vite
    return "/api";
  }

  // В продакшене используем текущий домен + /api
  if (typeof window !== 'undefined') {
    const origin = window.location.origin;
    // Убираем порт если он стандартный (443 для https, 80 для http)
    let baseUrl = origin;
    if (origin.includes(':443')) {
      baseUrl = origin.replace(':443', '');
    } else if (origin.includes(':80') && origin.startsWith('http://')) {
      baseUrl = origin.replace(':80', '');
    }
    return `${baseUrl}/api`;
  }
  // Fallback для SSR или других случаев
  return "/api";
};

export const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    "Content-Type": "application/json",
  },
});

// Интерцептор для добавления JWT токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('jwt_token');
      // Убираем автоматическую перезагрузку
      // window.location.reload();
    }
    return Promise.reject(error);
  }
);
