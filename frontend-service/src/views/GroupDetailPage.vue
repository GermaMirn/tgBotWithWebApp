<template>
  <div class="group-detail-page">
    <div v-if="loading" class="loading-overlay">
      <i class="pi pi-spin pi-spinner spinner"></i>
      <p>Загрузка группы...</p>
    </div>

    <div v-else-if="group" class="group-content">
      <h1 class="group-title">{{ group.name }}</h1>
      <div class="group-info">
        <div class="group-info-item"><strong>Описание:</strong> {{ group.description || 'Нет описания' }}</div>
        <div class="group-info-item"><strong>Язык:</strong> {{ group.language }}</div>
        <div class="group-info-item"><strong>Уровень:</strong> {{ group.level }}</div>
        <div class="group-info-item"><strong>Тип:</strong> {{ group.group_type }}</div>
        <div class="group-info-item"><strong>Макс. студентов:</strong> {{ group.max_students }}</div>
        <div class="group-info-item"><strong>Дата начала:</strong> {{ formatDate(group.start_date) }}</div>
        <div class="group-info-item"><strong>Дата окончания:</strong> {{ formatDate(group.end_date) }}</div>
      </div>

      <div class="detail-section">
        <h3>Учитель</h3>
        <div class="user-card">
          <i class="pi pi-user user-icon"></i>
          <span>{{ group.teacher?.full_name || '—' }}</span>
        </div>
      </div>

      <div class="detail-section">
        <h3>Студенты ({{ group.students.length }})</h3>
        <div class="students-list">
          <div
            class="user-card"
            v-for="student in group.students"
            :key="student.id"
          >
            <i class="pi pi-user user-icon"></i>
            <span>{{ student.full_name }}</span>

            <Button
              v-if="userRole === 'teacher' || userRole === 'admin'"
              icon="pi pi-trash"
              class="p-button-danger p-button-trash"
              outlined
              style="margin-left: auto;"
              @click="handleRemoveMember(student)"
            />
          </div>
        </div>
      </div>

      <div class="detail-section">
        <h3>Действия</h3>
        <div class="actions-grid">
          <Button
            v-if="userRole === 'teacher' || userRole === 'admin'"
            label="Пригласить студента"
            icon="pi pi-user-plus"
            class="action-button"
            outlined
            @click="inviteDialog = true"
          />
          <Button
            v-if="userRole === 'student'"
            label="Покинуть группу"
            icon="pi pi-sign-out"
            class="action-button p-button-danger"
            outlined
            @click="handleLeaveGroup"
          />
          <Button
            label="Назад"
            icon="pi pi-arrow-left"
            class="action-button"
            outlined
            @click="$router.back()"
          />
        </div>
      </div>
    </div>

    <div v-else>
      <p>Группа не найдена</p>
    </div>

    <!-- Диалог приглашения -->
    <InviteUserIntoGroupDialog
      v-model:visible="inviteDialog"
      :group-id="group?.id"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { groupsApi } from '@/services/api/groups'
import { useUserStore } from '@/stores/user'
import type { Group } from '@/types/groups'
import Button from 'primevue/button'
import InviteUserIntoGroupDialog from '@/components/dialogs/InviteUserIntoGroupDialog.vue'

export default defineComponent({
  name: 'GroupDetailPage',
  components: {
    Button,
    InviteUserIntoGroupDialog
  },
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      userStore: useUserStore(),
      loading: false,
      group: null as Group | null,
      inviteDialog: false,
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
    formatDate(date: string | null) {
      return date ? new Date(date).toLocaleDateString() : '—'
    },
    async loadGroup() {
      this.loading = true
      try {
        const groupData = await groupsApi.getGroupById(Number(this.id))
        groupData.students = Array.isArray(groupData.students)
          ? groupData.students
          : groupData.students
            ? [groupData.students]
            : []
        groupData.students = groupData.students.map(s => ({
          ...s,
          full_name: s.full_name || s.username || 'Неизвестный студент'
        }))
        this.group = groupData
      } catch (e) {
        console.error('Ошибка загрузки группы', e)
        this.group = null
      } finally {
        this.loading = false
      }
    },
    async handleLeaveGroup() {
      if (!confirm('Вы уверены, что хотите покинуть группу?')) return

      try {
        this.loading = true
        await groupsApi.leaveGroup(Number(this.id))
        this.$toast.add({
          severity: 'success',
          summary: 'Выход из группы',
          detail: 'Вы успешно покинули группу',
          life: 3000
        })
        // После выхода можно редиректить на список групп
        this.$router.push('/groups')
      } catch (error) {
        this.$toast.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: 'Не удалось покинуть группу',
          life: 3000
        })
        console.error(error)
      } finally {
        this.loading = false
      }
    },
    async handleRemoveMember(student: any) {
      if (!confirm(`Вы уверены, что хотите удалить ${student.full_name} из группы?`)) return

      try {
        this.loading = true
        await groupsApi.removeMember(Number(this.id), student.telegram_id)
        this.$toast.add({ severity: 'success', summary: 'Участник удалён', detail: `${student.full_name} удалён из группы`, life: 3000 })
        // Обновляем локальный список студентов
        if (this.group) {
          this.group.students = this.group.students.filter(s => s.id !== student.id)
        }
      } catch (error) {
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось удалить участника', life: 3000 })
        console.error(error)
      } finally { this.loading = false }
    }
  },
  mounted() {
    this.loadGroup()
  }
})
</script>

<style scoped>
.group-detail-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.p-button-trash {
  padding: 0.2rem;
  background: transparent;
  box-shadow: none;
  cursor: pointer;
}

.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 1rem;
  gap: 1rem;
  color: var(--text-color, #fff);
}

.spinner {
  font-size: 2.5rem;
  color: var(--primary-color);
}

.group-info {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

.group-info-item {
  flex: 1 1 200px;
}

.group-info-item strong {
  color: #333;
}

.group-title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  text-align: center;
}

.group-info p {
  margin: 0.25rem 0;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  margin: 0.25rem 0;
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
}

.user-icon {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.students-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
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

.action-button {
  width: 100%;
  justify-content: flex-start;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

@media screen and (max-width: 768px) {
  .group-title {
    font-size: 2rem;
  }
  .user-card {
    flex: 1 1 100%;
  }
  .students-list {
    flex-direction: column;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
