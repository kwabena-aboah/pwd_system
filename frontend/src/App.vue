<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useOfflineStore } from '@/stores/offline'

const offlineStore = useOfflineStore()

onMounted(() => {
  // Register service worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(() => {})
    })
  }
  // Initial sync attempt
  offlineStore.sync()
})
</script>
