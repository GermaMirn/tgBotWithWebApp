export interface Teacher {
  id: string;
  telegram_id: number;
  bio?: string;
  specialization: string;
  experience_years: number;
  education?: string;
  certificates?: string[];
  hourly_rate: number;
  created_at: string;
  updated_at?: string;
  full_name?: string;
}

export interface TeacherCreate {
  telegram_id: number;
  bio?: string;
  specialization: string;
  experience_years: number;
  education?: string;
  certificates?: string[];
  hourly_rate: number;
}
