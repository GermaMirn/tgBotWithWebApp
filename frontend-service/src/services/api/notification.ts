import { api } from "./axios";
import { NotificationSettings, NotificationSettingsStatus } from "../../types/notification";

export const notificationsApi = {
  // Получить настройки уведомлений (с автоматическим созданием если нет)
  async getSettings(userId: string): Promise<NotificationSettings> {
    const response = await api.get(`/notification/users/${userId}/settings`);
    return response.data;
  },

  // Обновить настройки уведомлений
  async updateSettings(userId: string, settings: Partial<NotificationSettings>): Promise<NotificationSettings> {
    const response = await api.patch(`/notification/users/${userId}/settings`, settings);
    return response.data;
  },

  // Включить/выключить уведомления
  async toggleNotifications(userId: string, enabled: boolean): Promise<NotificationSettings> {
    return this.updateSettings(userId, { telegram_enabled: enabled });
  },

  // Установить chat_id
  async setChatId(userId: string, chatId: number): Promise<NotificationSettings> {
    const response = await api.post(`/notification/users/${userId}/chat-id`, { chat_id: chatId });
    return response.data;
  },

  // Проверить статус уведомлений
  async getNotificationStatus(userId: string): Promise<NotificationSettingsStatus> {
    const response = await api.get(`/notification/users/${userId}/settings/status`);
    return response.data;
  }
};
