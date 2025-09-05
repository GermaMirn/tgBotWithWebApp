<template>
  <div class="calendar-page">
    <!-- Основной контент -->
    <div class="main-content">
      <!-- Заголовок -->
      <div class="page-header">
        <h1>Календарь занятий</h1>
        <p>Выберите удобное время для записи на занятия</p>
      </div>

      <!-- Выбор преподавателя (для студентов и админов) -->
      <div v-if="!isTeacher" class="teacher-selection">
        <div class="teacher-selector">
          <label for="teacher-select">Выберите преподавателя</label>
          <Dropdown
            id="teacher-select"
            v-model="selectedTeacher"
            :options="teachers"
            optionLabel="full_name"
            placeholder="Выберите преподавателя для записи"
            class="teacher-dropdown"
            @change="onTeacherChange"
          />
        </div>
      </div>

      <!-- Календарь -->
      <div v-if="!isTeacher ? selectedTeacher : true" class="calendar-container">
        <!-- Навигация по месяцам -->
        <div class="calendar-navigation">
          <div class="month-selector">
            <h2>{{ currentMonthName }} {{ currentYear }}</h2>
            <p class="month-subtitle">
              {{ isTeacher ? 'Управление моим расписанием' : isAdmin ? `Управление расписанием ${selectedTeacher?.full_name}` : `Расписание ${selectedTeacher?.full_name}` }}
            </p>
          </div>
        </div>

        <!-- Сетка календаря -->
        <div class="calendar-grid">
          <!-- Заголовки дней недели -->
          <div class="calendar-header">
            <div
              v-for="dayName in dayNames"
              :key="dayName"
              class="day-header"
            >
              {{ dayName }}
            </div>
          </div>

          <!-- Дни месяца -->
          <div class="calendar-days">
            <div
              v-for="day in calendarDays"
              :key="day.key"
              class="calendar-day"
              :class="{
                'other-month': day.otherMonth,
                'today': day.isToday,
                'weekend': day.isWeekend,
                'work-day': day.isWorkDay,
                'non-work-day': !day.isWorkDay && !day.otherMonth,
                'non-work-cursor-day': !day.isWorkDay && day.otherMonth && (!isTeacher || !isAdmin),
                'has-events': day.hasEvents,
                'selected': selectedDate && isSameDay(day.date, selectedDate)
              }"
              @click="selectDate(day)"
            >
              <div class="day-number">{{ day.dayNumber }}</div>
              <div v-if="day.hasEvents" class="day-events">
                <div class="event-dot"></div>
              </div>

            </div>
          </div>
        </div>

        <!-- Информация о выбранном дне -->
        <div v-if="selectedDate" class="selected-day-info">
          <div class="selected-day-header">
            <h3>{{ formatSelectedDate(selectedDate) }}</h3>
            <p class="day-description">{{ getDayDescription(selectedDate) }}</p>
          </div>

          <!-- Временные слоты для студентов -->
          <div class="time-slots-section">
            <h4>Доступное время</h4>
            <div class="time-slots-grid">
              <div
                v-for="slot in availableSlots"
                :key="slot.time"
                class="time-slot"
                :class="{
                  'available': slot.available,
                  'booked': slot.booked,
                  'unavailable': !slot.available
                }"
                @click="slot.available ? bookSlot(slot) : null"
              >
                <div class="slot-time">{{ slot.time }}</div>
                <div class="slot-status">
                  <span v-if="slot.available" class="status-available">
                    <i class="pi pi-check"></i> Свободно
                  </span>
                  <span v-else-if="slot.booked" class="status-booked">
                    <i class="pi pi-times"></i> Занято
                  </span>
                  <span v-else class="status-unavailable">
                    <i class="pi pi-clock"></i> Недоступно
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Настройки дня для учителей и админов -->
          <div v-if="isTeacher || isAdmin" class="day-settings-section">
            <h4>Настройки дня</h4>

            <!-- Переключатель активности дня -->
            <div class="activation-toggle">
              <label class="toggle-label">
                <input type="checkbox" :checked="daySettings.isActive" @change="toggleDayActivity" />
                <span class="toggle-text">Отметить день как рабочий</span>
              </label>
            </div>

            <!-- Настройки времени (только если день активен) -->
            <div v-if="daySettings.isActive" class="time-settings">
              <h5>Рабочие часы</h5>

              <div class="time-range">
                <div class="time-input-group">
                  <label>Начало работы</label>
                  <input type="time" v-model="daySettings.startTime" class="time-input" />
                </div>

                <div class="time-input-group">
                  <label>Конец работы</label>
                  <input type="time" v-model="daySettings.endTime" class="time-input" />
                </div>
              </div>

              <Button
                label="Создать урок"
                icon="pi pi-plus"
                @click="openCreateLessonDialog"
                outlined
                class="action-button"
              />
            </div>

            <!-- Кнопки действий -->
            <div class="settings-actions">
              <Button label="Сохранить" @click="saveDaySettings" class="save-btn" />
              <Button label="Отмена" severity="secondary" @click="cancelDaySettings" class="cancel-btn" />
            </div>
          </div>
        </div>

        <!-- Сообщение о выборе дня -->
        <div v-else class="select-day-message">
          <div class="message-content">
            <i class="pi pi-calendar message-icon"></i>
            <h3>{{ isTeacher ? 'Выберите день' : 'Выберите рабочий день' }}</h3>
            <p>{{ isTeacher ? 'Нажмите на любой день в календаре, чтобы управлять расписанием' : 'Нажмите на любой рабочий день в календаре, чтобы увидеть доступное время' }}</p>
          </div>
        </div>
      </div>

      <!-- Сообщение о выборе преподавателя (для студентов и админов) -->
      <div v-if="!isTeacher && !selectedTeacher" class="select-teacher-message">
        <div class="message-content">
          <i class="pi pi-users message-icon"></i>
          <h3>Выберите преподавателя</h3>
          <p>Для просмотра расписания выберите преподавателя из списка выше</p>
        </div>
      </div>
    </div>

    <!-- Диалог подтверждения бронирования -->
    <BookingLessonDialog
      v-model:visible="bookingDialog"
      :slot="selectedSlot"
      :date="selectedDate"
      :loading="bookingLoading"
      @confirm="confirmBooking"
    />

    <!-- Диалог создания урока -->
    <CreateLessonDialog
      v-model:visible="createLessonDialog"
      :lesson="newLesson"
      :session="newSession"
      :lesson-types="lessonTypes"
      @save="createLesson"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import { useUserStore } from '@/stores/user'
