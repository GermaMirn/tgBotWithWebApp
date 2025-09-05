import { api } from "./axios";
import { Teacher, TeacherCreate } from "@/types/teacher";

export const teachersApi = {
  // Получение всех учителей
  async getTeachers(): Promise<Teacher[]> {
    const response = await api.get("/teachers/");
    return response.data;
  },

  // Получение учителя по ID
  async getTeacherById(id: string): Promise<Teacher> {
    const response = await api.get(`/teachers/${id}`);
    return response.data;
  },

  // Получение учителя по Telegram ID
  async getTeacherByTelegramId(telegramId: number): Promise<Teacher> {
    const response = await api.get(`/teachers/by-telegram/${telegramId}`);
    return response.data;
  },

  // Создание учителя (с авторизацией)
  async createTeacher(data: TeacherCreate): Promise<Teacher> {
    const response = await api.post("/teachers", data);
    return response.data;
  },

  // Создание учителя без авторизации (для переключения ролей)
  async createTeacherWithoutAuth(data: TeacherCreate): Promise<Teacher> {
    const response = await api.post("/teachers/create-without-auth", data);
    return response.data;
  },

  // Обновление учителя
  async updateTeacher(id: string, data: Partial<TeacherCreate>): Promise<Teacher> {
    const response = await api.put(`/teachers/${id}`, data);
    return response.data;
  },

  // Удаление учителя
  async deleteTeacher(id: string): Promise<void> {
    await api.delete(`/teachers/${id}`);
  },

  // Получение данных текущего учителя
  async getCurrentTeacher(): Promise<Teacher> {
    const response = await api.get("/teachers/me");
    return response.data;
  },

  // Обновление данных текущего учителя
  async updateCurrentTeacher(data: Partial<TeacherCreate>): Promise<Teacher> {
    const response = await api.put("/teachers/me", data);
    return response.data;
  }
};
