<template>
  <Dialog
    v-model:visible="visibleLocal"
    modal
    header="Добавить новый язык"
    :style="{ width: '90vw', maxWidth: '500px' }"
  >
    <div class="add-language-form">
      <div class="form-group">
        <label for="newLanguageName">Название языка *</label>
        <input
          id="newLanguageName"
          v-model="localLanguage.name"
          type="text"
          placeholder="Например: Испанский"
          class="form-input"
          required
        />
      </div>
      <div class="form-group">
        <label for="newLanguageCode">Код языка *</label>
        <input
          id="newLanguageCode"
          v-model="localLanguage.code"
          type="text"
          placeholder="Например: es"
          class="form-input"
          required
          maxlength="10"
        />
        <small class="form-hint">Короткий код языка (максимум 10 символов)</small>
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
        label="Добавить"
        icon="pi pi-check"
        @click="save"
        :loading="loading"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, PropType, ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

export default defineComponent({
  name: 'AddLanguageDialog',
  components: { Dialog, Button },
  props: {
    visible: { type: Boolean, required: true },
    loading: { type: Boolean, default: false },
    language: {
      type: Object as PropType<{ name: string; code: string }>,
      default: () => ({ name: '', code: '' })
    }
  },
  emits: ['update:visible', 'save', 'cancel'],
  setup(props, { emit }) {
    const visibleLocal = ref(props.visible)
    const localLanguage = ref({ ...props.language })

    watch(() => props.visible, (val) => {
      visibleLocal.value = val
      if (val) {
        localLanguage.value = { ...props.language }
      }
    })

    watch(visibleLocal, (val) => {
      emit('update:visible', val)
    })

    watch(() => props.language, (val) => {
      localLanguage.value = { ...val }
    })

    const close = () => {
      visibleLocal.value = false
      emit('cancel')
    }

    const save = () => {
      if (!localLanguage.value.name.trim() || !localLanguage.value.code.trim()) {
        return
      }
      emit('save', { ...localLanguage.value })
    }

    return { visibleLocal, localLanguage, close, save }
  }
})
</script>

<style scoped>
.add-language-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 1rem 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: #333;
}

.form-input {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.form-hint {
  display: block;
  margin-top: 4px;
  color: #666;
  font-size: 12px;
}
</style>

