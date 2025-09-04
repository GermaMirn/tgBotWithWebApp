import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authApi, type TelegramUser } from '@/services/api/auth';

export interface User {
  id: string; // UUID теперь строка
  telegram_id: number;
  username?: string;
  full_name: string;
  phone_number?: string;
  email?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
  role?: string;
  timezone: string;
}

// Функция для декодирования JWT токена
function decodeJWT(token: string) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null);
  const isLoading = ref(false);
  const isAuthenticated = ref(false);
  const isInitialized = ref(false);

  // Геттеры
  const hasToken = computed(() => {
    return !!localStorage.getItem('jwt_token');
  });

  const userData = computed(() => user.value);

  // Получаем роль пользователя из JWT токена или данных пользователя
  const userRole = computed(() => {
    // Сначала проверяем JWT токен
    const token = localStorage.getItem('jwt_token');
    if (token) {
      const payload = decodeJWT(token);
      if (payload?.role) {
        return payload.role;
      }
    }

    // Если в токене нет роли, берем из данных пользователя
    return user.value?.role || 'student';
  });

  // Проверяем, является ли пользователь админом
  const isAdmin = computed(() => {
    return userRole.value === 'admin';
  });

  // Проверяем, является ли пользователь учителем
  const isTeacher = computed(() => {
    return userRole.value === 'teacher';
  });

  // Проверяем, является ли пользователь студентом
  const isStudent = computed(() => {
    return userRole.value === 'student';
  });

  // Методы
  const login = async (userData: TelegramUser) => {
    try {
      isLoading.value = true;
      const response = await authApi.loginViaMiniApp(userData);

      // Сохраняем токен
      localStorage.setItem('jwt_token', response.access_token);

      // Всегда получаем актуальные данные пользователя после login
      await fetchCurrentUser();

      return response;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchCurrentUser = async () => {
    try {
      const userData = await authApi.getCurrentUser();
      user.value = userData.user;
      isAuthenticated.value = true;
      isInitialized.value = true;
    } catch (error) {
      console.error('Error fetching user data:', error);
      logout();
    }
  };

  const logout = () => {
    localStorage.removeItem('jwt_token');
    user.value = null;
    isAuthenticated.value = false;
    isInitialized.value = true;
  };

  const checkAuth = async () => {
    const token = localStorage.getItem('jwt_token');
    if (token && !isAuthenticated.value) {
      try {
        await fetchCurrentUser();
      } catch (error) {
        console.error('Auth check failed:', error);
        logout();
      }
    } else if (!token) {
      // Если нет токена, помечаем как инициализированное
      isInitialized.value = true;
    }
  };

  // Инициализация store при создании
  const initialize = async () => {
    if (!isInitialized.value) {
      await checkAuth();
    }
  };

  return {
    user,
    isLoading,
    isAuthenticated,
    isInitialized,
    hasToken,
    userData,
    userRole,
    isAdmin,
    isTeacher,
    isStudent,
    login,
    logout,
    fetchCurrentUser,
    checkAuth,
    initialize
  };
});
