<template>
  <Dialog
    v-model:visible="visibleLocal"
    modal
    header="Пригласить в группу"
    :closable="true"
    :style="{ width: '90vw', maxWidth: '500px' }"
  >
    <div class="edit-form">
      <!-- выбор студента -->
      <div class="field field--stack">
        <InputGroup>
          <InputGroupAddon>
            <i class="pi pi-user"></i>
          </InputGroupAddon>
          <FloatLabel>
            <Dropdown
              id="userSelect"
              v-model="selectedStudent"
              :options="students"
              filter
              optionLabel="full_name"
              placeholder=" "
              class="dropdown"
            />
            <label for="userSelect">Пользователь</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- сообщение -->
      <div class="field field--stack">
        <InputGroup>
          <InputGroupAddon>
            <i class="pi pi-comment"></i>
          </InputGroupAddon>
          <FloatLabel>
            <InputText
              id="inviteMessage"
              v-model="inviteMessage"
              textarea
              rows="3"
              autoResize
            />
            <label for="inviteMessage">Сообщение (опционально)</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- время жизни -->
      <div class="field field--stack">
        <InputGroup>
          <InputGroupAddon>
            <i class="pi pi-clock"></i>
          </InputGroupAddon>
          <FloatLabel>
            <InputNumber
              id="inviteExpires"
              v-model="inviteExpires"
              :min="1"
              :max="168"
            />
            <label for="inviteExpires">Время жизни (часы)</label>
          </FloatLabel>
        </InputGroup>
      </div>

      <!-- готовая ссылка -->
      <div v-if="inviteCreatedLink" class="field field--stack">
        <InputGroup>
          <InputGroupAddon>
            <i class="pi pi-link"></i>
          </InputGroupAddon>
          <FloatLabel>
            <InputText id="inviteLink" v-model="inviteCreatedLink" readonly />
            <label for="inviteLink">Ссылка приглашения</label>
          </FloatLabel>
          <Button icon="pi pi-copy" @click="copyInviteLink" />
        </InputGroup>
      </div>

      <!-- Активные ссылки для выбранного студента -->
      <div v-if="selectedStudent && studentInvitations.length > 0" class="field">
        <div class="invitations-list">
          <h4>Активные приглашения для {{ selectedStudent.full_name }}:</h4>
          <div v-for="inv in studentInvitations" :key="inv.id" class="invitation-item">
            <div class="invitation-info">
              <div class="invitation-header">
                <span class="invitation-group">{{ inv.group_name }}</span>
                <Tag
                  :value="inv.is_active ? 'Активно' : getStatusLabel(inv.status)"
                  :severity="inv.is_active ? 'success' : 'secondary'"
                />
              </div>
              <div class="invitation-link">
                <InputText :value="inv.invite_url" readonly class="link-input" />
              </div>
              <div v-if="inv.message" class="invitation-message">
                <small><strong>Сообщение:</strong> {{ inv.message }}</small>
              </div>
              <div class="invitation-dates">
                <small v-if="inv.expires_at">
                  Действительно до: {{ formatDate(inv.expires_at) }}
                </small>
              </div>
              <div class="invitation-actions">
                <Button
                  label="Копировать"
                  icon="pi pi-copy"
                  size="small"
                  outlined
                  class="action-button"
                  @click="copyLink(inv.invite_url)"
                />
                <br />
                <Button
                  label="Удалить"
                  icon="pi pi-trash"
                  size="small"
                  severity="danger"
                  outlined
                  class="action-button"
                  :loading="deletingInvitationId === inv.id"
                  @click="deleteInvitation(inv.id)"
                />
              </div>
            </div>
          </div>
        </div>
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
        label="Создать"
        icon="pi pi-share-alt"
        :loading="inviteCreating"
        @click="createInvitation"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, ref, watch, onMounted } from 'vue'
import Dialog from 'primevue/dialog'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import FloatLabel from 'primevue/floatlabel'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'
import { adminApi, User } from '@/services/api/admin'
import { groupsApi } from '@/services/api/groups'

