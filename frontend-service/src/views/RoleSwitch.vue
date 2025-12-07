<template>
  <div class="role-switch-page">
    <div class="main-content">
      <div v-if="loading" class="loading-indicator">
        <LoadingSpinner />
        <p>Проверяем ссылку...</p>
      </div>

      <div v-else-if="error" class="detail-section">
        <h2>Ошибка</h2>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="!isValid" class="detail-section">
        <h2>Недействительная ссылка</h2>
        <p>Ссылка недействительна или истекла.</p>
      </div>

      <div v-else-if="!formSubmitted" class="detail-section">
        <div class="page-header">
          <h1>Стать учителем</h1>
          <p class="description">
            Заполните форму ниже, чтобы стать учителем. После успешного заполнения
            ваша роль изменится со студента на учителя.
          </p>
        </div>

        <div v-if="!isTelegramMiniApp" class="telegram-warning">
          <div class="warning-icon">⚠️</div>
          <h3>Откройте ссылку в Telegram</h3>
          <p>Для переключения роли необходимо открыть эту ссылку в Telegram Mini App.</p>
          <p>Скопируйте ссылку и отправьте её в Telegram бот.</p>
          <div class="link-container">
            <input :value="currentUrl" readonly class="link-input" ref="urlInput" />
            <Button
              :label="urlCopied ? 'Скопировано!' : 'Копировать'"
              @click="copyUrl"
              outlined
            />
          </div>
        </div>

        <form @submit.prevent="submitForm" class="form">
          <div class="form-group">
            <label for="specialization">Специализация *</label>
            <input id="specialization" v-model="form.specialization" type="text" required placeholder="Например: Математика, Английский язык" class="form-input" />
          </div>

          <div class="form-group">
            <label for="experience">Опыт преподавания (лет) *</label>
            <input id="experience" v-model.number="form.experience" type="number" min="0" max="50" required placeholder="0" class="form-input" />
          </div>

          <div class="form-group">
            <label for="hourlyRate">Почасовая ставка (₽) *</label>
            <input id="hourlyRate" v-model.number="form.hourlyRate" type="number" min="100" max="10000" required placeholder="1000" class="form-input" />
          </div>

          <div class="form-group">
            <label for="description">Описание</label>
            <textarea id="description" v-model="form.description" rows="4" placeholder="Расскажите о себе, методах преподавания, достижениях..." class="form-textarea"></textarea>
          </div>

          <div class="form-group">
            <label for="languages">Языки преподавания</label>
            <div class="languages-selector">
              <MultiSelect
                id="languages"
                v-model="form.selectedLanguages"
                :options="languageOptions"
                optionLabel="label"
                optionValue="code"
                placeholder="Выберите языки"
                :filter="true"
                display="chip"
                class="form-multiselect"
              />
              <button
                type="button"
                @click="showAddLanguageDialog = true"
                class="btn-add-language"
                title="Добавить новый язык"
              >
                <span style="font-size: 16px; margin-right: 4px;">+</span> Добавить язык
              </button>
            </div>
          </div>

          <div class="form-group">
            <label for="education">Образование</label>
            <input id="education" v-model="form.education" type="text" placeholder="Высшее образование, сертификаты..." class="form-input" />
          </div>

          <div class="form-actions">
            <Button
              type="submit"
              :label="submitting ? 'Отправка...' : 'Стать учителем'"
              :disabled="submitting"
              :loading="submitting"
            />
          </div>
        </form>
      </div>

      <div v-else class="detail-section">
        <div class="message-content">
          <div class="message-icon">✅</div>
          <h2>Поздравляем!</h2>
          <p>Вы успешно стали учителем!</p>
          <p class="success-details">Теперь вы можете создавать уроки и получать учеников.</p>
        </div>
      </div>
    </div>

    <!-- Диалог добавления нового языка -->
    <AddLanguageDialog
      v-model:visible="showAddLanguageDialog"
      :language="newLanguage"
      :loading="addingLanguage"
      @save="addNewLanguage"
      @cancel="showAddLanguageDialog = false"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRoute } from 'vue-router'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import MultiSelect from 'primevue/multiselect'
