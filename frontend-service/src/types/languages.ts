export interface StudioLanguage {
  id: number;
  name: string;
  code: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface StudioLanguageCreate {
  name: string;
  code: string;
  is_active?: boolean;
}

export interface StudioLanguageUpdate {
  name?: string;
  code?: string;
  is_active?: boolean;
}

