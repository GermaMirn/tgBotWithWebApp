import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0',
    cors: true,
    strictPort: false,
    hmr: {
      port: 5173,
      host: 'localhost'
    },
    proxy: {},
    headers: {
      'Access-Control-Allow-Origin': '*'
    },
    allowedHosts: [
      'localhost',
      '.cloudpub.ru'
    ], // поменять на свои домены в проде
  }
})

