import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

const isDev = process.env.NODE_ENV === 'development'

// Use env variable for backend
const API_BASE = process.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [
    vue(),

    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: false, // 🔥 disable PWA in dev (avoids cache madness)
      },

      includeAssets: ['favicon.ico', 'logo.png', 'offline.html'],

      manifest: {
        name: 'PWD Management System',
        short_name: 'PWDMS',
        description: 'Persons With Disability Management System',
        theme_color: '#1a56db',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait-primary',
        start_url: '/',
        icons: [
          { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable',
          },
        ],
      },

      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],

        runtimeCaching: [
          // 🔥 DO NOT cache auth endpoints
          {
            urlPattern: /\/api\/auth\//,
            handler: 'NetworkOnly',
          },

          // API caching (safe endpoints only)
          {
            urlPattern: /\/api\/(?!auth).*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 200,
                maxAgeSeconds: 24 * 60 * 60,
              },
              networkTimeoutSeconds: 5,
            },
          },

          // Media caching
          {
            urlPattern: /\/media\//,
            handler: 'CacheFirst',
            options: {
              cacheName: 'media-cache',
              expiration: {
                maxEntries: 300,
                maxAgeSeconds: 30 * 24 * 60 * 60,
              },
            },
          },
        ],
      },
    }),
  ],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  // DEV ONLY proxy (safe)
  server: isDev
    ? {
        proxy: {
          '/_backend/api': {
            target: API_BASE,
            changeOrigin: true,
            secure: false,
          },
          '/_backend/media': {
            target: API_BASE,
            changeOrigin: true,
            secure: false,
          },
        },
      }
    : undefined,
})