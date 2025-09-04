<template>
  <div class="role-switch-container">
    <div class="role-switch-card">
      <div v-if="loading" class="loading">
        <LoadingSpinner />
        <p>Проверяем ссылку...</p>
      </div>

      <div v-else-if="error" class="error">
        <h2>Ошибка</h2>
        <p>{{ error }}</p>
      </div>

      <div v-else-if="!isValid" class="invalid-link">
        <h2>Недействительная ссылка</h2>
        <p>Ссылка недействительна или истекла.</p>
      </div>

            <div v-else-if="!formSubmitted" class="role-switch-form">
        <h2>Стать учителем</h2>
        <p class="description">
          Заполните форму ниже, чтобы стать учителем. После успешного заполнения
          ваша роль изменится со студента на учителя.
        </p>

        <div v-if="!isTelegramMiniApp" class="telegram-warning">
          <div class="warning-icon">⚠️</div>
          <h3>Откройте ссылку в Telegram</h3>
          <p>Для переключения роли необходимо открыть эту ссылку в Telegram Mini App.</p>
          <p>Скопируйте ссылку и отправьте её в Telegram бот.</p>
          <div class="link-container">
            <input :value="currentUrl" readonly class="link-input" ref="urlInput" />
            <button @click="copyUrl" class="btn-copy">{{ urlCopied ? 'Скопировано!' : 'Копировать' }}</button>
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
            <input id="languages" v-model="form.languages" type="text" placeholder="Русский, Английский" class="form-input" />
          </div>

          <div class="form-group">
            <label for="education">Образование</label>
            <input id="education" v-model="form.education" type="text" placeholder="Высшее образование, сертификаты..." class="form-input" />
          </div>

          <div class="form-actions">
            <button type="submit" :disabled="submitting" class="btn-primary">{{ submitting ? 'Отправка...' : 'Стать учителем' }}</button>
          </div>
        </form>
      </div>

      <div v-else class="success">
        <div class="success-icon">✅</div>
        <h2>Поздравляем!</h2>
        <p>Вы успешно стали учителем!</p>
        <p class="success-details">Теперь вы можете создавать уроки и получать учеников.</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRoute } from 'vue-router'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { useUserStore } from '@/stores/user'
import { roleSwitchApi } from '@/services/api/roleSwitch'
import { teachersApi } from '@/services/api/teachers'
import { useUiStore } from '@/stores/ui'

export default defineComponent({
  name: 'RoleSwitchPage',
  components: { LoadingSpinner },
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
  education: ''
      }
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
  } catch (err) {
    console.error('Error validating link:', err)
      this.error = 'Ошибка при проверке ссылки'
  } finally {
      this.loading = false
      this.ui.hideLoading()
    }
  },
  methods: {
    async submitForm() {
      this.submitting = true
      this.ui.showLoading('Отправка формы...')
      try {
        const roleData = await roleSwitchApi.switchRole(this.token)
    if (roleData.access_token) {
      localStorage.setItem('jwt_token', roleData.access_token)
    }
        await this.userStore.fetchCurrentUser()
    await teachersApi.createTeacherWithoutAuth({
          telegram_id: this.userStore.userData?.telegram_id!,
          specialization: this.form.specialization,
          experience_years: Number(this.form.experience),
          hourly_rate: Number(this.form.hourlyRate),
          bio: this.form.description,
          education: this.form.education
        })
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
.role-switch-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.role-switch-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
}

.loading, .error, .invalid-link, .success {
  text-align: center;
}

.loading p {
  margin-top: 16px;
  color: #666;
}

.error h2, .invalid-link h2, .success h2 {
  color: #e74c3c;
  margin-bottom: 16px;
}

.success h2 {
  color: #27ae60;
}

.success-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.success-details {
  color: #666;
  margin-bottom: 24px;
}

.description {
  color: #666;
  margin-bottom: 32px;
  line-height: 1.6;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

.form-input, .form-textarea {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-top: 16px;
}

.btn-primary, .btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5a6fd8;
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f8f9fa;
  color: #333;
  border: 2px solid #e1e5e9;
}

.btn-secondary:hover {
  background: #e9ecef;
}

.telegram-warning {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  text-align: center;
}

.warning-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.telegram-warning h3 {
  color: #856404;
  margin-bottom: 12px;
}

.telegram-warning p {
  color: #856404;
  margin-bottom: 8px;
}

.link-container {
  display: flex;
  gap: 12px;
  margin: 16px 0;
  justify-content: center;
}

.link-input {
  flex: 1;
  max-width: 400px;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-family: monospace;
  font-size: 14px;
  background: white;
}

.btn-copy {
  background: #28a745;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-copy:hover {
  background: #218838;
}

@media (max-width: 768px) {
  .role-switch-card {
    padding: 24px;
    margin: 16px;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>
