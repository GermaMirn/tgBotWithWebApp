<template>
  <div class="teachers-page">
    <div class="main-content">
      <div class="page-header">
        <h1>Преподаватели</h1>
        <p>Познакомьтесь с нашими опытными преподавателями</p>
      </div>

      <!-- Error state -->
      <div v-if="error" class="error-container">
        <i class="pi pi-exclamation-triangle error-icon"></i>
        <h2>Ошибка загрузки</h2>
        <p>{{ error }}</p>
        <button @click="loadTeachers" class="btn-retry">Попробовать снова</button>
      </div>

      <!-- Empty state -->
      <div v-else-if="teachers.length === 0" class="empty-state">
        <i class="pi pi-users empty-icon"></i>
        <h2>Пока нет преподавателей</h2>
        <p>Мы готовим подробную информацию о наших преподавателях</p>
      </div>

      <!-- Teachers list -->
      <div v-else class="teachers-grid">
        <div
          v-for="teacher in teachers"
          :key="teacher.id"
          class="teacher-card"
        >
          <div class="teacher-header">
            <div class="teacher-avatar">
              <i class="pi pi-user"></i>
            </div>
            <div class="teacher-info">
              <h3 class="teacher-name">{{ teacher.full_name || `Преподаватель ${teacher.id.slice(0, 8)}` }}</h3>
              <p class="teacher-specialization">{{ teacher.specialization }}</p>
            </div>
          </div>

          <div class="teacher-details">
            <div class="detail-item">
              <i class="pi pi-briefcase"></i>
              <span>{{ teacher.experience_years }} лет опыта</span>
            </div>

            <div class="detail-item">
              <i class="pi pi-dollar"></i>
              <span>{{ teacher.hourly_rate }} ₽/час</span>
            </div>

            <div v-if="teacher.education" class="detail-item">
              <i class="pi pi-graduation-cap"></i>
              <span>{{ teacher.education }}</span>
            </div>
          </div>

          <div v-if="teacher.bio" class="teacher-bio">
            <p>{{ teacher.bio }}</p>
          </div>

          <div v-if="teacher.certificates && teacher.certificates.length > 0" class="teacher-certificates">
            <h4>Сертификаты:</h4>
            <ul>
              <li v-for="cert in teacher.certificates" :key="cert">{{ cert }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { teachersApi } from '@/services/api/teachers'
import type { Teacher } from '@/types/teacher'
import { useUiStore } from '@/stores/ui'

export default defineComponent({
  name: 'TeachersPage',
  data() {
    return {
      ui: useUiStore(),
      teachers: [] as Teacher[],
      loading: true,
      error: null as string | null
    }
  },
  methods: {
    async loadTeachers() {
      try {
        this.loading = true
        this.error = null
        this.ui.showLoading('Загрузка преподавателей...')
        this.teachers = await teachersApi.getTeachers()
      } catch (err) {
        console.error('Error loading teachers:', err)
        this.error = 'Не удалось загрузить список преподавателей'
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: this.error, life: 4000 })
      } finally {
        this.loading = false
        this.ui.hideLoading()
      }
    }
  },
  mounted() {
    this.loadTeachers()
  }
})
</script>

<style scoped>
.teachers-page {
  min-height: 100vh;
  background: var(--surface-ground);
}

.main-content {
  padding: 1rem;
  max-width: 1200px;
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

.loading-container {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-container p {
  margin-top: 1rem;
  color: var(--text-color-secondary);
}

.error-container {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--surface-card);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-icon {
  font-size: 3rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.error-container h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.error-container p {
  color: var(--text-color-secondary);
  margin-bottom: 1.5rem;
}

.btn-retry {
  padding: 0.75rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-retry:hover {
  background: var(--primary-600);
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: var(--surface-card);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.empty-state h2 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.empty-state p {
  font-size: 1.125rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.teachers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.teacher-card {
  background: var(--surface-card);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.teacher-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.teacher-header {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.teacher-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.teacher-avatar i {
  font-size: 1.5rem;
  color: white;
}

.teacher-info {
  flex: 1;
}

.teacher-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: var(--text-color);
}

.teacher-specialization {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.teacher-details {
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.detail-item i {
  margin-right: 0.5rem;
  color: var(--primary-color);
  width: 16px;
}

.teacher-bio {
  margin-bottom: 1rem;
  padding: 1rem;
  background: var(--surface-ground);
  border-radius: 8px;
}

.teacher-bio p {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--text-color);
}

.teacher-certificates {
  border-top: 1px solid var(--surface-border);
  padding-top: 1rem;
}

.teacher-certificates h4 {
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.teacher-certificates ul {
  margin: 0;
  padding-left: 1.25rem;
}

.teacher-certificates li {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.25rem;
}

@media (max-width: 768px) {
  .teachers-grid {
    grid-template-columns: 1fr;
  }

  .teacher-card {
    padding: 1rem;
  }

  .teacher-header {
    flex-direction: column;
    text-align: center;
  }

  .teacher-avatar {
    margin-right: 0;
    margin-bottom: 1rem;
  }
}
</style>

