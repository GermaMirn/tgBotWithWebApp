<template>
  <div class="groups-page">
    <div class="main-content">
      <div class="page-header">
        <h1>Мои группы</h1>

        <p v-if="userRole === 'student'">Список групп, в которых вы обучаетесь</p>
        <p v-if="userRole === 'teacher'  || userRole === 'admin'">Список групп, в которых вы препадаёте</p>
      </div>

      <div
        class="detail-section"
        v-if="userRole === 'teacher'  || userRole === 'admin'"
      >
        <h3>Действия</h3>

        <div class="actions-grid">
          <Button
            label="Создать группу"
            icon="pi pi-users"
            class="action-button"
            @click="openCreateGroup"
            outlined
          />
        </div>
      </div>

      <!-- Остальной контент -->
      <div v-if="loading && !showCreateGroup" class="loading-overlay">
        <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
        <p>Загрузка групп...</p>
      </div>

      <div v-else class="detail-section">
        <h3>Группы</h3>

        <div v-if="groups.length > 0" class="groups-list">
          <div v-for="group in groups" :key="group.id" class="group-card">
            <h3>{{ group.name }}</h3>
            <p v-if="group.description">{{ group.description }}</p>
            <p v-else><em>Описание отсутствует</em></p>

            <div class="actions-grid">
              <Button
                label="Подробнее"
                icon="pi pi-info-circle"
                text
                outlined
                @click="$router.push(`/groups/${group.id}`)"
              />

              <Button
                v-if="userRole === 'teacher' || userRole === 'admin'"
                label="Изменить данные"
                icon="pi pi-pencil"
                text
                outlined
                @click="openEditGroup(group)"
              />

              <Button
                v-if="userRole === 'teacher' || userRole === 'admin'"
                label="Удалить"
                icon="pi pi-trash"
                text
                class="delete-btn"
                @click="deleteGroup(group.id)"
              />
            </div>
          </div>
        </div>
        <div v-else class="no-groups">
          <p>Группы не найдены.</p>
        </div>
      </div>

      <!-- Модалка создания группы -->
      <CreateGroupDialog
        v-model:visible="showCreateGroup"
        :mode="mode"
        :form="dialogForm"
        :loading="loading"
        :language-options="languageOptions"
        :level-options="levelOptions"
        :type-options="typeOptions"
        @cancel="showCreateGroup = false"
        @save="createOrUpdateGroup"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useUserStore } from '@/stores/user'
import { groupsApi } from '@/services/api/groups'
import { languagesApi } from '@/services/api/languages'
import type { Group } from '@/types/groups'
import type { StudioLanguage } from '@/types/languages'
import Button from 'primevue/button'
import CreateGroupDialog from '@/components/dialogs/CreateGroupDialog.vue'

