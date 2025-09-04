import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', {
  state: () => ({
    isGlobalLoading: false as boolean,
    loadingMessage: 'Загрузка...' as string
  }),
  actions: {
    showLoading(message?: string) {
      this.loadingMessage = message || 'Загрузка...'
      this.isGlobalLoading = true
    },
    hideLoading() {
      this.isGlobalLoading = false
      this.loadingMessage = 'Загрузка...'
    }
  }
})