export default defineComponent({
  name: 'InviteUserIntoGroupDialog',
  components: {
    Dialog,
    InputGroup,
    InputGroupAddon,
    FloatLabel,
    InputNumber,
    InputText,
    Dropdown,
    Button,
    Tag
  },
  props: {
    visible: { type: Boolean, required: true },
    groupId: { type: Number, required: true }
  },
  emits: ['update:visible'],
  setup(props, { emit }) {
    const toast = useToast()
    const visibleLocal = ref(false)

    const students = ref<User[]>([])
    const selectedStudent = ref<User | null>(null)
    const inviteMessage = ref('')
    const inviteExpires = ref(24)
    const inviteCreatedLink = ref('')
    const inviteCreating = ref(false)
    const studentInvitations = ref<any[]>([])
    const loadingInvitations = ref(false)
    const deletingInvitationId = ref<number | null>(null)

    // следим за props.visible и синхронизируем локальную переменную
    watch(() => props.visible, (val) => {
      visibleLocal.value = val
    })

    // когда локальная переменная меняется — сообщаем родителю
    watch(visibleLocal, (val) => {
      emit('update:visible', val)
      if (!val) {
        selectedStudent.value = null
        inviteMessage.value = ''
        inviteExpires.value = 24
        inviteCreatedLink.value = ''
        studentInvitations.value = []
      }
    })

    // Загружаем приглашения при выборе студента
    watch(selectedStudent, async (newStudent) => {
      if (newStudent?.telegram_id) {
        await loadStudentInvitations(newStudent.telegram_id)
      } else {
        studentInvitations.value = []
      }
    })

    const loadStudents = async () => {
      try {
        const res = await adminApi.getUsers("student")
        students.value = res.map((s: any) => ({
          ...s,
          full_name: s.full_name || s.username || 'Без имени'
        }))
      } catch (e) {
        console.error('Ошибка загрузки студентов', e)
      }
    }

    const loadStudentInvitations = async (telegramId: number) => {
      loadingInvitations.value = true
      try {
        const invitations = await groupsApi.getStudentInvitations(telegramId)
        // Фильтруем только приглашения для текущей группы
        studentInvitations.value = invitations.filter((inv: any) => inv.group_id === props.groupId)
      } catch (err) {
        console.error('Ошибка загрузки приглашений', err)
        studentInvitations.value = []
      } finally {
        loadingInvitations.value = false
      }
    }

    const createInvitation = async () => {
      inviteCreating.value = true
      try {
        const payload: any = {
          group_id: props.groupId,
          expires_in_hours: inviteExpires.value || 24,
          message: inviteMessage.value || undefined
        }
        if (selectedStudent.value?.telegram_id) {
          payload.student_telegram_id = selectedStudent.value.telegram_id
        }
        const res = await groupsApi.createInvitation(payload)
        const token = res.invite_token || res.token || res.inviteToken
        if (token) {
          inviteCreatedLink.value = `${window.location.origin}/groups/invite/${token}`
          toast.add({
            severity: 'success',
            summary: 'Приглашение создано',
            detail: 'Ссылка для приглашения успешно создана',
            life: 3000
          })
          // Обновляем список приглашений, если студент выбран
          if (selectedStudent.value?.telegram_id) {
            await loadStudentInvitations(selectedStudent.value.telegram_id)
          }
        }
      } catch (err) {
        toast.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: 'Не удалось создать приглашение',
          life: 3000
        })
      } finally {
        inviteCreating.value = false
      }
    }

    const deleteInvitation = async (invitationId: number) => {
      deletingInvitationId.value = invitationId
      try {
        await groupsApi.deleteInvitation(invitationId)
        toast.add({
          severity: 'success',
          summary: 'Успешно',
          detail: 'Приглашение удалено',
          life: 3000
        })
        // Обновляем список приглашений
        if (selectedStudent.value?.telegram_id) {
          await loadStudentInvitations(selectedStudent.value.telegram_id)
        }
      } catch (err) {
        toast.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: 'Не удалось удалить приглашение',
          life: 3000
        })
      } finally {
        deletingInvitationId.value = null
      }
    }

    const getStatusLabel = (status: string) => {
      const statusMap: Record<string, string> = {
        'pending': 'Ожидает',
        'accepted': 'Принято',
        'declined': 'Отклонено',
        'expired': 'Истекло'
      }
      return statusMap[status] || status
    }

    const formatDate = (dateString: string) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ru-RU')
    }

    const copyLink = (link: string) => {
      navigator.clipboard?.writeText(link)
      toast.add({
        severity: 'info',
        summary: 'Скопировано',
        detail: 'Ссылка скопирована в буфер обмена',
        life: 2000
      })
    }

    const copyInviteLink = () => {
      if (!inviteCreatedLink.value) return
      navigator.clipboard?.writeText(inviteCreatedLink.value)
    }

    const close = () => {
      visibleLocal.value = false
    }

    onMounted(loadStudents)

    return {
      visibleLocal,
      students,
      selectedStudent,
      inviteMessage,
      inviteExpires,
      inviteCreatedLink,
      inviteCreating,
      studentInvitations,
      loadingInvitations,
      deletingInvitationId,
      createInvitation,
      copyInviteLink,
      deleteInvitation,
      getStatusLabel,
      formatDate,
      copyLink,
      close
    }
  }
})
</script>


<style scoped>
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 1.2rem;
}

.field {
  margin-bottom: 1rem;
}

#inviteLink {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.invitations-list {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--surface-ground);
  border-radius: 8px;
}

.invitations-list h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
}

.invitation-item {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: var(--surface-card);
  border-radius: 6px;
  border: 1px solid var(--surface-border);
}

.invitation-item:last-child {
  margin-bottom: 0;
}

.invitation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.invitation-group {
  font-weight: 600;
  font-size: 0.95rem;
}

.invitation-link {
  margin-bottom: 0.5rem;
}

.link-input {
  width: 100%;
  font-size: 0.85rem;
}

.invitation-message {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: var(--surface-50);
  border-radius: 4px;
  color: var(--text-color-secondary);
}

.invitation-dates {
  margin-top: 0.5rem;
  color: var(--text-color-secondary);
}

.invitation-actions {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--surface-border);
}

.invitation-actions br {
  display: block;
  margin: 5px 0;
  content: "";
}

.action-button {
  width: 100%;
}

.invitation-actions .p-button:not(:last-child) {
  margin-bottom: 5px;
}
</style>
