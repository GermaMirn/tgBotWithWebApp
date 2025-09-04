<template>
  <Dialog
    v-model:visible="localVisible"
    modal
    header="Редактировать данные студента"
    :closable="true"
    :style="{ width: '90vw', maxWidth: '500px' }"
  >
    <div class="edit-form">
      <!-- Цели обучения -->
      <div class="field field--stack">
        <InputGroup>
          <InputGroupAddon>
            <i class="pi pi-chart-line"></i>
          </InputGroupAddon>
          <FloatLabel>
            <InputText
              id="study_goals"
              v-model="form.study_goals"
              placeholder=" "
              class="w-full"
              @focus="goalsTouched = true"
              @blur="goalsTouched = true"
            />
            <label for="study_goals">Цели обучения</label>
          </FloatLabel>
        </InputGroup>
        <small v-if="goalsError" class="p-error">Пожалуйста, заполните цель обучения</small>
      </div>
    </div>

    <template #footer>
      <Button label="Отмена" icon="pi pi-times" text @click="close" />
      <Button label="Сохранить" icon="pi pi-check" :loading="saving" @click="save" />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, ref, watch, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import FloatLabel from 'primevue/floatlabel'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'

export default defineComponent({
  name: 'EditStudentDialog',
  components: { Dialog, Button, InputText, FloatLabel, InputGroup, InputGroupAddon },
  props: {
    visible: { type: Boolean, required: true },
    modelValue: {
      type: Object as () => {
        telegram_id: string | null | undefined
        study_goals: string
        level: string | undefined
        preferred_languages: string[] | undefined
      },
      required: true
    },
    saving: { type: Boolean, default: false }
  },
  emits: ['update:visible', 'update:modelValue', 'save'],
  setup(props, { emit }) {
    const localVisible = ref(props.visible)
    const form = ref({ ...props.modelValue })
    const goalsTouched = ref(false)

    // Синхронизация формы с родителем
    watch(() => props.visible, (val) => {
      localVisible.value = val
      if (val) {
        // Когда диалог открылся, подставляем актуальные значения из родителя
        form.value = { ...props.modelValue }
        goalsTouched.value = false
      }
    })
    watch(localVisible, val => { emit('update:visible', val) })

    const goalsError = computed(() => goalsTouched.value && !form.value.study_goals?.trim())

    const close = () => { localVisible.value = false }
    const save = () => {
      if (!goalsError.value) {
        emit('update:modelValue', { ...form.value })
        emit('save')
      }
    }

    return { localVisible, form, goalsTouched, goalsError, close, save }
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
</style>
