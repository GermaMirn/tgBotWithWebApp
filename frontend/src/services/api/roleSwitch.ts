import { api } from "./axios";
import { RoleSwitchValidateResponse, RoleSwitchResponse } from "@/types/roleSwitch";

export const roleSwitchApi = {
  // Валидация токена ссылки для переключения роли
  async validateToken(token: string): Promise<RoleSwitchValidateResponse> {
    const response = await api.get(`/role/role-switch/validate/${token}`);
    return response.data;
  },

  // Переключение роли по токену
  async switchRole(token: string): Promise<RoleSwitchResponse> {
    const response = await api.post('/role/role-switch', { token });
    return response.data;
  }
};
