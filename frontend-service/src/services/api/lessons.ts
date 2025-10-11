import { api } from './axios'
import {
  LessonSession,
  CreateSessionPayload,
  LessonParticipant,
  EnrollmentCreate,
  FreeSlotsResponse
} from '@/types/lessons'

export const lessonsApi = {
  // ====== СЕССИИ ======

  // Получить сессии преподавателя за период
  async getTeacherSessions(
    teacherTelegramId: number,
    start: string,
    end: string
  ): Promise<LessonSession[]> {
    const { data } = await api.get('/lessons/sessions/by-teacher', {
      params: { teacher_telegram_id: teacherTelegramId, start, end }
    })
    return data
  },

  // Создать сессию (требует lesson_id)
  async createSession(payload: CreateSessionPayload): Promise<LessonSession> {
    const { data } = await api.post('/lessons/sessions', payload)
    return data
  },

  // Получить конкретную сессию
  async getSession(sessionId: number): Promise<LessonSession> {
    const { data } = await api.get(`/lessons/sessions/${sessionId}`)
    return data
  },

  // Обновить сессию
  async updateSession(sessionId: number, payload: Partial<LessonSession>): Promise<LessonSession> {
    const { data } = await api.put(`/lessons/sessions/${sessionId}`, payload)
    return data
  },

  // Удалить сессию
  async deleteSession(sessionId: number): Promise<void> {
    await api.delete(`/lessons/sessions/${sessionId}`)
  },

  // ====== УРОКИ ======

  // Создать урок и сессию вместе
  async createFullLesson(payload: {
    lesson: {
      title: string
      lesson_type: "INDIVIDUAL" | "GROUP" | "TRIAL"
      language: string
      level: string
      description?: string
      teacher_telegram_id: number
    },
    session: {
      start_time: string
      end_time: string
    },
    teacher_telegram_id: number
  }): Promise<LessonSession> {
    const { data } = await api.post('/lessons/create-full-lesson', payload)
    return data
  },

  // Удалить урок вместе со всеми его сессиями
  async deleteFullLesson(lessonId: number): Promise<void> {
    await api.delete(`/lessons/delete-full-lesson/${lessonId}`)
  },

  // Получить урок
  async getLesson(lessonId: number) {
    const { data } = await api.get(`/lessons/${lessonId}`)
    return data
  },

  // Получить уроки с фильтрами
  async getLessons(filters?: {
    language?: string
    level?: string
    teacher_id?: number
  }) {
    const { data } = await api.get('/lessons', { params: filters })
    return data
  },

  // ====== ЗАПИСИ СТУДЕНТОВ ======

  // Записать студента/группу на занятие
  async enroll(payload: EnrollmentCreate): Promise<LessonParticipant> {
    const { data } = await api.post('/lessons/enroll', payload)
    return data
  },

  // Получить участников занятия
  async getLessonParticipants(lessonId: number): Promise<LessonParticipant[]> {
    const { data } = await api.get(`/lessons/${lessonId}/participants`)
    return data
  },

  // Отписать студента от занятия
  async removeStudent(lessonId: number, studentId: string): Promise<void> {
    await api.delete(`/lessons/${lessonId}/participants/${studentId}`)
  },

  // Отписать группу от занятия
  async removeGroup(lessonId: number, groupId: number): Promise<void> {
    await api.delete(`/lessons/${lessonId}/participants/group/${groupId}`)
  },

  // Подтвердить/отменить подтверждение участника
  async setParticipantConfirmation(participantId: number, confirmed: boolean): Promise<LessonParticipant> {
    const { data } = await api.put(`/lessons/participants/${participantId}?confirmed=${confirmed}`)
    return data
  },

  // ====== ПОСЕЩАЕМОСТЬ ======

  // Добавить запись о посещении
  async addAttendance(payload: {
    lesson_id: number
    student_id: string
    status: string
    join_time?: string
    leave_time?: string
  }) {
    const { data } = await api.post('/lessons/attendance', payload)
    return data
  },

  // Получить посещаемость урока
  async getLessonAttendance(lessonId: number) {
    const { data } = await api.get(`/lessons/attendance/${lessonId}`)
    return data
  },

  // ====== СВОБОДНЫЕ СЛОТЫ ======

  // Получить свободные слоты преподавателя
  async getFreeSlots(teacherTelegramId: number, date: string): Promise<FreeSlotsResponse> {
    const { data } = await api.get('/lessons/free-slots', {
      params: { teacher_telegram_id: teacherTelegramId, the_date: date }
    })
    return data
  }
}