import { calendarApi } from '@/services/api/calendar'
import { teachersApi } from '@/services/api/teachers'
import { lessonsApi } from '@/services/api/lessons'
import type { CalendarResponse, TeacherSpecialDayUpdate, TimeSlotResponse } from '@/types/calendar'
import type { Teacher } from '@/types/teacher'
import { useUiStore } from '@/stores/ui'
import BookingLessonDialog from '@/components/dialogs/BookingLessonDialog.vue'
import CreateLessonDialog from '@/components/dialogs/CreateLessonDialog.vue'

export default defineComponent({
  name: 'CalendarViewPage',
  components: { Button, Dropdown, BookingLessonDialog, CreateLessonDialog },
  data() {
    return {
      userStore: useUserStore(),
      ui: useUiStore(),
      selectedTeacher: null as Teacher | null,
      selectedDate: null as Date | null,
      bookingDialog: false,
      bookingLoading: false,
      selectedSlot: null as TimeSlotResponse | null,
      daySettings: {
        isActive: false,
        startTime: '09:00',
        endTime: '18:00',
        bookedSlots: [] as string[]
      },
      loading: false,
      calendarData: null as CalendarResponse | null,
      teachers: [] as Teacher[],
      teachersLoading: false,
      availableSlots: [] as TimeSlotResponse[],
      currentDate: new Date(),
      dayNames: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'] as string[],
      createLessonDialog: false,
      newLesson: {
        title: "",
        lesson_type: null,
        language: "",
        level: "",
        description: ""
      },
      newSession: {
        start_time: null,
        end_time: null
      },
      lessonTypes: [
        { label: "Индивидуальный", value: "INDIVIDUAL" },
        { label: "Групповой", value: "GROUP" },
        { label: "Пробный", value: "TRIAL" }
      ]
    }
  },
  computed: {
    isTeacher(): boolean {
      return this.userStore.isTeacher
    },
    isAdmin(): boolean {
      return this.userStore.isAdmin
    },
    currentMonth(): number {
      return this.currentDate.getMonth()
    },
    currentYear(): number {
      return this.currentDate.getFullYear()
    },
    currentMonthName(): string {
      const months = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
      ]
      return months[this.currentMonth]
    },
    calendarDays(): Array<{
      date: Date; dayNumber: number; otherMonth: boolean; isToday: boolean; isWeekend: boolean; isWorkDay: boolean; hasEvents: boolean; key: string
    }> {
      const days: Array<{
        date: Date; dayNumber: number; otherMonth: boolean; isToday: boolean; isWeekend: boolean; isWorkDay: boolean; hasEvents: boolean; key: string
      }> = []
      const today = new Date()

      const firstDay = new Date(this.currentYear, this.currentMonth, 1)
      const lastDay = new Date(this.currentYear, this.currentMonth + 1, 0)

      let firstDayOfWeek = firstDay.getDay()
      firstDayOfWeek = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1

      for (let i = firstDayOfWeek - 1; i >= 0; i--) {
        const date = new Date(this.currentYear, this.currentMonth, -i, 12, 0, 0)
        let isWorkDay = false
        if (this.isTeacher || this.selectedTeacher) {
          if (this.calendarData) {
            const dayData = this.calendarData.days.find(d => new Date(d.date).toDateString() === date.toDateString())
            isWorkDay = dayData?.is_active || false
          }
        }
        let dayData = this.calendarData?.days.find(d => new Date(d.date).toDateString() === date.toDateString());
        days.push({
          date,
          dayNumber: date.getDate(),
          otherMonth: true,
          isToday: this.isSameDay(date, today),
          isWeekend: date.getDay() === 0 || date.getDay() === 6,
          isWorkDay,
          hasEvents: (dayData?.booked_slots?.length || 0) > 0,
          key: `prev-${date.getTime()}`
        })
      }

      for (let day = 1; day <= lastDay.getDate(); day++) {
        const date = new Date(this.currentYear, this.currentMonth, day, 12, 0, 0)
        let isWorkDay = false
        if (this.isTeacher || this.selectedTeacher) {
          if (this.calendarData) {
            const dayData = this.calendarData.days.find(d => new Date(d.date).toDateString() === date.toDateString())
            isWorkDay = dayData?.is_active || false
          }
        }
        let dayData = this.calendarData?.days.find(d => new Date(d.date).toDateString() === date.toDateString());
        days.push({
          date,
          dayNumber: day,
          otherMonth: false,
          isToday: this.isSameDay(date, today),
          isWeekend: date.getDay() === 0 || date.getDay() === 6,
          isWorkDay,
          hasEvents: (dayData?.booked_slots?.length || 0) > 0,
          key: `current-${date.getTime()}`
        })
      }

      const remainingDays = 42 - days.length
      for (let day = 1; day <= remainingDays; day++) {
        const date = new Date(this.currentYear, this.currentMonth + 1, day, 12, 0, 0)
        let isWorkDay = false
        if (this.isTeacher || this.selectedTeacher) {
          if (this.calendarData) {
            const dayData = this.calendarData.days.find(d => new Date(d.date).toDateString() === date.toDateString())
            isWorkDay = dayData?.is_active || false
          }
        }
        let dayData = this.calendarData?.days.find(d => new Date(d.date).toDateString() === date.toDateString());
        days.push({
          date,
          dayNumber: date.getDate(),
          otherMonth: true,
          isToday: this.isSameDay(date, today),
          isWeekend: date.getDay() === 0 || date.getDay() === 6,
          isWorkDay,
          hasEvents: (dayData?.booked_slots?.length || 0) > 0,
          key: `next-${date.getTime()}`
        })
      }
      return days
    }
  },
  methods: {
    async loadTeachers() {
      this.teachersLoading = true
      this.ui.showLoading('Загрузка преподавателей...')
      try {
        const teachersData = await teachersApi.getTeachers()
        this.teachers = teachersData
      } catch (error) {
        console.error('Ошибка загрузки преподавателей:', error)
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Ошибка загрузки списка преподавателей', life: 5000 })
      } finally {
        this.teachersLoading = false
        this.ui.hideLoading()
      }
    },
    async loadCalendarData() {
      if (!this.isTeacher && !this.selectedTeacher) return
      this.loading = true
      this.ui.showLoading('Загрузка календаря...')
      try {
        let teacherTelegramId: number | undefined
        if (this.isTeacher) {
          teacherTelegramId = this.userStore.userData?.telegram_id
        } else if (this.selectedTeacher) {
          teacherTelegramId = (this.selectedTeacher as any).telegram_id
        }
        if (!teacherTelegramId) return
        const startDate = new Date(this.currentYear, this.currentMonth, 1)
        const endDate = new Date(this.currentYear, this.currentMonth + 2, 0)
        this.calendarData = await calendarApi.getTeacherFullSchedule(
          teacherTelegramId,
          startDate.toISOString().split('T')[0],
          endDate.toISOString().split('T')[0]
        )
      } catch (error: any) {
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: `Ошибка загрузки календаря: ${error?.message || error}`, life: 5000 })
      } finally {
        this.loading = false
        this.ui.hideLoading()
      }
    },
    async onTeacherChange() {
      this.selectedDate = null
      if (this.selectedTeacher) {
        await this.loadCalendarData()
      }
    },
    isSameDay(date1: Date, date2: Date) {
      return date1.getDate() === date2.getDate() &&
             date1.getMonth() === date2.getMonth() &&
             date1.getFullYear() === date2.getFullYear()
    },
    selectDate(day: any) {
      if (day.otherMonth) return
      if (!this.isTeacher && !this.isAdmin && !day.isWorkDay) return

      this.selectedDate = day.date

      const dayData = this.calendarData?.days.find(d =>
        new Date(d.date).toDateString() === day.date.toDateString()
      )

      if (dayData) {
        this.daySettings = {
          isActive: dayData.is_active,
          startTime: dayData.start_time || '09:00',
          endTime: dayData.end_time || '18:00',
          bookedSlots: dayData.booked_slots || []
        }
      } else {
        this.daySettings = {
          isActive: day.isWorkDay || false,
          startTime: '09:00',
          endTime: '18:00',
          bookedSlots: []
        }
      }

      const dayIndex = this.calendarDays.findIndex(d =>
        !d.otherMonth && this.isSameDay(d.date, day.date)
      )
      if (dayIndex !== -1) this.calendarDays[dayIndex].isWorkDay = this.daySettings.isActive

      this.availableSlots = this.daySettings.bookedSlots.map(slotTime => ({
        time: slotTime,
        available: !this.daySettings.bookedSlots.includes(slotTime),
        booked: false,
        unavailable: false
      }))
    },
    formatSelectedDate(date: Date) {
      return date.toLocaleDateString('ru-RU', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
    },
    getDayDescription(date: Date) {
      const today = new Date()
      if (this.isSameDay(date, today)) return 'Сегодня'
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      if (this.isSameDay(date, tomorrow)) return 'Завтра'
      return ''
    },
    bookSlot(slot: TimeSlotResponse) {
      this.selectedSlot = slot
      this.bookingDialog = true
    },
    async confirmBooking() {
      this.bookingLoading = true
      this.ui.showLoading('Подтверждение записи...')
      try {
        await new Promise((resolve) => setTimeout(resolve, 1000))
        this.bookingDialog = false
        if (this.selectedSlot) {
          const slot = this.availableSlots.find((s) => s.time === this.selectedSlot!.time)
          if (slot) {
            slot.available = true
            slot.booked = false
          }
        }
        this.selectedSlot = null
        this.$toast.add({ severity: 'success', summary: 'Готово', detail: 'Запись подтверждена', life: 3000 })
      } catch (error) {
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось записаться на занятие', life: 5000 })
      } finally {
        this.bookingLoading = false
        this.ui.hideLoading()
      }
    },
    toggleDayActivity() {
      this.daySettings.isActive = !this.daySettings.isActive
    },
    async saveDaySettings() {
      this.ui.showLoading('Сохранение настроек...')
      try {
        let teacherTelegramId: number | undefined
        if (this.isTeacher) {
          teacherTelegramId = this.userStore.userData?.telegram_id
        } else if (this.isAdmin && this.selectedTeacher) {
          teacherTelegramId = (this.selectedTeacher as any).telegram_id
        }
        if (!teacherTelegramId || !this.selectedDate) {
          this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось определить пользователя или дату', life: 5000 })
          return
        }

        const scheduleDate = this.selectedDate.toISOString().split('T')[0]
        const scheduleData: TeacherSpecialDayUpdate = {
          teacher_telegram_id: teacherTelegramId,
          date: scheduleDate,
          start_time: this.daySettings.startTime,
          end_time: this.daySettings.endTime,
        }

        const existingDays = await calendarApi.getTeacherSpecialDays(
          teacherTelegramId,
          scheduleDate,
          scheduleDate
        )

        const existingDay = existingDays.find(d => d.date === scheduleDate)

        if (existingDay) {
          await calendarApi.updateTeacherSpecialDay(existingDay.id, scheduleData)
        } else {
          await calendarApi.createTeacherSpecialDay({
            teacher_telegram_id: teacherTelegramId,
            date: scheduleDate,
            start_time: this.daySettings.startTime,
            end_time: this.daySettings.endTime
          })
        }

        this.$toast.add({ severity: 'success', summary: 'Сохранено', detail: 'Настройки дня сохранены', life: 3000 })

        const dayIndex = this.calendarDays.findIndex((d) => !d.otherMonth && this.selectedDate && this.isSameDay(d.date, this.selectedDate))
        if (dayIndex !== -1) {
          this.calendarDays[dayIndex].isWorkDay = this.daySettings.isActive
        }
      } catch (error) {
        console.error('Ошибка при сохранении настроек:', error)
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Ошибка при сохранении настроек', life: 5000 })
      } finally {
        this.ui.hideLoading()
      }
    },
    async cancelDaySettings() {
      this.ui.showLoading('Отмена изменений...')
      try {
        let teacherTelegramId: number | undefined
        if (this.isTeacher) {
          teacherTelegramId = this.userStore.userData?.telegram_id
        } else if (this.isAdmin && this.selectedTeacher) {
          teacherTelegramId = (this.selectedTeacher as any).telegram_id
        }
        if (!teacherTelegramId || !this.selectedDate) return
        const scheduleDate = this.selectedDate.toISOString().split('T')[0]
        const daySchedule = await calendarApi.getTeacherDaySchedule(teacherTelegramId, scheduleDate)
        this.daySettings = {
          isActive: daySchedule.is_active,
          startTime: daySchedule.start_time,
          endTime: daySchedule.end_time,
          bookedSlots: daySchedule.booked_slots || []
        }
      } catch (error) {
        console.error('Ошибка при отмене настроек:', error)
        const day = this.calendarDays.find((d) => !d.otherMonth && this.selectedDate && this.isSameDay(d.date, this.selectedDate))
        if (day) {
          this.daySettings = {
            isActive: day.isWorkDay,
            startTime: '09:00',
            endTime: '18:00',
            bookedSlots: []
          }
        }
      } finally {
        this.ui.hideLoading()
      }
    },
    openCreateLessonDialog() {
    this.createLessonDialog = true
    },
    async createLesson() {
      if (!this.newLesson.title || !this.newSession.start_time || !this.newSession.end_time) return;

      const date = this.selectedDate

      const startDateTime = new Date(date)
      startDateTime.setHours(this.newSession.start_time.getHours())
      startDateTime.setMinutes(this.newSession.start_time.getMinutes())

      const endDateTime = new Date(date)
      endDateTime.setHours(this.newSession.end_time.getHours())
      endDateTime.setMinutes(this.newSession.end_time.getMinutes())

      const payload = {
        lesson: { ...this.newLesson, teacher_telegram_id: this.userStore.userData.telegram_id },
        session: {
          start_time: startDateTime.toISOString(),
          end_time: endDateTime.toISOString()
        },
        teacher_telegram_id: this.userStore.userData.telegram_id
      };

      try {
        await lessonsApi.createFullLesson(payload)
        this.$toast.add({ severity: 'success', summary: 'Успех', detail: 'Урок создан' })
        this.createLessonDialog = false

        const startTime = this.formatTime(this.newSession.start_time)
        const endTime = this.formatTime(this.newSession.end_time)
        const newSlotTime = `${startTime}-${endTime}`

        this.availableSlots.push({
          time: newSlotTime,
          available: true,
          booked: false,
          unavailable: false
        })

        await this.loadCalendarData()
      } catch (e: any) {
        this.$toast.add({ severity: 'error', summary: 'Ошибка', detail: e.message || 'Не удалось создать урок' })
      }
    },
    formatTime(date: Date) {
      const hours = date.getHours().toString().padStart(2, '0')
      const minutes = date.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    }
  },
  async mounted() {
    if (!this.isTeacher) {
      await this.loadTeachers()
    }
    if (this.isTeacher || this.selectedTeacher) {
      await this.loadCalendarData()
    }
  }
})
</script>