export default defineComponent({
  name: 'UserGroupsPage',
  components: {
    Button,
    CreateGroupDialog
  },
  data() {
    return {
      userStore: useUserStore(),
      loading: false,
      groups: [] as Group[],
      showCreateGroup: false,
      mode: 'create' as 'create' | 'edit',
      editingGroupId: null as number | null,
      dialogForm: {
        name: '',
        description: '',
        language: '',
        level: '',
        group_type: 'REGULAR' as Group['group_type'],
        max_students: 10,
        start_date: null as string | null,
        end_date: null as string | null,
      },
      languageOptions: [] as Array<{ label: string; value: string }>,
      levelOptions: [
        { label: 'Начальный', value: 'beginner' },
        { label: 'Средний', value: 'intermediate' },
        { label: 'Продвинутый', value: 'advanced' },
      ],
      typeOptions: [
        { label: 'Регулярный', value: 'REGULAR' },
        { label: 'Интенсивный', value: 'INTENSIVE' },
        { label: 'Разговорный', value: 'CONVERSATION' },
        { label: 'Грамматический', value: 'GRAMMAR' },
      ],
    }
  },
  computed: {
    userRole(): string {
      return this.userStore.userRole
    },
    isAuthenticated(): boolean {
      return this.userStore.isAuthenticated
    }
  },
  methods: {
    async loadLanguages() {
      try {
        const languages = await languagesApi.getLanguages(true) // только активные
        this.languageOptions = languages.map(lang => ({
          label: lang.name,
          value: lang.code
        }))
      } catch (error) {
        console.error('Failed to load languages:', error)
        // Если не удалось загрузить, используем пустой список
        this.languageOptions = []
      }
    },
    async loadGroups() {
      if (!this.isAuthenticated) return
      this.loading = true
      try {
        if (this.userRole === 'teacher' || this.userRole === 'admin') {
          this.groups = await groupsApi.getTeacherGroups()
        } else if (this.userRole === 'student') {
          this.groups = await groupsApi.getStudentGroups()
        } else {
          this.groups = []
        }
      } catch (error) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка загрузки',
          detail: 'Не удалось загрузить группы',
          life: 5000,
        })
      } finally {
        this.loading = false
      }
    },
    async createOrUpdateGroup() {
      if (!this.dialogForm.name.trim()) {
        this.$toast.add({
          severity: 'warn',
          summary: 'Ошибка',
          detail: 'Название группы обязательно',
          life: 3000,
        })
        return
      }

      this.loading = true
      try {
        if (this.mode === 'create') {
          const newGroup = await groupsApi.createGroup(this.dialogForm)
          this.groups.push(newGroup)
          this.$toast.add({
            severity: 'success',
            summary: 'Группа создана',
            detail: `Группа "${newGroup.name}" успешно создана`,
            life: 3000,
          })
        } else if (this.mode === 'edit' && this.editingGroupId) {
          const updatedGroup = await groupsApi.updateGroup(this.editingGroupId, this.dialogForm)
          const index = this.groups.findIndex(g => g.id === updatedGroup.id)
          if (index !== -1) this.groups.splice(index, 1, updatedGroup)

          this.$toast.add({
            severity: 'success',
            summary: 'Группа обновлена',
            detail: `Группа "${updatedGroup.name}" успешно обновлена`,
            life: 3000,
          })
        }
        this.showCreateGroup = false
      } catch (error) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка сохранения',
          detail: 'Не удалось сохранить группу',
          life: 5000,
        })
      } finally {
        this.loading = false
      }
    },
    async deleteGroup(groupId: number) {
      const confirmed = window.confirm('Вы уверены, что хотите удалить группу?')
      if (!confirmed) return

      try {
        this.loading = true
        await groupsApi.deleteGroup(groupId)
        this.groups = this.groups.filter(g => g.id !== groupId)
        this.$toast.add({
          severity: 'success',
          summary: 'Группа удалена',
          detail: 'Группа успешно удалена',
          life: 3000,
        })
      } catch (error) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка удаления',
          detail: 'Не удалось удалить группу',
          life: 5000,
        })
      } finally {
        this.loading = false
      }
    },
    openCreateGroup() {
      this.mode = 'create'
      this.editingGroupId = null
      this.dialogForm = {
        name: '',
        description: '',
        language: '',
        level: '',
        group_type: 'REGULAR',
        max_students: 10,
        start_date: null,
        end_date: null,
      }
      this.showCreateGroup = true
    },
    openEditGroup(group: Group) {
      this.mode = 'edit'
      this.editingGroupId = group.id
      this.dialogForm = {
        name: group.name,
        description: group.description || '',
        language: group.language,
        level: group.level,
        group_type: group.group_type,
        max_students: group.max_students,
        start_date: group.start_date,
        end_date: group.end_date,
      }
      this.showCreateGroup = true
    },
  },
  async mounted() {
    await this.loadLanguages()
    this.loadGroups()
  }
})
</script>

<style scoped>
.groups-page {
  min-height: 100vh;
  background: var(--surface-ground);
}

.main-content {
  padding: 1rem 0;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 1rem;
  padding: 2rem 0;
}

.groups-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.group-card {
  flex: 1 1 300px;
  border: 1px solid #ddd;
  padding: 1rem;
  border-radius: 8px;
  background-color: #fafafa;
  box-shadow: 0 0 6px rgb(0 0 0 / 0.05);
}

.group-card h3 {
  margin: 0 0 0.5rem 0;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.2rem;
  color: #555;
}

.no-groups {
  font-style: italic;
  color: #888;
  text-align: center;
  margin-top: 2rem;
}

.create-group-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.create-group-btn:hover {
  background-color: #2563eb;
}

.delete-btn {
  background-color: #00000000;
  color: #ef4444;
  border: none;
}

.delete-btn:hover {
  background-color: #dd373707;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  width: 300px;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
}

.modal-content input,
.modal-content textarea {
  width: 100%;
  margin-bottom: 0.7rem;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.modal-actions button {
  padding: 0.4rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-actions button:first-child {
  background-color: #3b82f6;
  color: white;
}

.modal-actions button:last-child {
  background-color: #e5e7eb;
}

/* Действия */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.action-button {
  width: 100%;
  justify-content: flex-start;
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

@media (max-width: 768px) {
  .main-content {
    padding: 0.5rem;
  }

  .page-header {
    padding: 1.5rem;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
