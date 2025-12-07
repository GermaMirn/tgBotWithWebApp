import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import 'primevue/resources/themes/lara-light-blue/theme.css'
import 'primevue/resources/primevue.min.css'
import 'primeicons/primeicons.css'
import App from './App.vue'
import router from './router'
import { useUiStore } from './stores/ui'
import { initTelegramMock } from './utils/telegramMock'

const app = createApp(App)
const pinia = createPinia()

// Проверяем режим работы приложения
const isDevMode = import.meta.env.VITE_APP_MODE === 'dev';

// Функция для инициализации мока в dev режиме
const setupDevMode = () => {
  if (!isDevMode) return;

  // Ждем, пока скрипт Telegram загрузится (если он загружается)
  const checkAndOverride = () => {
    const tg = window.Telegram?.WebApp;

    // Если Telegram WebApp существует, но нет данных пользователя - перезаписываем моком
    if (tg && !tg.initDataUnsafe?.user) {
      console.log('[Dev Mode] Telegram WebApp exists but has no user data, overriding with mock...');
      initTelegramMock();
    } else if (!tg) {
      console.log('[Dev Mode] Telegram WebApp not found, initializing mock...');
      initTelegramMock();
    } else if (tg.initDataUnsafe?.user) {
      console.log('[Dev Mode] Telegram WebApp has user data, keeping it');
    }

    // Проверяем, что мок правильно инициализирован
    if (window.Telegram?.WebApp) {
      console.log('[Dev Mode] Final state, user data:', window.Telegram.WebApp.initDataUnsafe?.user);
    }
  };

  // Проверяем сразу
  checkAndOverride();

  // Также проверяем после небольшой задержки на случай, если скрипт загружается асинхронно
  setTimeout(checkAndOverride, 100);
  setTimeout(checkAndOverride, 500);
};

setupDevMode();

const initTelegramApp = () => {
  try {
    const tgWebApp = window.Telegram?.WebApp;

    if (!tgWebApp) {
      if (isDevMode) {
        console.log('[Dev Mode] Telegram WebApp not detected, using mock');
        // В dev режиме мок уже должен быть инициализирован
        const mockWebApp = window.Telegram?.WebApp;
        if (mockWebApp) {
          mockWebApp.expand();
          mockWebApp.enableClosingConfirmation();
          app.config.globalProperties.$tgWebApp = mockWebApp;
          app.provide('tgWebApp', mockWebApp);
          return true;
        }
      } else {
        console.log('Telegram WebApp not detected');
      }
      return false;
    }

    tgWebApp.expand();
    tgWebApp.enableClosingConfirmation();

    app.config.globalProperties.$tgWebApp = tgWebApp;
    app.provide('tgWebApp', tgWebApp);

    return true;
  } catch (e) {
    console.error('Error initializing Telegram WebApp:', e);
    return false;
  }
}

let isTelegram = initTelegramApp();

setTimeout(() => {
  if (!isTelegram) {
    isTelegram = initTelegramApp();
    console.log('Second attempt. Running in Telegram:', isTelegram);
  }
}, 500);

app.use(pinia);
app.use(PrimeVue);
app.use(ToastService);
app.use(router);

// Экспортируем глобальный ui-store
const ui = useUiStore();
app.config.globalProperties.$ui = ui;
app.provide('ui', ui);

app.mount('#app');