<style scoped>
.calendar-page {
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

.teacher-selection {
  background: var(--surface-card);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.teacher-selector {
  display: flex;
  flex-direction: column;
  max-width: 400px;
  margin: 0 auto;
}

.teacher-selector label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-color);
  text-align: center;
}

.teacher-dropdown {
  width: 100%;
}

.calendar-container {
  background: var(--surface-card);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.calendar-navigation {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;
}

.month-selector {
  text-align: center;
}

.month-selector h2 {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: var(--text-color);
}

.month-subtitle {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.calendar-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
}

.day-header {
  text-align: center;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  padding: 0.5rem;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
}

.calendar-day {
  aspect-ratio: 1;
  border-radius: 12px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px solid transparent;
}

.calendar-day:hover:not(.other-month) {
  background: var(--surface-hover);
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.calendar-day.other-month {
  opacity: 0.3;
  cursor: default;
}

.calendar-day.today {
  background: var(--primary-color);
  color: white;
  font-weight: 600;
}

.calendar-day.today:hover {
  background: var(--primary-600);
}

.calendar-day.weekend:not(.today) {
  color: var(--red-500);
}

.calendar-day.non-work-day:not(.today) {
  background: var(--surface-section);
  opacity: 0.6;
}

.calendar-day.non-work-cursor-day:not(.today) {
  cursor: not-allowed;
}

.calendar-day.selected:not(.today) {
  background: var(--primary-100);
  border-color: var(--primary-color);
  color: var(--primary-color);
  font-weight: 600;
}

.day-number {
  font-size: 1rem;
  font-weight: 500;
}

.day-events {
  position: absolute;
  bottom: 0.25rem;
  display: flex;
  gap: 0.125rem;
}

.event-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--primary-color);
}

