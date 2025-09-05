<template>
  <div class="admin-role-switch">
    <div class="container">
      <h1>Управление переключением ролей</h1>

      <div class="admin-card">
        <h2>Создать ссылку для переключения роли</h2>
        <form @submit.prevent="createLink" class="create-form">
          <div class="form-group">
            <label for="targetRole">Целевая роль</label>
            <Dropdown
              id="targetRole"
              v-model="form.targetRole"
              :options="roleOptions"
              optionLabel="name"
              optionValue="value"
              placeholder="Выберите роль"
              class="form-input"
              @change="onRoleChange"
            />
          </div>

          <div class="form-group" v-if="form.targetRole">
            <label for="userSelect">Пользователь</label>
            <Dropdown
              id="userSelect"
              v-model="selectedUser"
              :options="users"
              filter
              optionLabel="full_name"
              placeholder="Выберите пользователя"
              class="form-input"
              :loading="loadingUsers"
              :disabled="!form.targetRole"
            />
          </div>

          <div class="form-group">
            <label for="expiresInHours">Время жизни ссылки (часы)</label>
            <input
              id="expiresInHours"
              v-model.number="form.expiresInHours"
              type="number"
              min="1"
              max="168"
              required
              placeholder="24"
              class="form-input"
            />
          </div>

          <button type="submit" :disabled="creating || !canCreateLink" class="btn-primary">
            {{ creating ? 'Создание...' : 'Создать ссылку' }}
          </button>
        </form>

        <div v-if="createdLink" class="link-result">
          <h3>Ссылка создана!</h3>
          <p>Скопируйте эту ссылку и отправьте пользователю:</p>
          <div class="link-container">
            <input :value="createdLink" readonly class="link-input" ref="linkInput" />
            <button @click="copyLink" class="btn-copy">
              {{ copied ? 'Скопировано!' : 'Копировать' }}
            </button>
          </div>
          <div class="link-info">
            <p><strong>Роль:</strong> {{ getRoleName(form.targetRole) }}</p>
            <p><strong>Истекает:</strong> {{ formatExpiryTime() }}</p>
          </div>
          <button @click="createNewLink" class="btn-secondary">Создать новую ссылку</button>
        </div>
      </div>

      <div class="admin-card">
        <h2>Активные ссылки</h2>
        <div v-if="links.length === 0" class="no-links">
          <p>Активных ссылок нет</p>
        </div>

        <div v-else class="links-list">
          <div v-for="link in links" :key="link.id" class="link-item">
            <div class="link-header">
              <span class="link-role">{{ getRoleName(link.target_role) }}</span>
              <span class="link-status" :class="{ used: link.is_used }">{{ getLinkStatus(link) }}</span>
            </div>

            <div class="link-token">
              <code>{{ link.token }}</code>
            </div>

            <div class="link-details">
              <p><strong>Создана:</strong> {{ formatDate(link.created_at) }}</p>
              <p><strong>Истекает:</strong> {{ formatDate(link.expires_at) }}</p>
              <p v-if="link.is_used"><strong>Использована:</strong> {{ formatDate(link.used_at) }}</p>
            </div>

            <div class="link-actions">
              <button @click="deleteLink(link.id)" class="btn-delete" :disabled="link.is_used" title="Удалить ссылку">
                <i class="pi pi-trash"></i>
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { adminApi, type User, type RoleSwitchLink } from '@/services/api/admin'
import Dropdown from 'primevue/dropdown'
import { useUiStore } from '@/stores/ui'

