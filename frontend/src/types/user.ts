export interface UserProfile {
  id: string
  telegram_id: string
  full_name: string
  username: string
  phone_number?: string
  email?: string
  role: string
}

export interface StudentProfile {
  id: string
  user_id: string
  level?: string
  preferred_languages?: string[]
  study_goals?: string
}

export interface TeacherProfile {
  id: string
  user_id: string
  bio?: string
  specialization?: string
  experience_years?: number
  education?: string
  certificates?: string[] | string
  hourly_rate?: number
}