.calendar-day.today .event-dot {
  background: white;
}

.day-settings-section {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: var(--surface-section);
  border-radius: 12px;
  border: 1px solid var(--surface-border);
}

.activation-toggle {
  margin-bottom: 1.5rem;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-weight: 500;
}

.toggle-label input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
  accent-color: var(--primary-color);
}

.toggle-text {
  color: var(--text-color);
}

.time-settings {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--surface-border);
}

.time-settings h5 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1rem;
}

.time-range {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.time-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time-input-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color-secondary);
}

.time-input {
  padding: 0.5rem;
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  background: var(--surface-card);
  color: var(--text-color);
  font-size: 0.875rem;
}

.time-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-100);
}

.booked-slots {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--surface-border);
}

.booked-slots h5 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1rem;
}

.booked-slots-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.booked-slot {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--red-50);
  border: 1px solid var(--red-200);
  border-radius: 8px;
  color: var(--red-700);
  font-size: 0.875rem;
}

.remove-slot-btn {
  background: none;
  border: none;
  color: var(--red-600);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.remove-slot-btn:hover {
  background: var(--red-100);
}

.settings-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--surface-border);
}

.save-btn {
  flex: 1;
}

.cancel-btn {
  flex: 1;
}

.selected-day-info {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid var(--surface-border);
}

