import { api } from "./axios";
import { Group, GroupCreate, GroupUpdate } from "@/types/groups";

export const groupsApi = {
  // Получить все группы
  async getGroups(): Promise<Group[]> {
    const response = await api.get("/groups");
    return response.data;
  },

  // Получить группы текущего учителя
  async getTeacherGroups(): Promise<Group[]> {
    const response = await api.get("/groups/teacher");
    return response.data;
  },

  // Получить группы текущего студента
  async getStudentGroups(): Promise<Group[]> {
    const response = await api.get("/groups/student");
    return response.data;
  },

  // Получить группу по ID
  async getGroupById(id: number): Promise<Group> {
    const response = await api.get(`/groups/${id}`);
    return response.data;
  },

  // Создать новую группу
  async createGroup(data: GroupCreate): Promise<Group> {
    const response = await api.post("/groups", data);
    return response.data;
  },

  // Обновить группу по ID
  async updateGroup(id: number, data: Partial<GroupUpdate>): Promise<Group> {
    const response = await api.patch(`/groups/${id}`, data);
    return response.data;
  },

  // Удалить группу по ID
  async deleteGroup(id: number): Promise<void> {
    await api.delete(`/groups/${id}`);
  },

  // Удалить участника из группы (только админ/владелец)
  async removeMember(groupId: number, studentTelegramId: number) {
    const response = await api.delete(`/groups/${groupId}/members/${studentTelegramId}`);
    return response.data; // ожидаем { message: "Member removed" }
  },

  // Выйти из группы (текущий пользователь)
  async leaveGroup(groupId: number) {
    const response = await api.delete(`/groups/${groupId}/leave`);
    return response.data; // ожидаем { message: "You have left the group" }
  },

  // Получить данные текущей группы (если есть такая концепция)
  async getCurrentGroup(): Promise<Group> {
    const response = await api.get("/groups/me");
    return response.data;
  },

  // Обновить данные текущей группы (если актуально)
  async updateCurrentGroup(data: Partial<GroupUpdate>): Promise<Group> {
    const response = await api.put("/groups/me", data);
    return response.data;
  },

  // Создать приглашение в группу
  async createInvitation(data: { group_id: number, expires_in_hours?: number, message?: string }) {
    const response = await api.post("/groups/invitations", data);
    return response.data; // ожидаем { invite_token: "..."} или { invite_token: "...", ... }
  },

  // Получить приглашение по токену
  async getInvitation(token: string) {
    const response = await api.get(`/groups/invitations/${token}/get`);
    return response.data;
  },

  // Принять приглашение (текущий пользователь)
  async acceptInvitation(token: string) {
    const response = await api.post(`/groups/invitations/${token}/accept`);
    return response.data;
  },

  // Получить список приглашений для студента
  async getStudentInvitations(studentTelegramId: number) {
    const response = await api.get(`/groups/invitations/student/${studentTelegramId}`);
    return response.data;
  },

  // Удалить приглашение
  async deleteInvitation(invitationId: number) {
    const response = await api.delete(`/groups/invitations/${invitationId}`);
    return response.data;
  },
};
