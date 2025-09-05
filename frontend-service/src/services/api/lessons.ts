// src/services/api/lessons.ts
import { api } from './axios'
import { TeacherWeekScheduleItem, TeacherDaySchedule, CalendarResponse, LessonSession, CreateSessionPayload, CreateDaySchedulePayload } from '@/types/lessons'


// ====== API ======
export const lessonsApi = {
  // Сессии (уроки) на день
  async getSessionsByDay(teacherTelegramId: number, date: string): Promise<LessonSession[]> {
    const { data } = await api.get('/lessons/sessions', {
      params: { teacher_telegram_id: teacherTelegramId, date }
    })
    return data
  },

  // Создать сессию
  async createSession(payload: CreateSessionPayload): Promise<LessonSession> {
    const { data } = await api.post('/lessons/sessions', payload)
    return data
  },

  // Создать сессию и урок
  async createFullLesson(payload: {
    lesson: {
      title: string
      lesson_type: "individual" | "group" | "trial"
      language: string
      level: string
      description?: string
      teacher_telegram_id: number
    },
    session: {
      start_time: string  // ISO строка
      end_time: string    // ISO строка
    },
    teacher_telegram_id: number
  }): Promise<LessonSession> {
    const { data } = await api.post('/lessons/create-full-lesson', payload)
    return data
  },

  // Записаться на сессию
  async bookSession(sessionId: number): Promise<{ ok: true }> {
    const { data } = await api.post(`/lessons/sessions/${sessionId}/book`)
    return data
  },

  // Отменить запись
  async cancelBooking(sessionId: number): Promise<{ ok: true }> {
    const { data } = await api.delete(`/lessons/sessions/${sessionId}/book`)
    return data
  }
}
