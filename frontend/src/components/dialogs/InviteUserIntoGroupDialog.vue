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
    Button
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
      createInvitation,
      copyInviteLink,
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
</style>
