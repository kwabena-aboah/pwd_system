<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Complaints & Grievances</h1>
      <button class="btn btn-primary" @click="showForm = true" v-if="auth.canEdit">
        <i class="bi bi-plus-lg me-1"></i>Log Complaint
      </button>
    </div>

    <!-- Stats row -->
    <div class="row g-3 mb-4">
      <div class="col" v-for="s in stats" :key="s.label">
        <div class="stat-pill" :style="{ borderColor: s.color }">
          <span class="stat-count" :style="{ color: s.color }">{{ s.value }}</span>
          <span class="stat-label">{{ s.label }}</span>
        </div>
      </div>
    </div>

    <div class="filter-bar mb-3">
      <select v-model="statusFilter" class="form-select" style="width:160px" @change="fetchComplaints">
        <option value="">All Status</option>
        <option value="open">Open</option>
        <option value="in_progress">In Progress</option>
        <option value="resolved">Resolved</option>
        <option value="closed">Closed</option>
      </select>
      <select v-model="priorityFilter" class="form-select" style="width:140px" @change="fetchComplaints">
        <option value="">All Priority</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="urgent">Urgent</option>
      </select>
    </div>

    <div class="row g-3">
      <div class="col-12" v-for="c in complaints" :key="c.id">
        <div class="complaint-item" @click="router.push(`/complaints/${c.id}`)">
          <div class="complaint-left">
            <span class="priority-dot" :class="'priority-' + c.priority"></span>
            <div>
              <strong>{{ c.title }}</strong>
              <div class="text-muted small">{{ c.complaint_number }} • {{ c.date_lodged }} • {{ c.source }}</div>
              <div v-if="c.pwd_name" class="text-muted small"><i class="bi bi-person me-1"></i>{{ c.pwd_name }}</div>
            </div>
          </div>
          <div class="complaint-right">
            <span class="badge" :class="priorityBadge(c.priority)">{{ c.priority }}</span>
            <span class="badge ms-1" :class="statusBadge(c.status)">{{ c.status }}</span>
            <div v-if="c.assigned_to_name" class="text-muted small mt-1">
              <i class="bi bi-person-fill me-1"></i>{{ c.assigned_to_name }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
const router = useRouter()
const auth = useAuthStore()
const complaints = ref([])
const showForm = ref(false)
const statusFilter = ref('')
const priorityFilter = ref('')
const summary = ref({ total: 0, open: 0, in_progress: 0, resolved: 0 })
const stats = computed(() => [
  { label: 'Total', value: summary.value.total, color: '#1a56db' },
  { label: 'Open', value: summary.value.open, color: '#ef4444' },
  { label: 'In Progress', value: summary.value.in_progress, color: '#f59e0b' },
  { label: 'Resolved', value: summary.value.resolved, color: '#10b981' },
])
const priorityBadge = p => ({ low: 'bg-secondary-subtle text-secondary', medium: 'bg-warning-subtle text-warning', high: 'bg-danger-subtle text-danger', urgent: 'bg-danger text-white' }[p] || '')
const statusBadge = s => ({ open: 'bg-danger-subtle text-danger', in_progress: 'bg-warning-subtle text-warning', resolved: 'bg-success-subtle text-success', closed: 'bg-secondary-subtle text-secondary' }[s] || '')
async function fetchComplaints() {
  const p = {}
  if (statusFilter.value) p.status = statusFilter.value
  if (priorityFilter.value) p.priority = priorityFilter.value
  const [cr, sr] = await Promise.all([api.get('/complaints/', { params: p }), api.get('/complaints/statistics/')])
  complaints.value = cr.data.results ?? cr.data
  summary.value = sr.data
}
onMounted(fetchComplaints)
</script>
<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.filter-bar { display: flex; gap: 10px; flex-wrap: wrap; }
.stat-pill { background: white; border-radius: 12px; padding: 14px 20px; box-shadow: var(--shadow); border-left: 4px solid; display: flex; flex-direction: column; }
.stat-count { font-size: 1.8rem; font-weight: 800; line-height: 1; }
.stat-label { font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px; }
.complaint-item { background: white; border-radius: var(--radius); padding: 16px 20px; box-shadow: var(--shadow); cursor: pointer; display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; transition: box-shadow 0.2s; }
.complaint-item:hover { box-shadow: var(--shadow-md); }
.complaint-left { display: flex; gap: 12px; align-items: flex-start; flex: 1; }
.priority-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }
.priority-low { background: #94a3b8; }
.priority-medium { background: #f59e0b; }
.priority-high { background: #ef4444; }
.priority-urgent { background: #7f1d1d; }
.complaint-right { text-align: right; flex-shrink: 0; }
</style>
