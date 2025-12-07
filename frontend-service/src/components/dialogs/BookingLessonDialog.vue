<template>
  <Dialog
    v-model:visible="visibleLocal"
    modal
    header="Подтверждение записи"
    :style="{ width: '90vw', maxWidth: '400px' }"
  >
    <div class="booking-details" v-if="slot && date">
      <div class="booking-info">
        <p><strong>Название:</strong> {{ slot.lesson.title }}</p>
        <p><strong>Описание:</strong> {{ slot.lesson.description }}</p>
        <p><strong>Дата:</strong> {{ formatDate(date) }}</p>
        <p><strong>Время:</strong> {{ slot.time }}</p>
        <p><strong>Тип:</strong> {{ getLessonTypeLabel(slot.lesson.lesson_type) }}</p>
        <p><strong>Язык:</strong> {{ getLanguageLabel(slot.lesson.language) }}</p>
        <p><strong>Уровень:</strong> {{ slot.lesson.level }}</p>

        <div class="detail-section">
          <h3>Учитель</h3>
          <div class="user-card">
            <i class="pi pi-user user-icon"></i>
            <span>{{ slot.teacher.full_name }}</span>
          </div>
        </div>

        <div v-if="slot.lesson.booked" class="detail-section">
          <h3>{{ slot.lesson.booked_by.type === 'student' ? 'Студент' : 'Группа'  }}</h3>
          <div
            v-if="slot.lesson.booked && slot.lesson.booked_by"
            class="user-card"
          >
            <i class="pi pi-user user-icon"></i>
            <div class="user-info">
              <div>
                <strong>{{ slot.lesson.booked_by.name || 'Неизвестный пользователь' }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <Button
        label="Отмена"
        icon="pi pi-times"
        text
        @click="close"
      />

      <!-- Если студент уже записан -->
      <Button
        v-if="slot?.lesson?.booked"
        label="Отменить запись"
        icon="pi pi-user-minus"
        class="p-button-danger cancel-btn"
        outlined
        @click="cancelBooking"
        :loading="loading"
      />

      <Button
        v-else-if="isTeacher && !slot?.lesson?.booked"
        label="Удалить сессию"
        icon="pi pi-trash"
        class="p-button-danger cancel-btn"
        outlined
        @click="deleteLesson"
        :loading="loading"
      />

      <!-- Если слот свободен -->
      <Button
        v-else="!isTeacher"
        label="Подтвердить"
        icon="pi pi-check"
        @click="confirm"
        :loading="loading"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, PropType, ref, watch, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import type { TimeSlotResponse } from '@/types/calendar'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'BookingDialog',
  components: { Dialog, Button },
  props: {
    visible: { type: Boolean, required: true },
    slot: { type: Object as PropType<TimeSlotResponse | null>, default: null },
    date: { type: Object as PropType<Date | null>, default: null },
    loading: { type: Boolean, default: false },
    lessonTypes: { 
      type: Array as PropType<{ label: string; value: string }[]>, 
      default: () => [
        { label: "Индивидуальный", value: "INDIVIDUAL" },
        { label: "Групповой", value: "GROUP" },
        { label: "Пробный", value: "TRIAL" }
      ]
    },
    languageOptions: { 
      type: Array as PropType<{ label: string; value: string }[]>, 
      default: () => []
    }
  },
  emits: ['update:visible', 'confirm', 'cancel', 'delete'],
  setup(props, { emit }) {
    const visibleLocal = ref(props.visible)
    const userStore = useUserStore()

    watch(() => props.visible, val => (visibleLocal.value = val))
    watch(visibleLocal, val => emit('update:visible', val))

    const close = () => (visibleLocal.value = false)
    const confirm = () => emit('confirm')
    const cancelBooking = () => emit('cancel')
    const deleteLesson = () => emit('delete')

    const formatDate = (date: Date) =>
      date.toLocaleDateString('ru-RU', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

    const isTeacher = computed(() => userStore.userData?.role === 'teacher')

    // Функция для получения названия типа урока
    const getLessonTypeLabel = (lessonType: string | null | undefined): string => {
      if (!lessonType) return 'Не указан'
      const type = props.lessonTypes.find(t => t.value === lessonType)
      return type ? type.label : lessonType
    }

    // Функция для получения названия языка
    const getLanguageLabel = (language: string | null | undefined): string => {
      if (!language) return 'Не указан'
      const lang = props.languageOptions.find(l => l.value === language)
      return lang ? lang.label : language
    }

    return { 
      visibleLocal, 
      isTeacher, 
      userStore, 
      close, 
      confirm, 
      deleteLesson, 
      cancelBooking, 
      formatDate,
      getLessonTypeLabel,
      getLanguageLabel
    }
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

.user-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  margin: 0.25rem 0;
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  border-bottom: 2px solid var(--surface-border);
  padding-bottom: 0.5rem;
}

.cancel-btn {
  font-size: 0.85rem;
  padding: 0.4rem 0.75rem;
  line-height: 1.2;
  border: none;
}
</style>
