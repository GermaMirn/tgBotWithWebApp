<script lang="ts">
import { defineComponent, ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import Default from "@/layouts/default.vue";
import LoadingSpinner from '@/components/LoadingSpinner.vue';

export default defineComponent({
  components: { Default, LoadingSpinner },
  setup() {
    const router = useRouter();
    const userStore = useUserStore();
    const isTelegram = ref(false);
    const isInitialized = ref(false);
    const isAuthChecked = ref(false);

    // Проверяем режим работы приложения
    const isDevMode = import.meta.env.VITE_APP_MODE === 'dev';

    // Надежная проверка Telegram WebApp
    const checkTelegram = () => {
      const tg = window.Telegram?.WebApp;
      // В dev режиме всегда разрешаем доступ
      if (isDevMode) {
        isTelegram.value = true;
        if (tg) {
          tg.expand();
          tg.enableClosingConfirmation();
        }
      } else if (tg?.initData || tg?.initDataUnsafe?.user) {
        isTelegram.value = true;
        tg.expand();
        tg.enableClosingConfirmation();
      }
      isInitialized.value = true;
    };

    // Функция для безопасной обработки данных пользователя
    const sanitizeUserData = (userData: any) => {
      return {
        id: userData.id,
        username: userData.username && userData.username.trim() !== '' ? userData.username : '-',
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        full_name: [userData.first_name, userData.last_name].filter(Boolean).join(" ") || 'Пользователь'
      };
    };

    // Глобальная проверка аутентификации
    const checkAuthentication = async () => {
      try {
        const tg = window.Telegram?.WebApp;

        if (isDevMode) {
          console.log('[Dev Mode] Checking authentication, Telegram WebApp:', !!tg);
          console.log('[Dev Mode] User data:', tg?.initDataUnsafe?.user);
        }

        // Всегда делаем запрос на login для обновления данных пользователя
        if (tg?.initDataUnsafe?.user) {
          const userData = tg.initDataUnsafe.user;

          // Проверяем, что у пользователя есть хотя бы имя
          if (!userData.first_name && !userData.last_name) {
            console.error('User data is incomplete: missing name');
            throw new Error('Недостаточно данных пользователя');
          }

          // Безопасно обрабатываем данные пользователя
          const loginData = sanitizeUserData(userData);

          if (isDevMode) {
            console.log('[Dev Mode] Attempting login with:', loginData);
          }

          try {
            // Всегда делаем login для обновления данных
            await userStore.login(loginData);

            if (isDevMode) {
              console.log('[Dev Mode] Login successful, authenticated:', userStore.isAuthenticated);
            }
          } catch (loginError: any) {
            // В dev режиме, если ошибка сети/CORS, пропускаем аутентификацию
            if (isDevMode && (loginError.code === 'ERR_NETWORK' || loginError.message?.includes('CORS'))) {
              console.log('[Dev Mode] Network/CORS error during login, skipping authentication in dev mode');
              // Не выбрасываем ошибку, просто продолжаем без аутентификации
            } else {
              throw loginError;
            }
          }
        } else {
          // Если нет данных Telegram, но есть токен, проверяем его
          if (userStore.hasToken) {
            try {
              await userStore.fetchCurrentUser();
            } catch (fetchError: any) {
              // В dev режиме, если ошибка сети/CORS, пропускаем
              if (isDevMode && (fetchError.code === 'ERR_NETWORK' || fetchError.message?.includes('CORS'))) {
                console.log('[Dev Mode] Network/CORS error during fetch, skipping in dev mode');
              } else {
                throw fetchError;
              }
            }
          } else if (isDevMode) {
            // В dev режиме, если нет токена и нет данных пользователя, просто помечаем как проверенное
            console.log('[Dev Mode] No authentication data, but allowing access');
          }
        }
      } catch (error: any) {
        console.error('Authentication check failed:', error);
        // В dev режиме не очищаем данные при ошибке сети/CORS, чтобы можно было тестировать
        if (!isDevMode) {
          userStore.logout();
        } else if (error.code === 'ERR_NETWORK' || error.message?.includes('CORS')) {
          console.log('[Dev Mode] Network/CORS error, but continuing in dev mode');
        } else {
          console.log('[Dev Mode] Authentication error, but continuing in dev mode');
        }
      } finally {
        isAuthChecked.value = true;
      }
    };

    // Проверяем при загрузке
    onMounted(async () => {
      checkTelegram();

      // Проверяем аутентификацию после инициализации Telegram
      await checkAuthentication();

      // Дополнительная проверка через 500мс на случай поздней инициализации
      setTimeout(async () => {
        if (!isAuthChecked.value) {
          checkTelegram();
          await checkAuthentication();
        }
      }, 500);
    });

    // Контроль роутинга с учетом аутентификации
    watch(
      () => router.currentRoute.value.path,
      (newPath) => {
        // В dev режиме разрешаем доступ из браузера
        if (isDevMode) {
          return;
        }

        // Исключаем маршруты, которые должны работать вне Telegram Mini App
        const allowedPaths = ['/web', '/role-switch', '/groups/invite'];
        const isAllowedPath = allowedPaths.some(path => newPath.startsWith(path));

        if (isInitialized.value && !isTelegram.value && !isAllowedPath) {
          router.replace('/web');
        }
      },
      { immediate: true }
    );

    return {
      isTelegram,
      isInitialized,
      isAuthChecked,
      userStore,
      isDevMode
    };
  }
});
</script>

<template>
  <Default>
    <template v-if="isInitialized && isAuthChecked">
      <router-view v-if="isTelegram || isDevMode || $route.path === '/web' || $route.path.startsWith('/role-switch') || $route.path.startsWith('/groups/invite')" />
      <div v-else class="redirect-message">
        Перенаправление в Telegram Mini App...
      </div>
    </template>
    <div v-else class="loading">
      <LoadingSpinner />
    </div>
  </Default>
</template>

<style>
html, body, #app {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  letter-spacing: 1px;
  margin: 0;
  padding: 0;
  height: 100%;
}

.loading, .redirect-message {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 1.2rem;
  gap: 1rem;
}

.loading p {
  margin: 0;
  color: var(--text-color-secondary);
}
</style>
