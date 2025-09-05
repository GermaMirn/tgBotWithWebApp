import { api } from "./axios";

export interface User {
  id: string;
  telegram_id: number;
  username?: string;
  full_name: string;
  phone_number?: string;
  email?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
  role: string;
  timezone: string;
}

export interface RoleSwitchLink {
  id: string;
  token: string;
  target_role: string;
  target_user_id?: string; // UUID как строка
  target_user_name?: string;
  created_at: string;
  expires_at: string;
  is_used: boolean;
  is_active: boolean;
  used_at?: string;
}

export interface CreateLinkRequest {
  target_role: string;
  target_user_id?: string;
  target_user_name?: string;
  expires_in_hours: number;
}

export interface SwitchUserRoleRequest {
  target_role: string;
  target_user_id: string;
  target_user_name: string;
}

export const adminApi = {
  // Получение пользователей с фильтрацией по роли
  async getUsers(role?: string): Promise<User[]> {
    const params = role ? { role } : {};
    const response = await api.get("/auth/users", { params });
    return response.data;
  },

  // Создание ссылки для переключения роли
  async createRoleSwitchLink(data: CreateLinkRequest): Promise<RoleSwitchLink> {
    const response = await api.post("/role/admin/role-switch-links", data);
    return response.data;
  },

  // Получение всех ссылок
  async getRoleSwitchLinks(): Promise<RoleSwitchLink[]> {
    const response = await api.get("/role/admin/role-switch-links");
    return response.data;
  },

  // Удаление ссылки
  async deleteRoleSwitchLink(linkId: string): Promise<void> {
    await api.delete(`/role/admin/role-switch-links/${linkId}`);
  },

  // Деактивация ссылки
  async deactivateRoleSwitchLink(linkId: string): Promise<RoleSwitchLink> {
    const response = await api.patch(`/role/admin/role-switch-links/${linkId}/deactivate`);
    return response.data;
  },

  // Прямое переключение роли пользователя (для студентов)
  async switchUserRole(data: SwitchUserRoleRequest): Promise<any> {
    const response = await api.post("/role/admin/switch-user-role", data);
    return response.data;
  }
};