export default defineComponent({
  name: 'AdminRoleSwitchPage',
  components: { Dropdown },
  data() {
    return {
      ui: useUiStore(),
      creating: false,
      loadingLinks: false,
      loadingUsers: false,
      copied: false,
      createdLink: '',
      links: [] as RoleSwitchLink[],
      form: {
        targetRole: '' as string,
        expiresInHours: 24 as number
      },
      roleOptions: [
        { name: 'Учитель', value: 'teacher' },
        { name: 'Студент', value: 'student' },
        { name: 'Администратор', value: 'admin' }
      ],
      users: [] as User[],
      selectedUser: null as User | null,
    }
  },
  computed: {
    canCreateLink(): boolean {
      return !!(this.form.targetRole && this.selectedUser)
    }
  },
  mounted() {
    this.loadLinks()
  },
  methods: {
    async onRoleChange() {
      this.selectedUser = null
      this.users = []
      if (!this.form.targetRole) return
      this.loadingUsers = true
      this.ui.showLoading('Загрузка пользователей...')
      try {
        let roleToFetch = ''
        if (this.form.targetRole === 'teacher') roleToFetch = 'student'
        else if (this.form.targetRole === 'student') roleToFetch = 'teacher'
        else if (this.form.targetRole === 'admin') roleToFetch = ''
        this.users = await adminApi.getUsers(roleToFetch)
      } catch (error) {
        console.error('Error loading users:', error)
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Ошибка при загрузке пользователей', life: 4000 })
      } finally {
        this.loadingUsers = false
        this.ui.hideLoading()
      }
    },
    getRoleName(role?: string) {
      const roleNames: Record<string, string> = { teacher: 'Учитель', student: 'Студент', admin: 'Администратор' }
      return role ? roleNames[role] || role : ''
    },
    formatDate(dateString: string) {
      return new Date(dateString).toLocaleString('ru-RU')
    },
    formatExpiryTime() {
      const hours = this.form.expiresInHours
      const expiryDate = new Date()
      expiryDate.setHours(expiryDate.getHours() + hours)
      return expiryDate.toLocaleString('ru-RU')
    },
    async createLink() {
      if (!this.canCreateLink) return
      this.creating = true
      this.ui.showLoading('Создание ссылки...')
      try {
        if (this.form.targetRole === 'student') {
          await adminApi.switchUserRole({
            target_role: this.form.targetRole,
            target_user_id: this.selectedUser!.id,
            target_user_name: this.selectedUser!.full_name
          })
          this.$toast.add({ severity: 'success', summary: 'Готово', detail: `Роль пользователя ${this.selectedUser!.full_name} изменена на "студент"`, life: 4000 })
          this.createNewLink()
          await this.loadLinks()
          return
        }
        const response = await adminApi.createRoleSwitchLink({
          target_role: this.form.targetRole,
          target_user_id: this.selectedUser!.id,
          target_user_name: this.selectedUser!.full_name,
          expires_in_hours: this.form.expiresInHours
        })
        this.createdLink = `${window.location.origin}/role-switch/${response.token}`
        await this.loadLinks()
        this.$toast.add({ severity: 'success', summary: 'Ссылка создана', detail: 'Отправьте ссылку пользователю', life: 4000 })
      } catch (err: any) {
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: err?.message || 'Ошибка при создании ссылки', life: 5000 })
      } finally {
        this.creating = false
        this.ui.hideLoading()
      }
    },
    async loadLinks() {
      this.loadingLinks = true
      this.ui.showLoading('Загрузка ссылок...')
      try {
        this.links = await adminApi.getRoleSwitchLinks()
      } catch (err) {
        console.error('Error loading links:', err)
      } finally {
        this.loadingLinks = false
        this.ui.hideLoading()
      }
    },
    async deactivateLink(linkId: string) {
      this.ui.showLoading('Деактивация ссылки...')
      await adminApi.deactivateRoleSwitchLink(linkId)
      await this.loadLinks()
      this.ui.hideLoading()
    },
    async deleteLink(linkId: string) {
      if (confirm('Удалить ссылку?')) {
        this.ui.showLoading('Удаление ссылки...')
        await adminApi.deleteRoleSwitchLink(linkId)
        await this.loadLinks()
        this.ui.hideLoading()
        this.$toast.add({ severity: 'success', summary: 'Удалено', detail: 'Ссылка удалена', life: 3000 })
      }
    },
    async copyLink() {
      const input = this.$refs.linkInput as HTMLInputElement | undefined
      if (!input) return
      try {
        await navigator.clipboard.writeText(this.createdLink)
        this.copied = true
        this.$toast.add({ severity: 'success', summary: 'Скопировано', detail: 'Ссылка скопирована в буфер обмена', life: 2500 })
        setTimeout(() => (this.copied = false), 2000)
      } catch (err) {
        input.select()
        document.execCommand('copy')
        this.copied = true
        setTimeout(() => (this.copied = false), 2000)
      }
    },
    createNewLink() {
      this.createdLink = ''
      this.form.targetRole = ''
      this.form.expiresInHours = 24
      this.selectedUser = null
      this.users = []
    },
    getLinkStatus(link: RoleSwitchLink) {
      if (link.is_used) return 'Использована'
      if (!link.is_active) return 'Неактивна'
      return 'Активна'
    }
  }
})
</script>

<style scoped>
.admin-role-switch {
  padding: 40px 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 40px;
  font-size: 2.5rem;
}

.admin-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.admin-card h2 {
  color: #333;
  margin-bottom: 24px;
  font-size: 1.5rem;
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 400px;
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
  background: white;
  width: 100%;
  min-width: 0;
}
.form-input:focus {
  outline: none;
  border-color: #667eea;
}

