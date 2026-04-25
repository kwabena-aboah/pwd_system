<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Audit Log</h1>
      <p class="page-subtitle">System-wide activity trail</p>
    </div>
    <div class="filter-bar mb-3">
      <input v-model="search" type="text" placeholder="Search by user, model or object..." class="form-control" style="max-width:320px" @input="debouncedFetch">
      <select v-model="actionFilter" class="form-select" style="width:140px" @change="fetch">
        <option value="">All Actions</option>
        <option value="0">Create</option>
        <option value="1">Update</option>
        <option value="2">Delete</option>
      </select>
    </div>
    <div class="table-card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead><tr><th>Timestamp</th><th>User</th><th>Action</th><th>Model</th><th>Object</th><th>Changes</th></tr></thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id">
              <td><small>{{ new Date(log.timestamp).toLocaleString() }}</small></td>
              <td><strong>{{ log.actor }}</strong><br><small class="text-muted">{{ log.actor_email }}</small></td>
              <td><span class="badge" :class="actionBadge(log.action)">{{ log.action }}</span></td>
              <td><code>{{ log.model }}</code></td>
              <td>{{ log.object }}</td>
              <td>
                <button class="btn btn-xs btn-outline-secondary" @click="showChanges(log)" v-if="log.changes && Object.keys(log.changes).length">
                  <i class="bi bi-list-ul"></i> {{ Object.keys(log.changes).length }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
const logs = ref([])
const search = ref('')
const actionFilter = ref('')
let timer = null
function debouncedFetch() { clearTimeout(timer); timer = setTimeout(fetch, 400) }
async function fetch() {
  const p = { search: search.value }
  if (actionFilter.value) p.action = actionFilter.value
  const { data } = await api.get('/audit-logs/', { params: p })
  logs.value = data.results ?? data
}
function actionBadge(a) {
  return { 'Create': 'bg-success-subtle text-success', 'Update': 'bg-warning-subtle text-warning', 'Delete': 'bg-danger-subtle text-danger' }[a] || 'bg-secondary-subtle text-secondary'
}
function showChanges(log) { alert(JSON.stringify(log.changes, null, 2)) }
onMounted(fetch)
</script>
<style scoped>
.page-header { margin-bottom: 24px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.page-subtitle { color: var(--text-secondary); font-size: 0.9rem; }
.filter-bar { display: flex; gap: 10px; flex-wrap: wrap; }
.table-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.table thead th { background: var(--surface-secondary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); padding: 12px 16px; }
.table tbody td { padding: 10px 16px; font-size: 0.8rem; }
</style>
