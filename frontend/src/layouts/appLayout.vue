<script lang="ts">
import { defineComponent } from 'vue';
import SidebarMenu from '@/components/SidebarMenu.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import Toast from 'primevue/toast';
import { useUiStore } from '@/stores/ui'

export default defineComponent({
  name: 'AppLayout',
  components: { SidebarMenu, LoadingSpinner, Toast },
  data() {
    return {
      isLoading: false,
      ui: useUiStore()
    }
  }
});
</script>

<template>
  <div class="app-layout">
    <!-- Глобальный Toast -->
    <Toast />
    <!-- Глобальный Loading -->
    <div v-if="ui.isGlobalLoading" class="global-loading-overlay">
      <LoadingSpinner :message="ui.loadingMessage" />
    </div>
    <!-- Бургер-меню -->
    <SidebarMenu />
    <!-- Основной контент -->
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-width: 100vw;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

.main-content {
  flex: 1;
  margin: 0;
  padding: 0;
  width: 100%;
  background-color: #F8F8F9;
  color: #5E606D;
}

.global-loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(2px);
  z-index: 9998;
  display: grid;
  place-items: center;
}
</style>

<style>
.p-toast {
  top: 0.8rem !important;
  left: 50% !important;
  right: auto !important;
  transform: translateX(-50%);
  min-width: unset;
  width: 78vw;
  max-width: 560px;
  max-height: 50vh;
  overflow-y: auto;
  pointer-events: auto;
  z-index: 9999 !important;
}

.p-toast .p-toast-message {
  width: 100%;
  padding: 0.75rem 1rem !important;
  font-size: 0.98rem !important;
  line-height: 1.35;
  border-radius: 12px !important;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12) !important;
  backdrop-filter: saturate(110%);
}

/* Расстояние между несколькими тостами */
.p-toast .p-toast-message + .p-toast-message {
  margin-top: 0.5rem;
}

/* Контент и иконки */
.p-toast .p-toast-message .p-toast-message-content {
  align-items: flex-start;
  gap: 0.6rem;
}
.p-toast .p-toast-message .p-toast-message-icon {
  font-size: 1.15rem;
  margin-right: 0.6rem;
}
.p-toast .p-toast-message .p-toast-message-text {
  font-size: 0.98rem;
}

/* Кнопка закрытия (увеличенный тач-таргет) */
.p-toast .p-toast-message .p-toast-icon-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: grid;
  place-content: center;
  margin-left: 0.25rem;
  opacity: 0.8;
  transition: background 0.15s ease, opacity 0.15s ease;
}
.p-toast .p-toast-message .p-toast-icon-close:hover {
  opacity: 1;
  background: var(--surface-hover, rgba(0,0,0,0.05));
}

/* Цветовые варианты (мягкие фоны и акцентные бордюры) */
.p-toast .p-toast-message.p-toast-message-success {
  background: #ecfdf5 !important; /* нежный зелёный */
  border-left: 6px solid #22c55e !important;
  color: #14532d !important;
}
.p-toast .p-toast-message.p-toast-message-info {
  background: #eef6ff !important; /* нежный синий */
  border-left: 6px solid #3b82f6 !important;
  color: #1e3a8a !important;
}
.p-toast .p-toast-message.p-toast-message-warn {
  background: #fff7ed !important; /* нежный оранжевый */
  border-left: 6px solid #f59e0b !important;
  color: #78350f !important;
}
.p-toast .p-toast-message.p-toast-message-error {
  background: #fef2f2 !important; /* нежный красный */
  border-left: 6px solid #ef4444 !important;
  color: #7f1d1d !important;
}

@media (max-width: 768px) {
  .p-toast {
    top: 0.6rem !important;
    width: 88vw;
    max-width: 88vw;
  }
  .p-toast .p-toast-message {
    padding: 0.65rem 0.8rem !important;
    font-size: 0.95rem !important;
    border-radius: 10px !important;
  }
  .p-toast .p-toast-message .p-toast-message-icon {
    font-size: 1.05rem;
    margin-right: 0.5rem;
  }
  .p-toast .p-toast-message .p-toast-message-text {
    font-size: 0.95rem;
  }
  .p-toast .p-toast-message .p-toast-icon-close {
    width: 28px;
    height: 28px;
    border-radius: 8px;
  }
}
</style>
