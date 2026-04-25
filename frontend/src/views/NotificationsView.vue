<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Notifications</h1>
      <button class="btn btn-outline-secondary" @click="markAllRead"><i class="bi bi-check2-all me-1"></i>Mark All Read</button>
    </div>
    <div class="notif-list">
      <div v-for="n in notifications" :key="n.id" class="notif-item" :class="{ unread: !n.is_read }">
        <div class="notif-icon" :class="'type-' + n.notification_type">
          <i class="bi" :class="typeIcon(n.notification_type)"></i>
        </div>
        <div class="notif-body">
          <strong>{{ n.title }}</strong>
          <p>{{ n.message }}</p>
          <small class="text-muted">{{ new Date(n.created_at).toLocaleString() }}</small>
        </div>
        <button v-if="!n.is_read" class="btn btn-sm btn-outline-primary" @click="markRead(n.id)">Mark read</button>
      </div>
      <div v-if="!notifications.length" class="empty-state">
        <i class="bi bi-bell"></i><p>No notifications</p>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
const notifications = ref([])
const typeIcon = t => ({ info: 'bi-info-circle', success: 'bi-check-circle', warning: 'bi-exclamation-triangle', danger: 'bi-x-circle', new_pwd: 'bi-person-plus', benefit: 'bi-gift', complaint: 'bi-chat-left-text', audit: 'bi-shield-check', system: 'bi-gear' }[t] || 'bi-bell')
async function fetch() {
  const { data } = await api.get('/notifications/')
  notifications.value = data.results ?? data
}
async function markRead(id) { await api.post(`/notifications/${id}/mark-read/`); fetch() }
async function markAllRead() { await api.post('/notifications/mark-all-read/'); fetch() }
onMounted(fetch)
</script>
<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.notif-list { display: flex; flex-direction: column; gap: 8px; }
.notif-item { background: white; border-radius: var(--radius); padding: 16px 20px; box-shadow: var(--shadow); display: flex; align-items: flex-start; gap: 14px; transition: box-shadow 0.2s; border-left: 4px solid transparent; }
.notif-item.unread { border-left-color: var(--bs-primary, #1a56db); background: #f0f4ff; }
.notif-icon { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; flex-shrink: 0; background: var(--surface-secondary); color: var(--bs-primary, #1a56db); }
.notif-body { flex: 1; }
.notif-body strong { display: block; font-size: 0.9rem; margin-bottom: 4px; }
.notif-body p { font-size: 0.825rem; color: var(--text-secondary); margin-bottom: 4px; }
.empty-state { text-align: center; padding: 60px; color: var(--text-secondary); }
.empty-state i { font-size: 3rem; display: block; margin-bottom: 12px; }
</style>
