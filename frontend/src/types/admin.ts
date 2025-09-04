export interface User {
  id: string
  full_name: string
  telegram_id: number
  username?: string
  email?: string
  phone_number?: string
  role?: string
}

export interface StudentWithUserData extends User {
  level?: string
  preferred_languages?: string[]
  study_goals?: string | null
}

export interface RoleSwitchLink {
  id: string
  token: string
  target_role: 'teacher' | 'student' | 'admin'
  target_user_id: string
  target_user_name: string
  is_active: boolean
  is_used: boolean
  created_at: string
  expires_at: string
  used_at?: string
}