/* Стили для Dropdown компонентов */
:deep(.p-dropdown) {
  width: 100%;
  height: auto;
  min-height: 48px; /* Такая же высота как у input */
}

:deep(.p-dropdown .p-dropdown-label) {
  padding: 12px 16px;
  font-size: 16px;
  line-height: 1.5;
}

:deep(.p-dropdown .p-dropdown-trigger) {
  width: 48px;
  height: 48px;
}

:deep(.p-dropdown.p-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

/* Уменьшаем размер Dropdown до размера input */
:deep(.p-dropdown) {
  width: 100%;
  height: 48px; /* Фиксированная высота как у input */
  min-height: 48px;
  max-height: 48px;
}

:deep(.p-dropdown .p-dropdown-label) {
  padding: 12px 16px;
  font-size: 16px;
  line-height: 1.5;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

:deep(.p-dropdown .p-dropdown-trigger) {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.p-dropdown .p-dropdown-trigger-icon) {
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateY(-11px);
}

:deep(.p-dropdown.p-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

/* Стили для выпадающего списка */
:deep(.p-dropdown-panel) {
  max-height: 200px;
  overflow-y: auto;
}

:deep(.p-dropdown-items .p-dropdown-item) {
  padding: 12px 16px;
  font-size: 16px;
}

/* Дополнительные стили для центрирования текста */
:deep(.p-dropdown .p-dropdown-label.p-inputtext) {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 16px;
}

:deep(.p-dropdown .p-dropdown-label.p-placeholder) {
  color: #6c757d;
  display: flex;
  align-items: center;
  height: 100%;
}

/* Стили для кнопок */
.btn-primary, .btn-secondary, .btn-copy {
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
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn-secondary {
  background: #f8f9fa;
  color: #333;
  border: 2px solid #e1e5e9;
}
.btn-copy {
  background: #28a745;
  color: white;
  white-space: nowrap;
}
.btn-copy:hover {
  background: #218838;
}
.link-result {
  margin-top: 32px;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #28a745;
}

.link-result h3 {
  color: #28a745;
  margin-bottom: 16px;
}

.link-container {
  display: flex;
  gap: 12px;
  margin: 16px 0;
}

.link-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-family: monospace;
  font-size: 14px;
  background: white;
}

.link-info {
  margin: 16px 0;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.link-info p {
  margin: 8px 0;
  color: #666;
}

.links-list {
  display: grid;
  gap: 20px;
}

.link-item {
  padding: 20px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  background: #f8f9fa;
}

.link-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.link-role {
  font-weight: 600;
  color: #333;
  padding: 4px 12px;
  background: #667eea;
  color: white;
  border-radius: 20px;
  font-size: 14px;
}

.link-status {
  font-size: 14px;
  padding: 4px 12px;
  border-radius: 20px;
  background: #28a745;
  color: white;
}

.link-status.used {
  background: #6c757d;
}

.link-token {
  margin: 12px 0;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e1e5e9;
}

.link-token code {
  font-family: monospace;
  font-size: 14px;
  color: #333;
  word-break: break-all;
}

.link-details p {
  margin: 4px 0;
  font-size: 14px;
  color: #666;
}

.link-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

.btn-delete {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #dc3545;
  color: white;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-delete:hover:not(:disabled) {
  background: #c82333;
  transform: translateY(-1px);
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-delete i {
  font-size: 12px;
}

.loading, .no-links {
  text-align: center;
  padding: 40px;
  color: #666;
}

.loading p {
  margin-top: 16px;
}

/* Styles for user dropdown */
.user-dropdown {
  position: relative;
  display: inline-block;
}

.user-dropdown-toggle {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #f8f9fa;
  color: #333;
  transition: border-color 0.3s ease;
}

.user-dropdown-toggle:focus {
  outline: none;
  border-color: #667eea;
}

.user-dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background-color: #fff;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  display: none; /* Hidden by default */
}

.user-dropdown.open .user-dropdown-menu {
  display: block; /* Show when dropdown is open */
}

.user-option {
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-option:hover {
  background-color: #f0f0f0;
}

.user-option.selected {
  background-color: #e9ecef;
  font-weight: 600;
}

.selected-user {
  font-weight: 600;
  color: #333;
}

.clear-user-btn {
  padding: 8px 12px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background-color: #f8f9fa;
  color: #666;
  cursor: pointer;
  transition: background-color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
}

.clear-user-btn:hover {
  background-color: #e9ecef;
}

@media (max-width: 768px) {
  .admin-role-switch {
    padding: 20px 16px;
  }

  .admin-card {
    padding: 24px;
  }

  .link-container {
    flex-direction: column;
  }

  .link-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
}
</style>
