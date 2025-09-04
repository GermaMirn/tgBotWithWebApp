import axios from "axios";

export const api = axios.create({
  baseURL: "https://bravely-inviting-flea.cloudpub.ru/api",
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
