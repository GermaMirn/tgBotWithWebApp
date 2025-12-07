/**
 * Мок для Telegram WebApp в режиме разработки
 * Позволяет тестировать приложение в браузере без Telegram Mini App
 */

export interface MockTelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  allows_write_to_pm?: boolean;
}

export interface MockTelegramWebApp {
  initData: string;
  initDataUnsafe: {
    user?: MockTelegramUser;
    query_id?: string;
    auth_date?: string;
    hash: string;
  };
  version: string;
  platform: string;
  expand(): void;
  close(): void;
  enableClosingConfirmation(): void;
  ready(): void;
  showAlert(message: string): void;
  showConfirm(message: string, callback?: (confirmed: boolean) => void): void;
  showPopup(params: any, callback?: (id: string) => void): void;
  showScanQrPopup(params: any, callback?: (data: string) => void): void;
  closeScanQrPopup(): void;
  readTextFromClipboard(callback?: (text: string) => void): void;
  requestWriteAccess(callback?: (granted: boolean) => void): void;
  requestContact(callback?: (granted: boolean) => void): void;
  openLink(url: string, options?: { try_instant_view?: boolean }): void;
  openTelegramLink(url: string): void;
  openInvoice(url: string, callback?: (status: string) => void): void;
  sendData(data: string): void;
  ready(): void;
  expand(): void;
  close(): void;
  enableClosingConfirmation(): void;
  disableClosingConfirmation(): void;
  onEvent(eventType: string, eventHandler: () => void): void;
  offEvent(eventType: string, eventHandler: () => void): void;
  sendEvent(eventType: string, eventData?: any): void;
  hapticFeedback(
    impactStyle: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft',
    impactType?: 'impact' | 'notification' | 'selection'
  ): void;
  cloudStorage: {
    setItem(key: string, value: string, callback?: (error: Error | null, success: boolean) => void): void;
    getItem(key: string, callback: (error: Error | null, value: string | null) => void): void;
    getItems(keys: string[], callback: (error: Error | null, values: Record<string, string>) => void): void;
    removeItem(key: string, callback?: (error: Error | null, success: boolean) => void): void;
    removeItems(keys: string[], callback?: (error: Error | null, success: boolean) => void): void;
    getKeys(callback: (error: Error | null, keys: string[]) => void): void;
  };
  themeParams: {
    bg_color?: string;
    text_color?: string;
    hint_color?: string;
    link_color?: string;
    button_color?: string;
    button_text_color?: string;
    secondary_bg_color?: string;
  };
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  headerColor: string;
  backgroundColor: string;
  BackButton: {
    isVisible: boolean;
    onClick(callback: () => void): void;
    offClick(callback: () => void): void;
    show(): void;
    hide(): void;
  };
  MainButton: {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isActive: boolean;
    isProgressVisible: boolean;
    setText(text: string): void;
    onClick(callback: () => void): void;
    offClick(callback: () => void): void;
    show(): void;
    hide(): void;
    enable(): void;
    disable(): void;
    showProgress(leaveActive?: boolean): void;
    hideProgress(): void;
    setParams(params: {
      text?: string;
      color?: string;
      text_color?: string;
      is_active?: boolean;
      is_visible?: boolean;
    }): void;
  };
  HapticFeedback: {
    impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void;
    notificationOccurred(type: 'error' | 'success' | 'warning'): void;
    selectionChanged(): void;
  };
}

/**
 * Создает мок Telegram WebApp с тестовыми данными пользователя
 */
