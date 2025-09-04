<template>
  <div class="invite-page">
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="invite-content">
      <h1 class="invite-title">Приглашение в группу "{{ group?.name }}"</h1>
      <div class="invite-info">
        <p><strong>Описание:</strong> {{ group?.description || '—' }}</p>
        <p><strong>Язык:</strong> {{ group?.language }}</p>
        <p><strong>Уровень:</strong> {{ group?.level }}</p>
        <p><strong>Макс. студентов:</strong> {{ group?.current_students }}/{{ group?.max_students }}</p>
        <p><strong>Дата начала:</strong> {{ formatDate(group?.start_date) }}</p>
        <p><strong>Дата окончания:</strong> {{ formatDate(group?.end_date) }}</p>
      </div>


      <div class="detail-section">
        <h3>Действия</h3>

        <div class="actions-grid">
          <Button
            label="Присоединиться"
            @click="acceptInvite"
            outlined
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import Button from 'primevue/button'
import { groupsApi } from '@/services/api/groups'

export default defineComponent({
  name: 'GroupInvitePage',
  components: { Button },
  data() {
    return {
      loading: true,
      error: '',
      group: null as any
    }
  },
  async mounted() {
    const token = this.$route.params.token as string
    try {
      this.group = await groupsApi.getInvitation(token)
    } catch (err: any) {
      this.error = err?.response?.data || 'Ошибка загрузки приглашения'
    } finally {
      this.loading = false
    }
  },
  methods: {
    formatDate(date: string | null) {
      return date ? new Date(date).toLocaleDateString() : '—'
    },
    async acceptInvite() {
      const token = this.$route.params.token as string
      try {
        await groupsApi.acceptInvitation(token)
        this.$toast.add({ severity: 'success', summary: 'Готово', detail: 'Вы присоединились к группе' })
        this.$router.push(`/groups/${this.group.id}`)
      } catch (err: any) {
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: err?.response?.data || err.message })
      }
    }
  }
})
</script>

<style scoped>
.invite-page {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.loading,
.error {
  padding: 3rem 1rem;
  font-size: 1.25rem;
  color: var(--text-color, #333);
}

.error {
  color: #d32f2f;
}

.invite-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 1.5rem;
  color: var(--text-color, #222);
}

.invite-info {
  margin-bottom: 2rem;
  font-size: 1.1rem;
  line-height: 1.6;
}

.invite-info p {
  margin: 0.5rem 0;
}

.invite-info strong {
  color: var(--primary-color);
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

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}
</style>
