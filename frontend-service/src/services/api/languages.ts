import { api } from "./axios";
import { StudioLanguage, StudioLanguageCreate, StudioLanguageUpdate } from "@/types/languages";

export const languagesApi = {
  // Получить все языки
  async getLanguages(activeOnly: boolean = false): Promise<StudioLanguage[]> {
    const response = await api.get("/languages", {
      params: { active_only: activeOnly }
    });
    return response.data;
  },

  // Получить язык по ID
  async getLanguageById(id: number): Promise<StudioLanguage> {
    const response = await api.get(`/languages/${id}`);
    return response.data;
  },

  // Создать новый язык (только для админов)
  async createLanguage(data: StudioLanguageCreate): Promise<StudioLanguage> {
    const response = await api.post("/languages", data);
    return response.data;
  },

  // Обновить язык (только для админов)
  async updateLanguage(id: number, data: StudioLanguageUpdate): Promise<StudioLanguage> {
    const response = await api.put(`/languages/${id}`, data);
    return response.data;
  },

  // Удалить язык (только для админов)
  async deleteLanguage(id: number): Promise<void> {
    await api.delete(`/languages/${id}`);
  },
};

