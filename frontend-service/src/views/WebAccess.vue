<template>
  <div class="web-access">
    <h1>Доступ только через Telegram</h1>
    <p>Для использования приложения, пожалуйста, откройте его через нашего бота:</p>
    <a :href="`https://t.me/${botUsername}`" class="tg-link">
      Открыть в Telegram
    </a>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  data() {
    return {
      botUsername: '@LangStudioBot'
    };
  }
});
</script>

<style scoped>
.web-access {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.tg-link {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #0088cc;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
}
</style>
