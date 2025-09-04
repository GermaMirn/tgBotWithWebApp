<template>
  <div class="profile-page">
    <div class="main-content">
      <div class="page-header">
        <h1>Мой профиль</h1>
        <p>Информация о вашем аккаунте</p>
      </div>

      <EditProfileDialog
        v-model:visible="editProfileDialog"
        v-model:modelValue="editForm"
        :saving="saving"
        @save="saveProfile"
      />

      <EditStudentDialog
        v-model:visible="editStudentDialog"
        v-model:modelValue="editStudentForm"
        :saving="saving"
        @save="saveStudentData"
      />

      <EditTeacherDialog
        v-model:visible="editTeacherDialog"
        v-model:modelValue="editTeacherForm"
        :saving="saving"
        @save="saveTeacherData"
      />

      <!-- Данные пользователя -->
      <div v-if="isAuthenticated && userData" class="user-profile">
        <!-- Индикатор загрузки -->
        <div v-if="loading" class="loading-overlay">
          <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
          <p>Загрузка данных профиля...</p>
        </div>
        <div class="profile-header">
          <Avatar
            :label="userData.full_name?.charAt(0) || 'U'"
            shape="circle"
            size="xlarge"
            class="profile-avatar"
          />
          <div class="profile-info">
            <h2>{{ userData.full_name || 'Пользователь' }}</h2>
            <p class="user-role">{{ getUserRoleName() }}</p>
            <p class="user-status">
              <i class="pi pi-check-circle"></i>
              Активный пользователь
            </p>
          </div>
        </div>

        <div class="profile-details">
          <div class="detail-section">
            <h3>Личная информация</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <label>ID пользователя</label>
                <span>{{ userData.id || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <label>Telegram ID</label>
                <span>{{ userData.telegram_id }}</span>
              </div>
              <div class="detail-item">
                <label>Имя</label>
                <span>{{ userData.full_name || 'Не указано' }}</span>
              </div>
              <div class="detail-item">
                <label>Username</label>
                <span>{{ userData.username !== '-' ? '@' + userData.username : 'Не указан' }}</span>
              </div>
              <div class="detail-item">
                <label>Телефон</label>
                <span>{{ userData.phone_number || 'Не указан' }}</span>
              </div>
              <div class="detail-item">
                <label>Email</label>
                <span>{{ userData.email || 'Не указан' }}</span>
              </div>
              <div class="detail-item">
                <label>Роль в системе</label>
                <span>{{ getUserRoleName() }}</span>
              </div>
            </div>

          </div>

          <!-- Данные студента -->
          <div v-if="userRole === 'student'" class="detail-section">
            <div v-if="loading" class="loading-section">
              <i class="pi pi-spin pi-spinner"></i>
              <p>Загрузка данных студента...</p>
            </div>
            <div v-else>
            <h3>Данные студента</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <label>Уровень</label>
                <span>{{ studentData?.level || 'Не указан' }}</span>
              </div>
              <div class="detail-item">
                <label>Предпочитаемые языки</label>
                <span>{{ studentData?.preferred_languages?.join(', ') || 'Не указаны' }}</span>
              </div>
              <div class="detail-item full-width">
                <label>Цели обучения</label>
                <span>{{ studentData?.study_goals || 'Не указаны' }}</span>
              </div>
            </div>

            </div>
          </div>

          <!-- Данные учителя -->
          <div v-if="userRole === 'teacher'" class="detail-section">
            <div v-if="loading" class="loading-section">
              <i class="pi pi-spin pi-spinner"></i>
              <p>Загрузка данных учителя...</p>
            </div>
            <div v-else>
            <h3>Данные учителя</h3>
            <div class="detail-grid">
              <div class="detail-item full-width">
                <label>О себе</label>
                <span>{{ teacherData?.bio || 'Не указано' }}</span>
              </div>
              <div class="detail-item">
                <label>Специализация</label>
                <span>{{ teacherData?.specialization || 'Не указана' }}</span>
              </div>
              <div class="detail-item">
                <label>Опыт работы</label>
                <span>{{ teacherData?.experience_years || 0 }} лет</span>
              </div>
              <div class="detail-item">
                <label>Почасовая ставка</label>
                <span>{{ teacherData?.hourly_rate || 0 }} ₽</span>
              </div>
              <div class="detail-item full-width">
                <label>Образование</label>
                <span>{{ teacherData?.education || 'Не указано' }}</span>
              </div>
              <div class="detail-item full-width">
                <label>Сертификаты</label>
                <span>{{ Array.isArray(teacherData?.certificates) ? teacherData.certificates.join(', ') : teacherData?.certificates || 'Не указаны' }}</span>
              </div>
            </div>

            </div>
          </div>

          <div class="detail-section">
            <h3>Статистика</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-number">0</div>
                <div class="stat-label">Завершенных занятий</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">0</div>
                <div class="stat-label">Запланированных занятий</div>
              </div>
              <div class="stat-item">
                <div class="stat-number">0</div>
                <div class="stat-label">Изучаемых языков</div>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3>Информация об аккаунте</h3>
            <div class="account-info">
              <div class="info-item">
                <i class="pi pi-telegram"></i>
                <div class="info-content">
                  <h4>Telegram авторизация</h4>
                  <p>Ваш аккаунт привязан к Telegram. Выход из аккаунта недоступен.</p>
                </div>
              </div>
              <div class="info-item">
                <i class="pi pi-shield"></i>
                <div class="info-content">
                  <h4>Безопасность</h4>
                  <p>Пароль не требуется. Доступ осуществляется через Telegram.</p>
                </div>
              </div>
              <div class="info-item">
                <i class="pi pi-info-circle"></i>
                <div class="info-content">
                  <h4>Роль: {{ getUserRoleName() }}</h4>
                  <p>{{ getRoleDescription() }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3>Действия</h3>
            <div class="actions-grid">
              <Button
                label="Редактировать профиль"
                icon="pi pi-pencil"
                class="action-button"
                @click="openEditProfile"
                outlined
              />
              <Button
                v-if="userRole === 'student'"
                label="Редактировать данные студента"
                icon="pi pi-pencil"
                class="action-button"
                @click="openEditStudent"
                outlined
              />
              <Button
                v-if="userRole === 'teacher'"
                label="Редактировать данные учителя"
                icon="pi pi-pencil"
                class="action-button"
                @click="openEditTeacher"
                outlined
              />
              <Button
                label="Настройки уведомлений"
                icon="pi pi-bell"
                class="action-button"
                outlined
              />
              <Button
                label="Связаться с поддержкой"
                icon="pi pi-comments"
                class="action-button"
                outlined
              />
              <Button
                label="Политика конфиденциальности"
                icon="pi pi-file"
                class="action-button"
                outlined
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/services/api/auth'
import { studentsApi } from '@/services/api/students'
import { teachersApi } from '@/services/api/teachers'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import type { UserProfile, StudentProfile, TeacherProfile } from '@/types/user.ts'
import EditProfileDialog from '@/components/dialogs/EditProfileDialog.vue'
import EditStudentDialog from '@/components/dialogs/EditStudentDialog.vue'
import EditTeacherDialog from '@/components/dialogs/EditTeacherDialog.vue'

export default defineComponent({
  name: 'ProfilePage',
  components: {
    Avatar,
    Button,
    EditProfileDialog,
    EditStudentDialog,
    EditTeacherDialog
  },
  data() {
    return {
      userStore: useUserStore(),
      router: useRouter(),
      editProfileDialog: false,
      editStudentDialog: false,
      editTeacherDialog: false,
      saving: false,
      studentData: null as StudentProfile | null,
      teacherData: null as TeacherProfile | null,
      loading: false,
      dataNotFound: false,
      editForm: {
        phone_number: '',
        email: ''
      },
      editStudentForm: {
        telegram_id: String(useUserStore().userData?.telegram_id || ''),
        study_goals: '',
        level: '',
        preferred_languages: [] as string[]
      },
      editTeacherForm: {
        bio: '',
        specialization: '',
        experience_years: 0,
        education: '',
        certificates: [] as string[],
        hourly_rate: 0
      },
      phoneFocused: false,
      emailFocused: false
    }
  },
  computed: {
    isAuthenticated(): boolean {
      return this.userStore.isAuthenticated
    },
    userData(): UserProfile | null {
      return this.userStore.userData
    },
    userRole(): string {
      return this.userStore.userRole
    },
    emailError(): boolean {
      const email = this.editForm.email?.trim()
      if (!email) return false
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return !emailRegex.test(email)
    },
    phoneError(): boolean {
      const raw = (this.editForm.phone_number ?? '').replace(/\D/g, '')
      if (raw.length === 0) return false
      if (raw.length === 11 && raw.startsWith('7')) return false
      return !(raw.length === 10)
    },
    isPhoneActive(): boolean {
      return this.phoneFocused || !!(this.editForm.phone_number && this.editForm.phone_number.toString().trim().length)
    },
    isEmailActive(): boolean {
      return this.emailFocused || !!(this.editForm.email && this.editForm.email.toString().trim().length)
    }
  },
  methods: {
    formatPhoneForMask(raw: string): string {
      const digits = String(raw || '').replace(/\D/g, '')
      if (!digits) return ''
      let d = digits
      if (d.startsWith('8')) d = '7' + d.slice(1)
      if (d[0] !== '7') d = '7' + d
      d = (d + '           ').slice(0, 11)
      // d[0] is country (7)
      return `+7 (${d[1] || ''}${d[2] || ''}${d[3] || ''}) ${d[4] || ''}${d[5] || ''}${d[6] || ''}-${d[7] || ''}${d[8] || ''}-${d[9] || ''}${d[10] || ''}`
    },
    onPhoneInput() {},
    getUserRoleName() {
      const role = this.userRole
      const roleNames: Record<string, string> = {
        admin: 'Администратор',
        teacher: 'Учитель',
        student: 'Студент'
      }
      return roleNames[role || 'student'] || 'Студент'
    },
    getRoleDescription() {
      const role = this.userRole
      const descriptions: Record<string, string> = {
        admin: 'Полный доступ к системе управления',
        teacher: 'Доступ к управлению занятиями и студентами',
        student: 'Доступ к просмотру занятий и календаря'
      }
      return descriptions[role || 'student'] || 'Базовый доступ к системе'
    },
    goToHome() {
      this.router.push('/home')
    },
    async loadUserData() {
      if (!this.isAuthenticated) return
      this.loading = true
      try {
        if (this.userRole === 'student') {
          const data = await studentsApi.getCurrentStudent()
          this.studentData = data
        } else if (this.userRole === 'teacher') {
          const data = await teachersApi.getCurrentTeacher()
          this.teacherData = data
        }
      } catch (error: any) {
        if (error.response?.status === 404) {
          if (this.userRole === 'teacher') {
            this.$toast.add({
              severity: 'warn',
              summary: 'Данные не найдены',
              detail: 'Профиль учителя не найден. Возможно, нужно переключить роль или создать профиль.',
              life: 5000
            })
          } else if (this.userRole === 'student') {
            this.$toast.add({
              severity: 'warn',
              summary: 'Данные не найдены',
              detail: 'Профиль студента не найден. Возможно, нужно переключить роль или создать профиль.',
              life: 5000
            })
          }
        } else {
          this.$toast.add({
            severity: 'error',
            summary: 'Ошибка загрузки',
            detail: `Не удалось загрузить данные профиля: ${error.response?.data?.detail || error.message}`,
            life: 5000
          })
        }
      } finally {
        this.loading = false
      }
    },
    refreshData() {
      this.loadUserData()
    },
    openEditProfile() {
      this.editForm.phone_number = this.formatPhoneForMask(this.userData?.phone_number || '')
      this.editForm.email = this.userData?.email || ''
      this.editProfileDialog = true
    },
    async saveProfile() {
      if (this.emailError) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка валидации',
          detail: 'Пожалуйста, введите корректный email адрес',
          life: 5000
        })
        return
      }
      if (this.phoneError) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка валидации',
          detail: 'Пожалуйста, введите корректный номер телефона',
          life: 5000
        })
        return
      }
      this.saving = true
      try {
        // Отправляем в API номер без форматирования
        const rawDigits = (this.editForm.phone_number || '').replace(/\D/g, '')
        const e164 = rawDigits ? `+${rawDigits}` : undefined
        const updatedUser = await authApi.updateProfile({
          phone_number: e164,
          email: this.editForm.email || undefined
        })
        if (this.userData) {
          this.userData.phone_number = updatedUser.phone_number
          this.userData.email = updatedUser.email
        }
        this.editProfileDialog = false
        this.$toast.add({
          severity: 'success',
          summary: 'Успешно',
          detail: 'Профиль успешно обновлен!',
          life: 3000
        })
        this.refreshData()
      } catch (error) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: 'Ошибка при обновлении профиля',
          life: 5000
        })
      } finally {
        this.saving = false
      }
    },
    openEditStudent() {
      if (!this.studentData) return

      this.editStudentForm.study_goals = this.studentData.study_goals || ''
      this.editStudentForm.level = this.studentData.level || ''
      this.editStudentForm.preferred_languages = this.studentData.preferred_languages || []

      this.editStudentDialog = true
    },
    async saveStudentData() {
      this.saving = true
      try {
        await studentsApi.updateCurrentStudent({
          study_goals: this.editStudentForm.study_goals,
          level: this.editStudentForm.level || undefined,
          preferred_languages: this.editStudentForm.preferred_languages.length
            ? this.editStudentForm.preferred_languages
            : undefined
        })

        // Обновляем локально studentData
        this.studentData = {
          ...this.studentData,
          study_goals: this.editStudentForm.study_goals,
          level: this.editStudentForm.level,
          preferred_languages: [...this.editStudentForm.preferred_languages]
        }

        this.editStudentDialog = false
        this.$toast.add({
          severity: 'success',
          summary: 'Успешно',
          detail: 'Данные студента успешно обновлены!',
          life: 3000
        })
      } catch (error) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: 'Ошибка при обновлении данных студента',
          life: 5000
        })
      } finally {
        this.saving = false
      }
    },
    openEditTeacher() {
      if (!this.teacherData) return

      this.editTeacherForm.bio = this.teacherData.bio || ''
      this.editTeacherForm.specialization = this.teacherData.specialization || ''
      this.editTeacherForm.experience_years = this.teacherData.experience_years || 0
      this.editTeacherForm.education = this.teacherData.education || ''
      this.editTeacherForm.certificates = Array.isArray(this.teacherData.certificates)
        ? this.teacherData.certificates
        : (this.teacherData.certificates ? String(this.teacherData.certificates).split(',').map(c => c.trim()).filter(Boolean) : [])
      this.editTeacherForm.hourly_rate = this.teacherData.hourly_rate || 0

      this.editTeacherDialog = true
    },
    async saveTeacherData() {
      if (!this.editTeacherForm.specialization?.trim()) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка валидации',
          detail: 'Пожалуйста, укажите специализацию',
          life: 5000
        })
        return
      }
      if (this.editTeacherForm.experience_years < 0 || this.editTeacherForm.experience_years > 50) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка валидации',
          detail: 'Опыт работы должен быть от 0 до 50 лет',
          life: 5000
        })
        return
      }
      if (this.editTeacherForm.hourly_rate < 0 || this.editTeacherForm.hourly_rate > 10000) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка валидации',
          detail: 'Почасовая ставка должна быть от 0 до 10000 ₽',
          life: 5000
        })
        return
      }
      this.saving = true
      try {
        const certificates = (this.editTeacherForm.certificates || []).map((c: string) => c.trim()).filter((c: string) => c)
        const updatedData = await teachersApi.updateCurrentTeacher({
          bio: this.editTeacherForm.bio,
          specialization: this.editTeacherForm.specialization,
          experience_years: this.editTeacherForm.experience_years,
          education: this.editTeacherForm.education,
          certificates: certificates,
          hourly_rate: this.editTeacherForm.hourly_rate
        })
        this.teacherData = updatedData
        this.editTeacherDialog = false
        this.$toast.add({
          severity: 'success',
          summary: 'Успешно',
          detail: 'Данные учителя успешно обновлены!',
          life: 3000
        })
        this.refreshData()
      } catch (error) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: 'Ошибка при обновлении данных учителя',
          life: 5000
        })
      } finally {
        this.saving = false
      }
    }
  },
  mounted() {
    this.loadUserData()
  }
})
</script>