import Button from 'primevue/button'
import AddLanguageDialog from '@/components/dialogs/AddLanguageDialog.vue'
import { useUserStore } from '@/stores/user'
import { roleSwitchApi } from '@/services/api/roleSwitch'
import { teachersApi } from '@/services/api/teachers'
import { languagesApi } from '@/services/api/languages'
import { useUiStore } from '@/stores/ui'
import type { StudioLanguage } from '@/types/languages'

export default defineComponent({
  name: 'RoleSwitchPage',
  components: { LoadingSpinner, MultiSelect, Button, AddLanguageDialog },
  data() {
    return {
      ui: useUiStore(),
      route: useRoute(),
      userStore: useUserStore(),
      loading: true,
      error: '',
      isValid: false,
      formSubmitted: false,
      submitting: false,
      urlCopied: false,
      form: {
  specialization: '',
        experience: 0,
        hourlyRate: 0,
  description: '',
  languages: '',
  selectedLanguages: [] as string[],
  education: ''
      },
      languageOptions: [] as Array<{ label: string; value: string; code: string }>,
      showAddLanguageDialog: false,
      addingLanguage: false,
      newLanguage: {
        name: '',
        code: ''
      },
      pendingLanguages: [] as Array<{ name: string; code: string }> // Языки, добавленные локально до авторизации
    }
  },
  computed: {
    isTelegramMiniApp(): boolean {
      return !!(window.Telegram && window.Telegram.WebApp)
    },
    currentUrl(): string {
      return window.location.href
    },
    token(): string {
      return this.route.params.token as string
    }
  },
  async mounted() {
    if (!this.token) {
      this.error = 'Ссылка не содержит токена'
      this.loading = false
    return
  }
    try {
      this.ui.showLoading('Проверка ссылки...')
      const data = await roleSwitchApi.validateToken(this.token)
      this.isValid = data.valid
    if (data.link && data.link.target_role !== 'teacher') {
        this.error = 'Эта ссылка не предназначена для переключения на роль учителя'
    }
      // Загружаем языки из БД
      await this.loadLanguages()
  } catch (err) {
    console.error('Error validating link:', err)
      this.error = 'Ошибка при проверке ссылки'
  } finally {
      this.loading = false
      this.ui.hideLoading()
    }
  },
  methods: {
    async loadLanguages() {
      try {
        const languages = await languagesApi.getLanguages(true) // только активные
        this.languageOptions = languages.map(lang => ({
          label: lang.name,
          value: lang.code,
          code: lang.code
        }))
      } catch (error) {
        console.error('Failed to load languages:', error)
        this.languageOptions = []
      }
    },
    async addNewLanguage(languageData: { name: string; code: string }) {
      if (!languageData.name.trim() || !languageData.code.trim()) {
        this.$toast.add({
          severity: 'warn',
          summary: 'Ошибка',
          detail: 'Заполните все поля',
          life: 3000
        })
        return
      }

      this.addingLanguage = true
      try {
        const code = languageData.code.toLowerCase().trim()
        const name = languageData.name.trim()

        // Проверяем, есть ли уже такой код
        const existing = this.languageOptions.find(l => l.code === code)
        if (existing) {
          this.$toast.add({
            severity: 'warn',
            summary: 'Ошибка',
            detail: 'Язык с таким кодом уже существует',
            life: 3000
          })
          this.addingLanguage = false
          return
        }

        // Пробуем создать язык через API, если пользователь авторизован
        const token = localStorage.getItem('jwt_token')
        if (token) {
          try {
            const createdLang = await languagesApi.createLanguage({
              name: name,
              code: code,
              is_active: true
            })

            // Добавляем в список
            const newLang = {
              label: createdLang.name,
              value: createdLang.code,
              code: createdLang.code
            }
            this.languageOptions.push(newLang)
            this.form.selectedLanguages.push(newLang.code)

            this.$toast.add({
              severity: 'success',
              summary: 'Успешно',
              detail: 'Язык добавлен в базу данных',
              life: 3000
            })
          } catch (apiError: any) {
            // Если не удалось создать через API, добавляем локально
            console.warn('Не удалось создать язык через API:', apiError)
            const newLang = {
              label: name,
              value: code,
              code: code
            }
            this.languageOptions.push(newLang)
            this.form.selectedLanguages.push(newLang.code)
            // Сохраняем для попытки создания после авторизации
            this.pendingLanguages.push({ name, code })

            this.$toast.add({
              severity: 'info',
              summary: 'Язык добавлен',
              detail: 'Язык добавлен в форму. Попытка создания в БД будет после авторизации.',
              life: 4000
            })
          }
        } else {
          // Если пользователь не авторизован, добавляем локально
          const newLang = {
            label: name,
            value: code,
            code: code
          }
          this.languageOptions.push(newLang)
          this.form.selectedLanguages.push(newLang.code)
          // Сохраняем для попытки создания после авторизации
          this.pendingLanguages.push({ name, code })

          this.$toast.add({
            severity: 'info',
            summary: 'Язык добавлен',
            detail: 'Язык добавлен в форму. Попытка создания в БД будет после переключения роли.',
            life: 4000
          })
        }

        this.showAddLanguageDialog = false
        this.newLanguage = { name: '', code: '' }
      } catch (error: any) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: error?.message || 'Не удалось добавить язык',
          life: 5000
        })
      } finally {
        this.addingLanguage = false
      }
    },
    async submitForm() {
      this.submitting = true
      this.ui.showLoading('Отправка формы...')
      try {
        const roleData = await roleSwitchApi.switchRole(this.token)
    if (roleData.access_token) {
      localStorage.setItem('jwt_token', roleData.access_token)
    }
        await this.userStore.fetchCurrentUser()

        // Пытаемся создать языки, которые были добавлены локально до авторизации
        if (this.pendingLanguages.length > 0) {
          for (const lang of this.pendingLanguages) {
            try {
              const createdLang = await languagesApi.createLanguage({
                name: lang.name,
                code: lang.code,
                is_active: true
              })
              // Обновляем в списке, если код совпадает
              const existingIndex = this.languageOptions.findIndex(l => l.code === lang.code)
              if (existingIndex !== -1) {
                this.languageOptions[existingIndex] = {
                  label: createdLang.name,
                  value: createdLang.code,
                  code: createdLang.code
                }
              }
            } catch (error) {
              console.warn(`Не удалось создать язык ${lang.name} в БД:`, error)
              // Продолжаем, даже если не удалось создать
            }
          }
          this.pendingLanguages = []
        }

        // Формируем строку языков из выбранных
        const selectedLanguageNames = this.form.selectedLanguages
          .map(code => {
            const lang = this.languageOptions.find(l => l.code === code)
            return lang ? lang.label : code
          })

        // Объединяем специализацию и языки
        let specialization = this.form.specialization
        if (selectedLanguageNames.length > 0) {
          const languagesString = selectedLanguageNames.join(', ')
          if (specialization) {
            specialization = `${specialization} (Языки: ${languagesString})`
          } else {
            specialization = `Языки: ${languagesString}`
          }
        }

        // Пытаемся создать учителя, если его еще нет
        console.log('[RoleSwitch] Creating teacher with data:', {
          telegram_id: this.userStore.userData?.telegram_id,
          specialization,
          experience_years: Number(this.form.experience),
          hourly_rate: Number(this.form.hourlyRate),
          bio: this.form.description,
          education: this.form.education
        })

        try {
          const createdTeacher = await teachersApi.createTeacherWithoutAuth({
            telegram_id: this.userStore.userData?.telegram_id!,
            specialization: specialization,
            experience_years: Number(this.form.experience),
            hourly_rate: Number(this.form.hourlyRate),
            bio: this.form.description,
            education: this.form.education
          })
          console.log('[RoleSwitch] Teacher created successfully:', createdTeacher)
        } catch (createError: any) {
          console.error('[RoleSwitch] Error creating teacher:', createError)
          console.error('[RoleSwitch] Error details:', {
            status: createError?.response?.status,
            data: createError?.response?.data,
            message: createError?.message
          })

          // Если учитель уже существует (400), пытаемся обновить его данные
          if (createError?.response?.status === 400 &&
              (createError?.response?.data?.detail?.includes('already exists') ||
               createError?.response?.data?.detail?.includes('Teacher with this telegram_id'))) {
            console.log('[RoleSwitch] Teacher already exists, updating profile...')
            try {
              // Обновляем профиль через updateCurrentTeacher
              const updatedTeacher = await teachersApi.updateCurrentTeacher({
                specialization: specialization,
                experience_years: Number(this.form.experience),
                hourly_rate: Number(this.form.hourlyRate),
                bio: this.form.description,
                education: this.form.education
              })
              console.log('[RoleSwitch] Teacher updated successfully:', updatedTeacher)
            } catch (updateError: any) {
              console.error('[RoleSwitch] Error updating existing teacher:', updateError)
              console.error('[RoleSwitch] Update error details:', {
                status: updateError?.response?.status,
                data: updateError?.response?.data,
                message: updateError?.message
              })
              // Не выбрасываем ошибку, так как учитель уже существует
              // Просто продолжаем
            }
          } else {
            // Если другая ошибка, выбрасываем её
            throw createError
          }
        }

        this.formSubmitted = true
        this.$toast.add({ severity: 'success', summary: 'Готово', detail: 'Вы стали учителем!', life: 4000 })
      } catch (err: any) {
        this.error = err?.message || 'Произошла ошибка'
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: this.error, life: 5000 })
  } finally {
        this.submitting = false
        this.ui.hideLoading()
      }
    },
    async copyUrl() {
      try {
        await navigator.clipboard.writeText(this.currentUrl)
        this.urlCopied = true
        this.$toast.add({ severity: 'success', summary: 'Скопировано', detail: 'Ссылка скопирована', life: 2500 })
        setTimeout(() => (this.urlCopied = false), 2000)
  } catch (err) {
        const urlInput = this.$refs.urlInput as HTMLInputElement | undefined
    if (urlInput) {
      urlInput.select()
      document.execCommand('copy')
          this.urlCopied = true
          setTimeout(() => (this.urlCopied = false), 2000)
        }
      }
    }
  }
})
</script>

