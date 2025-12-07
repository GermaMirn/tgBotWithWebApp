<template>
  <Dialog
    v-model:visible="visibleLocal"
    modal
    header="Создать урок"
    :style="{ width: '90vw', maxWidth: '500px' }"
    :closable="false"
  >
    <div class="edit-form">
      <!-- Название урока -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-book"></i></InputGroupAddon>
          <FloatLabel>
            <InputText id="lesson_title" v-model="lesson.title" placeholder=" " class="w-full" />
            <label for="lesson_title">Название урока</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Тип урока -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-tags"></i></InputGroupAddon>
          <FloatLabel>
            <Dropdown
              id="lesson_type"
              v-model="lesson.lesson_type"
              :options="lessonTypes"
              optionLabel="label"
              optionValue="value"
              placeholder=" "
              class="w-full"
            />
            <label for="lesson_type">Тип урока</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Язык -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-globe"></i></InputGroupAddon>
          <FloatLabel>
            <Dropdown
              id="lesson_language"
              v-model="lesson.language"
              :options="filteredLanguageOptions"
              optionLabel="label"
              optionValue="value"
              placeholder=" "
              class="w-full"
              :loading="loadingTeacher"
              :disabled="loadingTeacher"
            />
            <label for="lesson_language">Язык</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Уровень -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-sort-alt"></i></InputGroupAddon>
          <FloatLabel>
            <InputText id="lesson_level" v-model="lesson.level" placeholder=" " class="w-full" />
            <label for="lesson_level">Уровень</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Описание -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-align-left"></i></InputGroupAddon>
          <FloatLabel>
            <InputText id="lesson_description" v-model="lesson.description" placeholder=" " class="w-full" />
            <label for="lesson_description">Описание</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Время начала -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-clock"></i></InputGroupAddon>
          <FloatLabel>
            <Calendar
              id="lesson_start_time"
              v-model="session.start_time"
              showTime
              hourFormat="24"
              placeholder=" "
              class="w-full"
              timeOnly
            />
            <label for="lesson_start_time">Время начала</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Время окончания -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-clock"></i></InputGroupAddon>
          <FloatLabel>
            <Calendar
              id="lesson_end_time"
              v-model="session.end_time"
              showTime
              hourFormat="24"
              placeholder=" "
              class="w-full"
              timeOnly
            />
            <label for="lesson_end_time">Время окончания</label>
          </FloatLabel>
        </InputGroup>
      </div>
    </div>

    <template #footer>
      <Button label="Отмена" icon="pi pi-times" text @click="close" />
      <Button label="Создать" icon="pi pi-check" @click="save" />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, PropType, ref, watch, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import FloatLabel from 'primevue/floatlabel'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import { useUserStore } from '@/stores/user'
import { teachersApi } from '@/services/api/teachers'

