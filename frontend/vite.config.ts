import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Integração com o backend real (JWT). Para dev com backend local,
      // troque o target por 'http://127.0.0.1:8000'.
      '/api': {
        target: 'https://qualytask.duckdns.org',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