export function createTelegramMock(): MockTelegramWebApp {
  const mockUser: MockTelegramUser = {
    id: 123456789,
    first_name: 'Test',
    last_name: 'User',
    username: 'testuser',
    language_code: 'ru',
    is_premium: false,
    allows_write_to_pm: true,
  };

  const mockWebApp: MockTelegramWebApp = {
    initData: 'mock_init_data',
    initDataUnsafe: {
      user: mockUser,
      query_id: 'mock_query_id',
      auth_date: Math.floor(Date.now() / 1000).toString(),
      hash: 'mock_hash',
    },
    version: '6.0',
    platform: 'web',
    isExpanded: true,
    viewportHeight: window.innerHeight,
    viewportStableHeight: window.innerHeight,
    headerColor: '#ffffff',
    backgroundColor: '#ffffff',
    themeParams: {
      bg_color: '#ffffff',
      text_color: '#000000',
      hint_color: '#999999',
      link_color: '#2481cc',
      button_color: '#2481cc',
      button_text_color: '#ffffff',
    },
    expand() {
      console.log('[Telegram Mock] expand() called');
      this.isExpanded = true;
    },
    close() {
      console.log('[Telegram Mock] close() called');
    },
    enableClosingConfirmation() {
      console.log('[Telegram Mock] enableClosingConfirmation() called');
    },
    disableClosingConfirmation() {
      console.log('[Telegram Mock] disableClosingConfirmation() called');
    },
    ready() {
      console.log('[Telegram Mock] ready() called');
    },
    showAlert(message: string) {
      console.log('[Telegram Mock] showAlert:', message);
      alert(message);
    },
    showConfirm(message: string, callback?: (confirmed: boolean) => void) {
      console.log('[Telegram Mock] showConfirm:', message);
      const confirmed = confirm(message);
      if (callback) callback(confirmed);
    },
    showPopup(params: any, callback?: (id: string) => void) {
      console.log('[Telegram Mock] showPopup:', params);
      if (callback) callback('mock_popup_id');
    },
    showScanQrPopup(params: any, callback?: (data: string) => void) {
      console.log('[Telegram Mock] showScanQrPopup:', params);
      if (callback) callback('mock_qr_data');
    },
    closeScanQrPopup() {
      console.log('[Telegram Mock] closeScanQrPopup() called');
    },
    readTextFromClipboard(callback?: (text: string) => void) {
      console.log('[Telegram Mock] readTextFromClipboard() called');
      navigator.clipboard.readText().then((text) => {
        if (callback) callback(text);
      });
    },
    requestWriteAccess(callback?: (granted: boolean) => void) {
      console.log('[Telegram Mock] requestWriteAccess() called');
      if (callback) callback(true);
    },
    requestContact(callback?: (granted: boolean) => void) {
      console.log('[Telegram Mock] requestContact() called');
      if (callback) callback(true);
    },
    openLink(url: string, options?: { try_instant_view?: boolean }) {
      console.log('[Telegram Mock] openLink:', url, options);
      window.open(url, '_blank');
    },
    openTelegramLink(url: string) {
      console.log('[Telegram Mock] openTelegramLink:', url);
      window.open(url, '_blank');
    },
    openInvoice(url: string, callback?: (status: string) => void) {
      console.log('[Telegram Mock] openInvoice:', url);
      if (callback) callback('paid');
    },
    sendData(data: string) {
      console.log('[Telegram Mock] sendData:', data);
    },
    onEvent(eventType: string, eventHandler: () => void) {
      console.log('[Telegram Mock] onEvent:', eventType);
    },
    offEvent(eventType: string, eventHandler: () => void) {
      console.log('[Telegram Mock] offEvent:', eventType);
    },
    sendEvent(eventType: string, eventData?: any) {
      console.log('[Telegram Mock] sendEvent:', eventType, eventData);
    },
    hapticFeedback(
      impactStyle: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft',
      impactType?: 'impact' | 'notification' | 'selection'
    ) {
      console.log('[Telegram Mock] hapticFeedback:', impactStyle, impactType);
    },
    cloudStorage: {
      setItem(key: string, value: string, callback?: (error: Error | null, success: boolean) => void) {
        localStorage.setItem(`tg_cloud_${key}`, value);
        if (callback) callback(null, true);
      },
      getItem(key: string, callback: (error: Error | null, value: string | null) => void) {
        const value = localStorage.getItem(`tg_cloud_${key}`);
        callback(null, value);
      },
      getItems(keys: string[], callback: (error: Error | null, values: Record<string, string>) => void) {
        const values: Record<string, string> = {};
        keys.forEach((key) => {
          const value = localStorage.getItem(`tg_cloud_${key}`);
          if (value) values[key] = value;
        });
        callback(null, values);
      },
      removeItem(key: string, callback?: (error: Error | null, success: boolean) => void) {
        localStorage.removeItem(`tg_cloud_${key}`);
        if (callback) callback(null, true);
      },
      removeItems(keys: string[], callback?: (error: Error | null, success: boolean) => void) {
        keys.forEach((key) => localStorage.removeItem(`tg_cloud_${key}`));
        if (callback) callback(null, true);
      },
      getKeys(callback: (error: Error | null, keys: string[]) => void) {
        const keys: string[] = [];
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key?.startsWith('tg_cloud_')) {
            keys.push(key.replace('tg_cloud_', ''));
          }
        }
        callback(null, keys);
      },
    },
    BackButton: {
      isVisible: false,
      onClick(callback: () => void) {
        console.log('[Telegram Mock] BackButton.onClick');
      },
      offClick(callback: () => void) {
        console.log('[Telegram Mock] BackButton.offClick');
      },
      show() {
        console.log('[Telegram Mock] BackButton.show()');
        this.isVisible = true;
      },
      hide() {
        console.log('[Telegram Mock] BackButton.hide()');
        this.isVisible = false;
      },
    },
    MainButton: {
      text: 'Continue',
      color: '#2481cc',
      textColor: '#ffffff',
      isVisible: false,
      isActive: true,
      isProgressVisible: false,
      setText(text: string) {
        this.text = text;
        console.log('[Telegram Mock] MainButton.setText:', text);
      },
      onClick(callback: () => void) {
        console.log('[Telegram Mock] MainButton.onClick');
      },
      offClick(callback: () => void) {
        console.log('[Telegram Mock] MainButton.offClick');
      },
      show() {
        this.isVisible = true;
        console.log('[Telegram Mock] MainButton.show()');
      },
      hide() {
        this.isVisible = false;
        console.log('[Telegram Mock] MainButton.hide()');
      },
      enable() {
        this.isActive = true;
        console.log('[Telegram Mock] MainButton.enable()');
      },
      disable() {
        this.isActive = false;
        console.log('[Telegram Mock] MainButton.disable()');
      },
      showProgress(leaveActive?: boolean) {
        this.isProgressVisible = true;
        console.log('[Telegram Mock] MainButton.showProgress()');
      },
      hideProgress() {
        this.isProgressVisible = false;
        console.log('[Telegram Mock] MainButton.hideProgress()');
      },
      setParams(params: {
        text?: string;
        color?: string;
        text_color?: string;
        is_active?: boolean;
        is_visible?: boolean;
      }) {
        if (params.text !== undefined) this.text = params.text;
        if (params.color !== undefined) this.color = params.color;
        if (params.text_color !== undefined) this.textColor = params.text_color;
        if (params.is_active !== undefined) this.isActive = params.is_active;
        if (params.is_visible !== undefined) this.isVisible = params.is_visible;
        console.log('[Telegram Mock] MainButton.setParams:', params);
      },
    },
    HapticFeedback: {
      impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') {
        console.log('[Telegram Mock] HapticFeedback.impactOccurred:', style);
      },
      notificationOccurred(type: 'error' | 'success' | 'warning') {
        console.log('[Telegram Mock] HapticFeedback.notificationOccurred:', type);
      },
      selectionChanged() {
        console.log('[Telegram Mock] HapticFeedback.selectionChanged()');
      },
    },
  };

  return mockWebApp;
}

/**
 * Инициализирует мок Telegram WebApp в window.Telegram
 */
export function initTelegramMock(): void {
  if (typeof window === 'undefined') return;

  const mockWebApp = createTelegramMock();

  // Устанавливаем мок в window.Telegram
  window.Telegram = {
    WebApp: mockWebApp as any,
  };

  console.log('[Telegram Mock] Initialized mock Telegram WebApp');
  console.log('[Telegram Mock] User:', mockWebApp.initDataUnsafe.user);
}


