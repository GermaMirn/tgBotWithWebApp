import { api } from "./axios";
import { Student, StudentCreate} from "@/types/students"

export const studentsApi = {
  // Получение всех студентов
  async getStudents(): Promise<Student[]> {
    const response = await api.get("/students");
    return response.data;
  },

  // Получение студента по ID
  async getStudentById(id: string): Promise<Student> {
    const response = await api.get(`/students/${id}`);
    return response.data;
  },

  // Получение студента по Telegram ID
  async getStudentByTelegramId(telegramId: number): Promise<Student> {
    const response = await api.get(`/students/by-telegram/${telegramId}`);
    return response.data;
  },

  // Создание студента
  async createStudent(data: StudentCreate): Promise<Student> {
    const response = await api.post("/students", data);
    return response.data;
  },

  // Обновление студента
  async updateStudent(id: string, data: Partial<StudentCreate>): Promise<Student> {
    const response = await api.put(`/students/${id}`, data);
    return response.data;
  },

  // Удаление студента
  async deleteStudent(id: string): Promise<void> {
    await api.delete(`/students/${id}`);
  },

  // Получение данных текущего студента
  async getCurrentStudent(): Promise<Student> {
    const response = await api.get("/students/me");
    return response.data;
  },

  // Обновление данных текущего студента
  async updateCurrentStudent(data: Partial<StudentCreate>): Promise<Student> {
    const response = await api.put("/students/me", data);
    return response.data;
  }
};
