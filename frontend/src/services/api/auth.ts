import { api } from "./axios";

export interface TelegramUser {
  id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
}

export const authApi = {
  // Вход через Telegram Mini App
  async loginViaMiniApp(userData: TelegramUser): Promise<AuthResponse> {
    // Безопасно обрабатываем данные
    const loginData = {
      id: userData.id,
      username: userData.username && userData.username.trim() !== '' ? userData.username : '-',
      full_name: userData.full_name || [userData.first_name, userData.last_name].filter(Boolean).join(" ") || 'Пользователь'
    };

    const response = await api.post("/auth/miniapp", loginData);
    return response.data;
  },

  // Обычный вход
  async login(userData: TelegramUser): Promise<AuthResponse> {
    const loginData = {
      telegram_id: userData.id,
      username: userData.username && userData.username.trim() !== '' ? userData.username : '-',
      full_name: userData.full_name || [userData.first_name, userData.last_name].filter(Boolean).join(" ") || 'Пользователь'
    };

    const response = await api.post("/auth/login", loginData);
    return response.data;
  },

  // Получение данных текущего пользователя
  async getCurrentUser() {
    const response = await api.get("/auth/user");
    return response.data;
  },

  // Обновление профиля пользователя
  async updateProfile(profileData: { phone_number?: string; email?: string }) {
    const response = await api.put("/auth/update-profile", profileData);
    return response.data;
  }
};
