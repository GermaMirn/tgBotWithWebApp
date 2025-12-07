<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Настройки уведомлений"
    :style="{ width: '500px' }"
    :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
  >
    <div class="notification-settings">
      <!-- Сообщение если уведомления включены -->
      <Message
        v-if="localSettings.telegram_enabled"
        severity="success"
        :closable="false"
        class="mb-3"
      >
        <div class="flex flex-column gap-2">
          <div>✅ Уведомления включены. Вы будете получать уведомления в Telegram о занятиях и событиях.</div>
        </div>
      </Message>

      <!-- Сообщение если уведомления выключены -->
      <Message
        v-if="!localSettings.telegram_enabled"
        severity="warn"
        :closable="false"
        class="mb-3"
      >
        <div class="flex flex-column gap-2">
          <div>🔕 Уведомления выключены. Вы не будете получать уведомления в Telegram.</div>
        </div>
      </Message>

      <!-- Основной переключатель -->
      <div class="setting-item">
        <div class="setting-info">
          <label class="setting-label">Уведомления в Telegram</label>
          <span class="setting-description">Получать уведомления о занятиях и событиях</span>
        </div>
        <InputSwitch
          v-model="localSettings.telegram_enabled"
        />
      </div>

      <!-- Дополнительные настройки (можно добавить позже) -->
      <!-- <div class="setting-item" v-if="localSettings.telegram_enabled && hasChatId">
        <div class="setting-info">
          <label class="setting-label">Напоминания о занятиях</label>
          <span class="setting-description">Уведомления за 30 минут до начала</span>
        </div>
        <InputSwitch v-model="localSettings.lesson_reminders" />
      </div>

      <div class="setting-item" v-if="localSettings.telegram_enabled && hasChatId">
        <div class="setting-info">
          <label class="setting-label">Уведомления о группах</label>
          <span class="setting-description">Новые участники, изменения в группах</span>
        </div>
        <InputSwitch v-model="localSettings.group_notifications" />
      </div> -->
    </div>

    <template #footer>
      <Button
        label="Отмена"
        icon="pi pi-times"
        text
        @click="closeDialog"
      />
      <Button
        label="Сохранить"
        icon="pi pi-check"
        :loading="saving"
        @click="saveSettings"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputSwitch from 'primevue/inputswitch'
import Message from 'primevue/message'
import { NotificationSettings } from '@/types/notification'

export default defineComponent({
  name: 'NotificationSettingsDialog',
  components: {
    Dialog,
    Button,
    InputSwitch,
    Message
  },
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    settings: {
      type: Object as PropType<NotificationSettings | null>,
      required: true
    },
    saving: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:visible', 'save'],
  data() {
    return {
      localSettings: {} as NotificationSettings
    }
  },
  computed: {
    hasChatId(): boolean {
      return !!this.localSettings.chat_id
    }
  },
  watch: {
    visible(newVal) {
      if (newVal && this.settings) {
        this.localSettings = { ...this.settings }
      }
    }
  },
  methods: {
    closeDialog() {
      this.$emit('update:visible', false)
    },
    saveSettings() {
      this.$emit('save', this.localSettings)
    },
    openTelegramBot() {
      // Открываем Telegram бота с командой /notification
      // Замените YOUR_BOT_USERNAME на реальное имя вашего бота
      window.open('https://t.me/LangStudioBot?start=notification', '_blank')
      this.closeDialog()
    }
  }
})
</script>

<style scoped>
.notification-settings {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 0;
  border-bottom: 1px solid var(--surface-200);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info {
  flex: 1;
  margin-right: 1rem;
}

.setting-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.setting-description {
  display: block;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}
</style>
