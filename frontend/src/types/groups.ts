import { Teacher } from "./teacher";
import { StudentWithUserData } from "./admin";

export interface Group {
  id: number;
  name: string;
  description?: string;
  group_type?: "REGULAR" | "INTENSIVE" | "CONVERSATION" | "GRAMMAR";
  max_students?: number;
  language: string;
  level: string;
  start_date?: string; // ISO дата
  end_date?: string;   // ISO дата
  status?: "ACTIVE" | "INACTIVE" | "FULL" | "WAITLIST";
  is_active?: boolean;
  teacher_telegram_id?: number;
  current_students?: number;

  teacher: Teacher;
  students?: StudentWithUserData[];
}

export interface GroupCreate {
  name: string;
  description?: string;
  group_type?: "REGULAR" | "INTENSIVE" | "CONVERSATION" | "GRAMMAR";
  max_students?: number;
  language: string;
  level: string;
  status?: "ACTIVE" | "INACTIVE" | "FULL" | "WAITLIST";
  start_date?: string;
  end_date?: string;
}

export interface GroupUpdate {
  name?: string;
  description?: string;
  group_type?: "REGULAR" | "INTENSIVE" | "CONVERSATION" | "GRAMMAR";
  max_students?: number;
  language: string;
  level: string;
  status?: "ACTIVE" | "INACTIVE" | "FULL" | "WAITLIST";
  start_date?: string;
  end_date?: string;
}
