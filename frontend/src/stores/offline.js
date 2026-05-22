// stores/offline.js — Offline-first queue using IndexedDB
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { openDB } from 'idb'
import api from '@/services/api'

const DB_NAME = 'pwdms_offline'
const DB_VERSION = 1
const STORE = 'pending_requests'

async function getDB() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: 'id', autoIncrement: true })
      }
    }
  })
}

export const useOfflineStore = defineStore('offline', () => {
  const isOnline = ref(navigator.onLine)
  const pendingCount = ref(0)
  const isSyncing = ref(false)

  // Track online status
  window.addEventListener('online', () => { isOnline.value = true; sync() })
  window.addEventListener('offline', () => { isOnline.value = false })

  async function queueRequest(method, url, data, description = '') {
    const db = await getDB()
    await db.add(STORE, {
      method, url, data, description,
      timestamp: new Date().toISOString(),
      retries: 0,
    })
    await updateCount()
  }

  async function updateCount() {
    const db = await getDB()
    pendingCount.value = await db.count(STORE)
  }

  async function sync() {
    if (!isOnline.value || isSyncing.value) return
    isSyncing.value = true
    const db = await getDB()
    const all = await db.getAll(STORE)

    for (const req of all) {
      try {
        await api({ method: req.method, url: req.url, data: req.data })
        await db.delete(STORE, req.id)
      } catch (err) {
        if (err.response) {
          // Server error — remove bad request
          await db.delete(STORE, req.id)
        }
        // Network error — keep in queue
      }
    }

    await updateCount()
    isSyncing.value = false
  }

  // Initialise count on load
  updateCount()

  return { isOnline, pendingCount, isSyncing, queueRequest, sync, updateCount }
})