<style scoped>
.profile-page {
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
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.page-header p {
  font-size: 1.125rem;
  color: var(--text-color-secondary);
  margin: 0;
}

/* Профиль пользователя */
.user-profile {
  background: var(--surface-card);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 16px;
}

.loading-overlay i {
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.loading-overlay p {
  color: var(--text-color-secondary);
  margin: 0;
}

.loading-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--text-color-secondary);
}

.loading-section i {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.loading-section p {
  margin: 0;
  font-size: 1rem;
}

.profile-header {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.profile-avatar {
  margin-bottom: 1rem;
}

.profile-info h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.user-role {
  margin: 0 0 0.5rem 0;
  opacity: 0.9;
  font-size: 1rem;
}

.user-status {
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  opacity: 0.8;
}

.user-status i {
  color: var(--green-300);
}

/* Детали профиля */
.profile-details {
  padding: 2rem;
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

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.detail-item span {
  font-size: 1rem;
  color: var(--text-color);
  font-weight: 600;
}

.role-badge {
  border-radius: 20px;
  font-size: 0.875rem;
  display: inline-block;
  width: fit-content;
}

/* Информация об аккаунте */
.account-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  background: var(--surface-section);
  border-radius: 12px;
  border: 1px solid var(--surface-border);
}

.info-item i {
  font-size: 1.5rem;
  color: var(--primary-color);
  margin-top: 0.25rem;
}

.info-content h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
}

.info-content p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-color-secondary);
  line-height: 1.4;
}

/* Статистика */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1.5rem;
  background: var(--surface-section);
  border-radius: 12px;
  border: 1px solid var(--surface-border);
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

/* Действия */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-button {
  width: 100%;
  justify-content: flex-start;
}

/* Если не аутентифицирован */
.auth-required {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--surface-card);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.auth-icon {
  font-size: 4rem;
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.auth-required h2 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.auth-required p {
  font-size: 1.125rem;
  color: var(--text-color-secondary);
  margin: 0 0 2rem 0;
}

/* Адаптация под мобильные устройства */
@media (max-width: 768px) {
  .main-content {
    padding: 0.5rem;
  }

  .page-header h1 {
    font-size: 1.75rem;
  }

  .profile-header {
    padding: 1.5rem;
  }

  .profile-details {
    padding: 1.5rem;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .info-item {
    flex-direction: column;
    text-align: center;
  }
}
</style>
