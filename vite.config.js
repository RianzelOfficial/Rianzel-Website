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
  preview: {
    host: '0.0.0.0',
    port: 4173,
    allowedHosts: [
      'rianzel-website.onrender.com',  // Render default domain
      'www.nazzelandrian.site'          // Your custom domain
    ]
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
