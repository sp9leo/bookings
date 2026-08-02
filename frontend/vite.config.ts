import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'fs'

function getBenchPath() {
  let currentDir = process.cwd()
  let prevDir = null
  while (currentDir !== prevDir) {
    if (fs.existsSync(resolve(currentDir, 'Procfile'))) {
      return currentDir
    }
    prevDir = currentDir
    currentDir = resolve(currentDir, '..')
  }
  return null
}

function detectProxyTarget() {
  if (process.env.VITE_BACKEND_URL) return process.env.VITE_BACKEND_URL
  const benchPath = getBenchPath()
  if (benchPath) return `http://localhost:8000`
  return 'http://192.168.1.111:8000'
}

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: detectProxyTarget(),
        changeOrigin: true
      }
    }
  }
})
