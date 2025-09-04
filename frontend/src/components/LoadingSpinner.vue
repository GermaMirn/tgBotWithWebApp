<template>
  <div class="loading-container">
    <ProgressSpinner
      :style="{ width: '50px', height: '50px' }"
      strokeWidth="4"
      fill="var(--surface-ground)"
      animationDuration=".5s"
    />
    <p class="loading-text">{{ message }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import ProgressSpinner from 'primevue/progressspinner';

export default defineComponent({
  name: 'LoadingSpinner',
  components: {
    ProgressSpinner
  },
  props: {
    message: {
      type: String,
      default: 'Загрузка...'
    }
  }
});
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 1rem;
}

.loading-text {
  font-size: 1.1rem;
  color: var(--text-color-secondary);
  margin: 0;
}
</style>