<style scoped>
.role-switch-page {
  min-height: 100vh;
  background: var(--surface-ground);
}

.main-content {
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem 0;
}

.page-header h1 {
  margin: 0 0 1rem 0;
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-color);
}

.description {
  color: var(--text-color-secondary);
  margin-bottom: 0;
  line-height: 1.6;
}

.detail-section {
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 1rem;
}

.detail-section h2 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1.5rem;
  font-weight: 600;
}

.detail-section p {
  color: var(--text-color-secondary);
  margin: 0.5rem 0;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.loading-indicator p {
  margin-top: 1rem;
  color: var(--text-color-secondary);
}

.message-content {
  text-align: center;
  padding: 2rem;
}

.message-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.message-content h2 {
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.message-content p {
  margin: 0.5rem 0;
  color: var(--text-color-secondary);
}

.success-details {
  color: var(--text-color-secondary);
  margin-top: 1rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.form-input, .form-textarea {
  padding: 0.75rem;
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  background: var(--surface-card);
  color: var(--text-color);
  transition: border-color 0.2s ease;
  width: 100%;
}

.languages-selector {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.form-multiselect {
  flex: 1;
  width: 100%;
}

:deep(.p-multiselect) {
  width: 100%;
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}

:deep(.p-multiselect:not(.p-disabled):hover) {
  border-color: var(--primary-color);
}

:deep(.p-multiselect:not(.p-disabled).p-focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem var(--primary-color-transparent);
}

.btn-add-language {
  padding: 0.75rem 1rem;
  background: var(--green-500);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-add-language:hover {
  background: var(--green-600);
}


.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 0.2rem var(--primary-color-transparent);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.telegram-warning {
  background: var(--yellow-50);
  border: 1px solid var(--yellow-200);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.warning-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.telegram-warning h3 {
  color: var(--yellow-800);
  margin: 0 0 0.75rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.telegram-warning p {
  color: var(--yellow-800);
  margin: 0.5rem 0;
}

.link-container {
  display: flex;
  gap: 0.75rem;
  margin: 1rem 0 0 0;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}

.link-input {
  flex: 1;
  min-width: 200px;
  max-width: 400px;
  padding: 0.75rem;
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  font-family: monospace;
  font-size: 0.875rem;
  background: var(--surface-card);
  color: var(--text-color);
}

@media (max-width: 768px) {
  .main-content {
    padding: 0.5rem;
  }

  .detail-section {
    padding: 1.5rem;
  }

  .page-header {
    padding: 1rem 0;
  }

  .page-header h1 {
    font-size: 1.75rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .link-container {
    flex-direction: column;
  }

  .link-input {
    width: 100%;
    max-width: 100%;
  }
}
</style>
