export interface RoleSwitchValidateResponse {
  valid: boolean;
  link?: {
    id: string;
    target_role: string;
    target_user_name?: string;
    expires_at: string;
  };
  message?: string;
}

export interface RoleSwitchRequest {
  token: string;
}

export interface RoleSwitchResponse {
  success: boolean;
  message: string;
  access_token?: string;
  user?: {
    id: string;
    telegram_id: number;
    full_name: string;
    role: string;
  };
}
