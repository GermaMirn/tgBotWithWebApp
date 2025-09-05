import { onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

export function useAuth() {
  const userStore = useUserStore();

  const initializeAuth = async () => {
    // Проверяем, есть ли токен
    if (userStore.hasToken) {
      // Если есть токен, но пользователь не аутентифицирован, загружаем данные
      if (!userStore.isAuthenticated) {
        await userStore.fetchCurrentUser();
      }
    } else {
      // Если нет токена, но есть данные Telegram, пытаемся войти
      const tg = window.Telegram?.WebApp;
      if (tg?.initDataUnsafe?.user) {
        const userData = tg.initDataUnsafe.user;
        try {
          await userStore.login(userData);
        } catch (error) {
          console.error('Auto-login failed:', error);
        }
      }
    }
  };

  onMounted(() => {
    initializeAuth();
  });

  return {
    userStore,
    initializeAuth
  };
}
