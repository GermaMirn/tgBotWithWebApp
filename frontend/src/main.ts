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

const app = createApp(App)
const pinia = createPinia()

const initTelegramApp = () => {
  try {
    const tgWebApp = window.Telegram?.WebApp;

    if (!tgWebApp) {
      console.log('Telegram WebApp not detected');
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
