<template>
  <Dialog
    v-model:visible="visibleLocal"
    modal
    header="Редактировать данные учителя"
    :closable="true"
    :style="{ width: '90vw', maxWidth: '500px' }"
  >
    <div class="edit-form">
      <!-- О себе -->
      <InputGroup class="field" style="margin-bottom: 1rem;">
        <InputGroupAddon>
          <i class="pi pi-user-edit"></i>
        </InputGroupAddon>
        <FloatLabel>
          <InputText id="bio" v-model="form.bio" placeholder=" " class="w-full" />
          <label for="bio">О себе</label>
        </FloatLabel>
      </InputGroup>

      <!-- Специализация -->
      <InputGroup class="field" style="margin-bottom: 1rem;">
        <InputGroupAddon>
          <i class="pi pi-briefcase"></i>
        </InputGroupAddon>
        <FloatLabel>
          <InputText id="specialization" v-model="form.specialization" placeholder=" " class="w-full" />
          <label for="specialization">Специализация</label>
        </FloatLabel>
      </InputGroup>

      <!-- Опыт -->
      <InputGroup class="field" style="margin-bottom: 1rem;">
        <InputGroupAddon>
          <i class="pi pi-calendar"></i>
        </InputGroupAddon>
        <FloatLabel>
          <InputNumber id="experience_years" v-model="form.experience_years" :min="0" :max="50" class="w-full" />
          <label for="experience_years">Опыт работы (лет)</label>
        </FloatLabel>
      </InputGroup>

      <!-- Образование -->
      <InputGroup class="field" style="margin-bottom: 1rem;">
        <InputGroupAddon>
          <i class="pi pi-graduation-cap"></i>
        </InputGroupAddon>
        <FloatLabel>
          <InputText id="education" v-model="form.education" placeholder=" " class="w-full" />
          <label for="education">Образование</label>
        </FloatLabel>
      </InputGroup>

      <!-- Сертификаты -->
      <InputGroup class="field" style="margin-bottom: 1rem;">
        <InputGroupAddon>
          <i class="pi pi-copy"></i>
        </InputGroupAddon>
        <FloatLabel>
          <Chips
            id="certificates"
            v-model="form.certificates"
            separator=","
            :addOnBlur="true"
            :allowDuplicate="false"
            placeholder="Например: CELTA, TESOL"
            class="w-full"
          />
          <label for="certificates">Сертификаты</label>
        </FloatLabel>
      </InputGroup>

      <!-- Ставка -->
      <InputGroup class="field" style="margin-bottom: 1rem;">
        <InputGroupAddon>
          <i class="pi pi-dollar"></i>
        </InputGroupAddon>
        <FloatLabel>
          <InputNumber
            id="hourly_rate"
            v-model="form.hourly_rate"
            :min="0"
            :max="10000"
            mode="currency"
            currency="RUB"
            locale="ru-RU"
            class="w-full"
          />
          <label for="hourly_rate">Почасовая ставка</label>
        </FloatLabel>
      </InputGroup>
    </div>

    <template #footer>
      <Button label="Отмена" icon="pi pi-times" text @click="close" />
      <Button label="Сохранить" icon="pi pi-check" :loading="saving" @click="save" />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import FloatLabel from 'primevue/floatlabel'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import Chips from 'primevue/chips'

export default defineComponent({
  name: 'EditTeacherDialog',
  components: { Dialog, Button, InputText, InputNumber, FloatLabel, InputGroup, InputGroupAddon, Chips },
  props: {
    visible: { type: Boolean, required: true },
    modelValue: {
      type: Object as () => {
        bio: string
        specialization: string
        experience_years: number
        education: string
        certificates: string[]
        hourly_rate: number
      },
      required: true
    },
    saving: { type: Boolean, default: false }
  },
  emits: ['update:visible', 'update:modelValue', 'save'],
  setup(props, { emit }) {
    const visibleLocal = ref(false)
    const form = ref({ ...props.modelValue })

    // Сбрасываем форму и открываем диалог при изменении props.visible на true
    watch(() => props.visible, (val) => {
      if (val) {
        form.value = { ...props.modelValue }
        visibleLocal.value = true
      }
    })

    // Синхронизация формы с родителем
    watch(form, val => {
      emit('update:modelValue', { ...val })
    }, { deep: true })

    const close = () => {
      visibleLocal.value = false
      emit('update:visible', false)
      form.value = { ...props.modelValue } // сброс изменений
    }

    const save = () => {
      emit('save')
    }

    return { visibleLocal, form, close, save }
  }
})
</script>

<style scoped>
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  position: absolute; /* вернуть дефолт для корректного смещения left */
  z-index: 2;
}

/* Сдвигаем сам label вправо, если слева есть иконка (IconField) */
:deep(.p-floatlabel .p-iconfield + label),
:deep(.p-floatlabel .p-input-icon-left + label),
:deep(.p-floatlabel .p-inputicon-left + label) {
  left: 2.25rem !important;
}

/* Сдвигаем контент input внутрь вправо под иконку IconField */
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
</style>
