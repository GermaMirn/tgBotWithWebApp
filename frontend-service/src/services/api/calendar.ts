import { api } from './axios'
import type {
  CalendarResponse,
  TeacherDayScheduleCreate,
  TeacherDayScheduleUpdate,
  TeacherDayScheduleResponse,
  TimeSlotResponse,
  TeacherScheduleCreate,
  TeacherScheduleUpdate,
  TeacherScheduleResponse,
  TeacherSpecialDayCreate,
  TeacherSpecialDayResponse,
  TeacherUnavailableResponse,
  TeacherScheduleFullResponse,
  TeacherSpecialDayUpdate
} from '@/types/calendar'

export const calendarApi = {
  // ===== Teacher Day Schedule (разовые рабочие дни) =====
  async createTeacherDaySchedule(schedule: TeacherDayScheduleCreate): Promise<TeacherDayScheduleResponse> {
    const response = await api.post('calendary/teacher-schedule', schedule)
    return response.data
  },

  async getTeacherDaySchedule(teacherTelegramId: number, scheduleDate: string): Promise<TeacherDayScheduleResponse> {
    const response = await api.get(`calendary/teacher-schedule/${teacherTelegramId}/${scheduleDate}`)
    return response.data
  },

  async updateTeacherDaySchedule(
    teacherTelegramId: number,
    scheduleDate: string,
    scheduleUpdate: TeacherDayScheduleUpdate
  ): Promise<TeacherDayScheduleResponse> {
    const response = await api.put(`calendary/teacher-schedule/${teacherTelegramId}/${scheduleDate}`, scheduleUpdate)
    return response.data
  },

  async getTimeSlots(teacherTelegramId: number, scheduleDate: string): Promise<TimeSlotResponse[]> {
    const response = await api.get(`calendary/time-slots/${teacherTelegramId}/${scheduleDate}`)
    return response.data
  },

  // ===== Teacher Weekly Schedule =====
  async createTeacherSchedule(schedule: TeacherScheduleCreate): Promise<TeacherScheduleResponse> {
    const response = await api.post('calendary/teacher-schedule', schedule)
    return response.data
  },

  async getTeacherSchedules(teacherTelegramId: number): Promise<TeacherScheduleResponse[]> {
    const response = await api.get(`calendary/teacher-schedule/${teacherTelegramId}`)
    return response.data
  },

  async getTeacherScheduleByDay(teacherTelegramId: number, dayOfWeek: number): Promise<TeacherScheduleResponse> {
    const response = await api.get(`calendary/teacher-schedule/${teacherTelegramId}/${dayOfWeek}`)
    return response.data
  },

  async updateTeacherSchedule(
    teacherTelegramId: number,
    dayOfWeek: number,
    scheduleUpdate: TeacherScheduleUpdate
  ): Promise<TeacherScheduleResponse> {
    const response = await api.put(`calendary/teacher-schedule/${teacherTelegramId}/${dayOfWeek}`, scheduleUpdate)
    return response.data
  },

  // ===== Teacher Special Day =====
  async createTeacherSpecialDay(specialDay: TeacherSpecialDayCreate): Promise<TeacherSpecialDayResponse> {
    const response = await api.post('calendary/teacher-special-day', specialDay)
    return response.data
  },

  async getTeacherSpecialDays(teacherTelegramId: number, start: string, end: string): Promise<TeacherSpecialDayResponse[]> {
    const response = await api.get(`calendary/teacher-special-day/${teacherTelegramId}`, {
      params: { start, end }
    })
    return response.data
  },

  async updateTeacherSpecialDay(
    specialDayId: number,
    specialDayUpdate: Partial<TeacherSpecialDayUpdate>
  ): Promise<TeacherSpecialDayResponse> {
    const response = await api.put(`calendary/teacher-special-day/${specialDayId}`, specialDayUpdate)
    return response.data
  },

  async deleteTeacherSpecialDay(specialDayId: number): Promise<{ status: string }> {
    const response = await api.delete(`calendary/teacher-special-day/${specialDayId}`)
    return response.data
  },

  // ===== Full Schedule =====
  async getTeacherFullSchedule(
    teacherTelegramId: number,
    start: string,
    end: string
  ): Promise<TeacherScheduleFullResponse> {
    const response = await api.post(`calendary/teacher-schedule/${teacherTelegramId}/full`, {start, end})
    return response.data
  },

  // ===== Calendar =====
  async getCalendar(teacherTelegramId: number, startDate: string, endDate: string): Promise<CalendarResponse> {
    const response = await api.get(`calendary/calendar/${teacherTelegramId}`, {
      params: { start_date: startDate, end_date: endDate }
    })
    return response.data
  }
}