export default defineComponent({
  name: 'CreateLessonDialog',
  components: { Dialog, Button, InputGroup, InputGroupAddon, FloatLabel, InputText, Dropdown, Calendar },
  props: {
    visible: { type: Boolean, required: true },
    lesson: { type: Object as PropType<any>, required: true },
    session: { type: Object as PropType<{ start_time: Date | null, end_time: Date | null }>, required: true },
    lessonTypes: { type: Array as PropType<{ label: string; value: string }[]>, required: true },
    languageOptions: { type: Array as PropType<{ label: string; value: string }[]>, required: true },
    daySettings: {
      type: Object as PropType<{
        startTime: string,
        endTime: string,
        lessons: any[]
      }>,
      default: () => ({ startTime: '09:00', endTime: '18:00', lessons: [] })
    },
    selectedDate: { type: Date as PropType<Date | null>, default: null }
  },
  emits: ['update:visible', 'save', 'cancel'],
  setup(props, { emit }) {
    const userStore = useUserStore()
    const visibleLocal = ref(props.visible)
    const teacherLanguages = ref<string[]>([])
    const loadingTeacher = ref(false)

    // Фильтруем языки по преподавателю
    const filteredLanguageOptions = computed(() => {
      if (teacherLanguages.value.length === 0) {
        // Если языки преподавателя не загружены, показываем все
        return props.languageOptions
      }
      // Фильтруем только те языки, которые есть у преподавателя
      return props.languageOptions.filter(lang =>
        teacherLanguages.value.some(tl =>
          tl.toLowerCase().includes(lang.label.toLowerCase()) ||
          tl.toLowerCase().includes(lang.value.toLowerCase())
        )
      )
    })

    // Загружаем языки преподавателя
    const loadTeacherLanguages = async () => {
      if (!userStore.isTeacher || !userStore.userData?.telegram_id) return

      loadingTeacher.value = true
      try {
        const teacher = await teachersApi.getCurrentTeacher()
        if (teacher?.specialization) {
          // Парсим specialization: "Математика (Языки: Английский, Китайский)"
          const langMatch = teacher.specialization.match(/Языки:\s*([^)]+)/i)
          if (langMatch) {
            teacherLanguages.value = langMatch[1].split(',').map(l => l.trim())
          } else {
            // Если формат другой, пытаемся извлечь языки из всей строки
            teacherLanguages.value = [teacher.specialization]
          }
        }
      } catch (error) {
        console.error('Error loading teacher languages:', error)
      } finally {
        loadingTeacher.value = false
      }
    }

    // Вычисляем начальное время на основе рабочего времени и занятых слотов
    const calculateStartTime = (): Date => {
      const today = new Date()
      const selectedDate = props.selectedDate || today

      // Парсим время начала рабочего дня
      const [startHour, startMinute] = props.daySettings.startTime.split(':').map(Number)
      const startTime = new Date(selectedDate)
      startTime.setHours(startHour, startMinute, 0, 0)

      // Получаем занятые слоты
      const bookedSlots = props.daySettings.lessons || []

      // Находим следующий свободный час
      let currentTime = new Date(startTime)
      const endTime = new Date(selectedDate)
      const [endHour, endMinute] = props.daySettings.endTime.split(':').map(Number)
      endTime.setHours(endHour, endMinute, 0, 0)

      // Проверяем каждый час, пока не найдем свободный
      while (currentTime < endTime) {
        const isBooked = bookedSlots.some((lesson: any) => {
          // Проверяем разные форматы данных
          let lessonStart: Date | null = null
          let lessonEnd: Date | null = null

          if (lesson.start_time && lesson.end_time) {
            lessonStart = new Date(lesson.start_time)
            lessonEnd = new Date(lesson.end_time)
          } else if (lesson.raw?.start_time && lesson.raw?.end_time) {
            lessonStart = new Date(lesson.raw.start_time)
            lessonEnd = new Date(lesson.raw.end_time)
          }

          if (!lessonStart || !lessonEnd) return false

          // Проверяем пересечение: текущее время попадает в занятый слот
          return currentTime >= lessonStart && currentTime < lessonEnd
        })

        if (!isBooked) {
          return new Date(currentTime)
        }

        // Переходим к следующему часу
        currentTime.setHours(currentTime.getHours() + 1)
      }

      // Если все время занято, возвращаем время начала смены
      return new Date(startTime)
    }

    // Вычисляем время окончания (начало + 1 час)
    const calculateEndTime = (startTime: Date): Date => {
      const endTime = new Date(startTime)
      endTime.setHours(endTime.getHours() + 1)
      return endTime
    }

    // Инициализируем время при открытии диалога
    watch(() => props.visible, async (val) => {
      visibleLocal.value = val
      if (val) {
        // Загружаем языки преподавателя
        await loadTeacherLanguages()

        // Устанавливаем время начала и окончания
        const startTime = calculateStartTime()
        const endTime = calculateEndTime(startTime)

        // Обновляем session через родительский компонент
        if (props.session) {
          props.session.start_time = startTime
          props.session.end_time = endTime
        }
      }
    })

    watch(visibleLocal, val => emit('update:visible', val))

    // Обновляем время окончания при изменении времени начала
    watch(() => props.session.start_time, (newStartTime) => {
      if (newStartTime && props.session) {
        props.session.end_time = calculateEndTime(newStartTime)
      }
    })

    const close = () => (visibleLocal.value = false)
    const save = () => emit('save')

    return {
      visibleLocal,
      close,
      save,
      filteredLanguageOptions,
      loadingTeacher
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
</style>
