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

    // Надежная проверка Telegram WebApp
    const checkTelegram = () => {
      const tg = window.Telegram?.WebApp;
      if (tg?.initData || tg?.initDataUnsafe?.user) {
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

          // Всегда делаем login для обновления данных
          await userStore.login(loginData);
        } else {
          // Если нет данных Telegram, но есть токен, проверяем его
          if (userStore.hasToken) {
            await userStore.fetchCurrentUser();
          }
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        // Если что-то пошло не так, очищаем данные
        userStore.logout();
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
      userStore
    };
  }
});
</script>

<template>
  <Default>
    <template v-if="isInitialized && isAuthChecked">
      <router-view v-if="isTelegram || $route.path === '/web' || $route.path.startsWith('/role-switch') || $route.path.startsWith('/groups/invite')" />
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
