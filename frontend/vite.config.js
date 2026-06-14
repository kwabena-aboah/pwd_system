import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  // In production (Render static site) the backend URL comes from VITE_API_BASE_URL.
  // In development the Vite dev-server proxy forwards /api to localhost:8000.
  const apiTarget = env.VITE_API_BASE_URL
    ? `https://${env.VITE_API_BASE_URL}`
    : 'http://localhost:8000'

  return {
    plugins: [
      vue(),
      VitePWA({
        registerType: 'autoUpdate',
        includeAssets: ['favicon.ico', 'logo.png'],
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
            { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' }
          ]
        },
        workbox: {
          globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
          runtimeCaching: [
            {
              urlPattern: /\/api\/pwds\//,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'pwds-cache',
                expiration: { maxEntries: 500, maxAgeSeconds: 7 * 24 * 60 * 60 },
                networkTimeoutSeconds: 5,
              }
            },
            {
              urlPattern: /\/api\//,
              handler: 'NetworkFirst',
              options: {
                cacheName: 'api-cache',
                expiration: { maxEntries: 200, maxAgeSeconds: 24 * 60 * 60 },
                networkTimeoutSeconds: 5,
              }
            },
            {
              urlPattern: /\/media\//,
              handler: 'CacheFirst',
              options: {
                cacheName: 'media-cache',
                expiration: { maxEntries: 300, maxAgeSeconds: 30 * 24 * 60 * 60 },
              }
            }
          ]
        }
      })
    ],
    resolve: {
      alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) }
    },
    // Only used during local development
    server: {
      proxy: {
        '/api': { target: 'http://localhost:8000', changeOrigin: true },
        '/media': { target: 'http://localhost:8000', changeOrigin: true },
        '/ws': { target: 'ws://localhost:8000', ws: true, changeOrigin: true },
      }
    }
  }
})