.selected-day-header {
  margin-bottom: 1.5rem;
}

.selected-day-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.day-description {
  font-size: 1rem;
  color: var(--primary-color);
  font-weight: 500;
  margin: 0;
}

.time-slots-section h4 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.time-slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.time-slot {
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid var(--surface-border);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.time-slot.available {
  border-color: var(--green-300);
  background: var(--green-50);
}

.time-slot.available:hover {
  border-color: var(--green-400);
  background: var(--green-100);
  transform: translateY(-2px);
}

.time-slot.booked {
  border-color: var(--red-300);
  background: var(--red-50);
  cursor: not-allowed;
  opacity: 0.7;
}

.time-slot.unavailable {
  border-color: var(--surface-border);
  background: var(--surface-section);
  cursor: not-allowed;
  opacity: 0.5;
}

.slot-time {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.slot-status {
  font-size: 0.875rem;
}

.status-available {
  color: var(--green-600);
}

.status-booked {
  color: var(--red-600);
}

.status-unavailable {
  color: var(--text-color-secondary);
}

.slot-status i {
  margin-right: 0.25rem;
}

.select-day-message {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.select-teacher-message {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.message-content {
  text-align: center;
  padding: 3rem;
}

.message-icon {
  font-size: 4rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.message-content h3 {
  margin: 0 0 1rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.message-content p {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: 1.125rem;
}

.booking-details {
  padding: 1rem 0;
}

.booking-info p {
  margin: 0.5rem 0;
  color: var(--text-color);
}

.booking-info strong {
  color: var(--text-color);
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--surface-border);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.create-lesson-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 1.25rem;
}

.field{
  margin-bottom: 1rem;
}

.action-button {
  width: 100%;
  justify-content: flex-start;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-indicator p {
  color: var(--text-color-secondary);
  margin: 0;
}

@media (max-width: 768px) {
  .main-content {
    padding: 0.5rem;
  }

  .page-header h1 {
    font-size: 1.75rem;
  }

  .calendar-container {
    padding: 1rem;
  }

  .month-selector h2 {
    font-size: 1.5rem;
  }

  .calendar-day {
    padding: 0.25rem;
  }

  .day-number {
    font-size: 0.875rem;
  }

  .time-slots-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>
