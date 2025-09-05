<template>
  <Dialog
    v-model:visible="visibleLocal"
    modal
    header="Подтверждение записи"
    :style="{ width: '90vw', maxWidth: '400px' }"
  >
    <div class="booking-details" v-if="slot && date">
      <div class="booking-info">
        <p><strong>Дата:</strong> {{ formatDate(date) }}</p>
        <p><strong>Время:</strong> {{ slot.time }}</p>
      </div>
    </div>

    <template #footer>
      <Button
        label="Отмена"
        icon="pi pi-times"
        text
        @click="close"
      />
      <Button
        label="Подтвердить"
        icon="pi pi-check"
        @click="confirm"
        :loading="loading"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, PropType, ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import type { TimeSlotResponse } from '@/types/calendar'

export default defineComponent({
  name: 'BookingDialog',
  components: { Dialog, Button },
  props: {
    visible: { type: Boolean, required: true },
    slot: { type: Object as PropType<TimeSlotResponse | null>, default: null },
    date: { type: Object as PropType<Date | null>, default: null },
    loading: { type: Boolean, default: false }
  },
  emits: ['update:visible', 'confirm', 'cancel'],
  setup(props, { emit }) {
    const visibleLocal = ref(props.visible)

    watch(() => props.visible, val => (visibleLocal.value = val))
    watch(visibleLocal, val => emit('update:visible', val))

    const close = () => (visibleLocal.value = false)
    const confirm = () => emit('confirm')

    const formatDate = (date: Date) =>
      date.toLocaleDateString('ru-RU', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

    return { visibleLocal, close, confirm, formatDate }
  }
})
</script>

<style scoped>
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding-top: 1.25rem;
}

:deep(.p-floatlabel .p-inputicon-left + label),
:deep(.p-floatlabel .p-input-icon-left + label) {
  margin-left: 2.25rem !important;
}

:deep(.p-dialog-content) {
  overflow: visible;
  position: relative;
  z-index: 0;
}

:deep(.p-floatlabel > label) {
  position: absolute;
  z-index: 2;
}

:deep(.p-floatlabel .p-iconfield + label),
:deep(.p-floatlabel .p-input-icon-left + label),
:deep(.p-floatlabel .p-inputicon-left + label) {
  left: 2.25rem !important;
}

:deep(.p-iconfield .p-inputtext),
:deep(.p-iconfield .p-inputmask input),
:deep(.p-input-icon-left .p-inputtext),
:deep(.p-input-icon-left .p-inputmask input),
:deep(.p-inputicon-left .p-inputtext),
:deep(.p-inputicon-left .p-inputmask input) {
  padding-left: 2.25rem;
}

.field-label {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.field-help {
  color: var(--text-color-secondary);
  font-size: 0.8rem;
}

.field--stack + .field--stack {
  margin-top: 0.75rem;
}

.error-text {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}
</style>
