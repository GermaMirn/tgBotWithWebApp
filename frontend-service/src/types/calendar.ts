import type { LessonShort, LessonSessionResponse } from "@/types/lessons";
import type { Teacher } from "@/types/teacher";

// Схемы для TeacherDaySchedule
export interface TeacherDayScheduleBase {
  teacher_telegram_id: number
  date: string
  start_time: string
  end_time: string
  is_active: boolean
  booked_slots: string[]
}

export interface TeacherDayScheduleCreate extends TeacherDayScheduleBase {}

export interface TeacherDayScheduleUpdate {
  start_time?: string
  end_time?: string
  is_active?: boolean
  booked_slots?: string[]
}

export interface TeacherDayScheduleResponse extends TeacherDayScheduleBase {
  id: number
  created_at: string
  updated_at?: string
}

// Схемы для TeacherSchedule (недельное расписание)
export interface TeacherScheduleBase {
  teacher_telegram_id: number
  day_of_week: number
  start_time: string
  end_time: string
  is_available: boolean
}

export interface TeacherScheduleCreate extends TeacherScheduleBase {}

export interface TeacherScheduleUpdate {
  start_time?: string
  end_time?: string
  is_available?: boolean
}

export interface TeacherScheduleResponse extends TeacherScheduleBase {
  id: number
  created_at: string
  updated_at?: string
}

// Схемы для календаря
export interface CalendarDayResponse {
  date: string
  is_active: boolean
  start_time: string
  end_time: string
  lessons: LessonSessionResponse[]
}

export interface CalendarResponse {
  teacher_telegram_id: number
  days: CalendarDayResponse[]
}

// Схемы для временных слотов
export interface TimeSlotResponse {
  time: string
  status: "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED"
  teacher: Teacher
  lesson?: LessonShort
}

// ===== Teacher Special Day =====
export interface TeacherSpecialDayBase {
  teacher_telegram_id: number
  date: string
  start_time: string
  end_time: string
}

export interface TeacherSpecialDayCreate extends TeacherSpecialDayBase {}

export interface TeacherSpecialDayUpdate extends TeacherSpecialDayBase {}

export interface TeacherSpecialDayResponse extends TeacherSpecialDayBase {
  id: number
}

// ===== Teacher Unavailable Periods =====
export interface TeacherUnavailableResponse {
  start_time: string
  end_time: string
  reason?: string | null
}
