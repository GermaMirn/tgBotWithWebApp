export type DayOfWeek = 0|1|2|3|4|5|6

export interface TeacherWeekScheduleItem {
  day_of_week: DayOfWeek
  is_available: boolean
  start_time: string | null // "09:00"
  end_time: string | null   // "18:00"
}

export interface TeacherDaySchedule {
  teacher_telegram_id: number
  date: string            // "YYYY-MM-DD"
  is_active: boolean
  start_time: string | null
  end_time: string | null
}

export interface CalendarDay {
  date: string            // "YYYY-MM-DD"
  is_active: boolean
  start_time: string | null
  end_time: string | null
}

export interface CalendarResponse {
  teacher_telegram_id: number
  days: CalendarDay[]
}

export type LessonStatus = 'scheduled'|'in_progress'|'completed'|'cancelled'

export interface Lesson {
  id: number
  title: string
  description?: string | null
  lesson_type: 'individual' | 'group' | 'trial'
  language: string
  level: string
  teacher_telegram_id: number
}

export interface LessonSession {
  id: number
  lesson_id: number
  start_time: string      // ISO
  end_time: string        // ISO
  status: LessonStatus
  // Расширим для фронта:
  is_booked?: boolean
  booked_by_me?: boolean
}

export interface CreateSessionPayload {
  lesson_id: number
  start_time: string      // ISO
  end_time: string        // ISO
}

export interface CreateDaySchedulePayload {
  is_active: boolean
  start_time: string | null
  end_time: string | null
}
