export interface Student {
  id: string;
  telegram_id: number;
  level: string;
  preferred_languages: string[];
  study_goals?: string;
  created_at: string;
  updated_at?: string;
}

export interface StudentCreate {
  telegram_id: number;
  level?: string;
  preferred_languages?: string[];
  study_goals?: string;
}
