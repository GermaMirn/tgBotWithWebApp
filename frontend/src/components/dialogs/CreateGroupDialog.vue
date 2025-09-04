<template>
  <Dialog
    v-model:visible="visibleLocal"
    modal
    :header="mode === 'create' ? 'Создать новую группу' : 'Редактировать группу'"
    :style="{ width: '90vw', maxWidth: '500px' }"
    :closable="true"
  >
    <div class="edit-form">
      <!-- Название -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-users"></i></InputGroupAddon>
          <FloatLabel>
            <InputText
              id="group_name"
              v-model="form.name"
              placeholder=" "
              class="w-full"
            />
            <label for="group_name">Название группы</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Описание -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-align-left"></i></InputGroupAddon>
          <FloatLabel>
            <Textarea
              id="group_description"
              v-model="form.description"
              rows="3"
              autoResize
              placeholder=" "
              class="w-full"
            />
            <label for="group_description">Описание</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Язык -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-globe"></i></InputGroupAddon>
          <FloatLabel>
            <Dropdown
              id="group_language"
              v-model="form.language"
              :options="languageOptions"
              optionLabel="label"
              optionValue="value"
              placeholder=" "
              class="w-full"
            />
            <label for="group_language">Язык</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Уровень -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-sort-alt"></i></InputGroupAddon>
          <FloatLabel>
            <Dropdown
              id="group_level"
              v-model="form.level"
              :options="levelOptions"
              optionLabel="label"
              optionValue="value"
              placeholder=" "
              class="w-full"
            />
            <label for="group_level">Уровень</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Тип -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-tags"></i></InputGroupAddon>
          <FloatLabel>
            <Dropdown
              id="group_type"
              v-model="form.group_type"
              :options="typeOptions"
              optionLabel="label"
              optionValue="value"
              placeholder=" "
              class="w-full"
            />
            <label for="group_type">Тип группы</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Макс. студентов -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-user-plus"></i></InputGroupAddon>
          <FloatLabel>
            <InputNumber
              id="max_students"
              v-model="form.max_students"
              :min="1"
              :max="100"
              placeholder=" "
              class="w-full"
            />
            <label for="max_students">Максимум студентов</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Дата начала -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-calendar"></i></InputGroupAddon>
          <FloatLabel>
            <Calendar
              id="start_date"
              v-model="startDateProxy"
              dateFormat="yy-mm-dd"
              showIcon
              placeholder=" "
              class="w-full"
            />
            <label for="start_date">Дата начала</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- Дата окончания -->
      <div class="field">
        <InputGroup>
          <InputGroupAddon><i class="pi pi-calendar-times"></i></InputGroupAddon>
          <FloatLabel>
            <Calendar
              id="end_date"
              v-model="endDateProxy"
              dateFormat="yy-mm-dd"
              showIcon
              placeholder=" "
              class="w-full"
            />
            <label for="end_date">Дата окончания</label>
          </FloatLabel>
        </InputGroup>

        <p v-if="validationError" class="error-text">
          {{ validationError }}
        </p>
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
        label="Сохранить"
        icon="pi pi-check"
        @click="save"
        :loading="loading"
      />
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
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'
import type { Group } from '@/types/groups'

export default defineComponent({
  name: 'CreateGroupDialog',
  components: {
    Dialog, Button, InputGroup, InputGroupAddon,
    FloatLabel, InputText, Textarea, Dropdown,
    InputNumber, Calendar
  },
  props: {
    visible: { type: Boolean, required: true },
    mode: { type: String as PropType<'create' | 'edit'>, required: true },
    form: { type: Object as PropType<Partial<Group>>, required: true },
    loading: { type: Boolean, default: false },
    languageOptions: { type: Array as PropType<any[]>, required: true },
    levelOptions: { type: Array as PropType<any[]>, required: true },
    typeOptions: { type: Array as PropType<any[]>, required: true },
  },
  emits: ['update:visible', 'save', 'cancel'],
  computed: {
    startDateProxy: {
      get(): Date | null {
        return this.form.start_date ? new Date(this.form.start_date) : null
      },
      set(val: Date | null) {
        this.form.start_date = val ? val.toISOString().slice(0, 10) : null
      }
    },
    endDateProxy: {
      get(): Date | null {
        return this.form.end_date ? new Date(this.form.end_date) : null
      },
      set(val: Date | null) {
        this.form.end_date = val ? val.toISOString().slice(0, 10) : null
      }
    }
  },
  setup(props, { emit }) {
    const visibleLocal = ref(props.visible)
    const validationError = ref<string | null>(null)

    // Синхронизируем при изменении пропса
    watch(() => props.visible, val => {
      visibleLocal.value = val
    })

    watch(visibleLocal, val => {
      emit('update:visible', val)
    })

    const close = () => {
      visibleLocal.value = false
    }

    const save = () => {
      if (!validateDates()) return
      emit('save', props.form)
    }

    const startDateProxy = computed<Date | null>({
      get: () => props.form.start_date ? new Date(props.form.start_date) : null,
      set: (val: Date | null) => { props.form.start_date = val ? val.toISOString().slice(0,10) : null }
    })

    const endDateProxy = computed<Date | null>({
      get: () => props.form.end_date ? new Date(props.form.end_date) : null,
      set: (val: Date | null) => { props.form.end_date = val ? val.toISOString().slice(0,10) : null }
    })

    const validateDates = () => {
      if (props.form.start_date && props.form.end_date) {
        const start = new Date(props.form.start_date)
        const end = new Date(props.form.end_date)

        if (end < start) {
          validationError.value = 'Дата окончания не может быть раньше даты начала'
          return false
        }
      }
      validationError.value = null
      return true
    }

    return { visibleLocal,  validationError, startDateProxy, endDateProxy, close, save, validateDates }
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
