import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/newsapi': {
        target: 'https://newsapi.org',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/newsapi/, '')
      },
      '/cheapshark': {
        target: 'https://www.cheapshark.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/cheapshark/, '')
      },
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})