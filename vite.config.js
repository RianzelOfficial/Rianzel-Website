import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  root: './frontend',
  plugins: [vue()],
  base: '/',
  server: {
    port: 5173,
    host: 'localhost',
    strictPort: true,
    force: true,
    watch: {
      usePolling: true
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true
  }
})
