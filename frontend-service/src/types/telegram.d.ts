export {};

declare global {
  namespace TelegramWebApp {
    interface User {
      id: number;
      first_name?: string;
      last_name?: string;
      username?: string;
      language_code?: string;
      is_premium?: boolean;
      allows_write_to_pm?: boolean;
    }

    interface InitDataUnsafe {
      user?: User;
      query_id?: string;
      auth_date?: string;
      hash: string;
    }

    interface WebApp {
      initData: string;
      initDataUnsafe: InitDataUnsafe;
      version: string;
      platform: string;
      expand(): void;
      close(): void;
      enableClosingConfirmation(): void;
    }
  }

  interface Window {
    Telegram?: {
      WebApp: TelegramWebApp.WebApp;
    };
  }
}
