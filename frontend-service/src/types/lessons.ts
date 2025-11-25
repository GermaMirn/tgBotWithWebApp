export type DayOfWeek = 0|1|2|3|4|5|6

export interface TeacherWeekScheduleItem {
  day_of_week: DayOfWeek
  is_available: boolean
  start_time: string | null // "09:00"
  end_time: string | null   // "18:00"
}

export interface BookedByShort {
  type: string
  id: string
  name:  string | null
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
  start_time: string
  end_time: string
  status: 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  lesson?: {
    id: number
    title: string
    description?: string
    lesson_type: 'INDIVIDUAL' | 'GROUP' | 'TRIAL'
    language: string
    level: string
    teacher_telegram_id: number
  }
}

export interface CreateSessionPayload {
  lesson_id: number
  start_time: string
  end_time: string
  status?: 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
}

export interface CreateDaySchedulePayload {
  is_active: boolean
  start_time: string | null
  end_time: string | null
}

export interface LessonShort {
  id: number
  title: string
  description?: string
  lesson_type: "INDIVIDUAL" | "GROUP" | "TRIAL"
  language: string
  booked: boolean
  booked_by: BookedByShort
  level: string
  teacher_telegram_id: number
}

export interface LessonSessionResponse {
  id: number
  lesson_id: number
  start_time: string
  end_time: string
  status: 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED'
  booked: boolean
  booked_by: BookedByShort
  lesson?: LessonShort
}

export interface EnrollmentCreate {
  lesson_id: number
  student_id?: string
  group_id?: number
}

export interface LessonParticipant {
  id: number
  lesson_id: number
  student_id?: string
  group_id?: number
  is_confirmed: boolean
  confirmation_date?: string
}

export interface FreeSlotsResponse {
  teacher_telegram_id: number
  date: string
  slots: string[]
}
