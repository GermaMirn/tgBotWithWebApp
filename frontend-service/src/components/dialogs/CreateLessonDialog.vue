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
              :options="languageOptions"
              optionLabel="label"
              optionValue="value"
              placeholder=" "
              class="w-full"
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
import { defineComponent, PropType, ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import FloatLabel from 'primevue/floatlabel'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'

export default defineComponent({
  name: 'CreateLessonDialog',
  components: { Dialog, Button, InputGroup, InputGroupAddon, FloatLabel, InputText, Dropdown, Calendar },
  props: {
    visible: { type: Boolean, required: true },
    lesson: { type: Object as PropType<any>, required: true },
    session: { type: Object as PropType<{ start_time: Date | null, end_time: Date | null }>, required: true },
    lessonTypes: { type: Array as PropType<{ label: string; value: string }[]>, required: true },
    languageOptions: { type: Array as PropType<{ label: string; value: string }[]>, required: true },
  },
  emits: ['update:visible', 'save', 'cancel'],
  setup(props, { emit }) {
    const visibleLocal = ref(props.visible)

    watch(() => props.visible, val => (visibleLocal.value = val))
    watch(visibleLocal, val => emit('update:visible', val))

    const close = () => (visibleLocal.value = false)
    const save = () => emit('save')

    return { visibleLocal, close, save }
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
