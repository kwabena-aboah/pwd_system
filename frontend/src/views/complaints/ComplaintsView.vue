<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Complaints & Grievances</h1>
      <button class="btn btn-primary" @click="openForm" v-if="auth.canEdit">
        <i class="bi bi-plus-lg me-1"></i>Log Complaint
      </button>
    </div>

    <!-- Modal -->
    <div class="modal-overlay" v-if="showForm" @click.self="closeForm">
      <div class="modal-box">
        <h5 class="mb-3">Log Complaint</h5>

        <div class="row g-3">
          <!-- PWD -->
          <div class="col-6">
            <label class="form-label">PWD Name *</label>
            <select v-model="newComplaint.pwd" class="form-select">
              <option value="">Select PWD</option>
              <option v-for="p in pwds" :key="p.id" :value="p.id">
                {{ p.first_name }} {{ p.last_name }}
              </option>
            </select>
          </div>

          <!-- Category -->
          <div class="col-6">
            <label class="form-label">Category *</label>
            <select v-model="newComplaint.category" class="form-select">
              <option value="">Select Category</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
          </div>

          <div class="col-6">
            <label class="form-label">Title *</label>
            <input v-model="newComplaint.title" class="form-control">
          </div>

          <div class="col-6">
            <label class="form-label">Description *</label>
            <textarea v-model="newComplaint.description" class="form-control"></textarea>
          </div>

          <div class="col-6">
            <label class="form-label">Source *</label>
            <select v-model="newComplaint.source" class="form-select">
              <option value="pwd">PWD Self</option>
              <option value="caregiver">Caregiver</option>
              <option value="community">Community</option>
              <option value="partner">Partner</option>
              <option value="anonymous">Anonymous</option>
            </select>
          </div>

          <div class="col-6">
            <label class="form-label">Complainant Name</label>
            <input v-model="newComplaint.complainant_name" class="form-control">
          </div>

          <div class="col-6">
            <label class="form-label">Complainant Phone</label>
            <input v-model="newComplaint.complainant_phone" class="form-control">
          </div>

          <div class="col-6">
            <label class="form-label">Priority *</label>
            <select v-model="newComplaint.priority" class="form-select">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div class="col-6">
            <label class="form-label">Status *</label>
            <select v-model="newComplaint.status" class="form-select">
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
              <option value="escalated">Escalated</option>
            </select>
          </div>

          <div class="col-6">
            <label class="form-label">Resolution</label>
            <textarea v-model="newComplaint.resolution" class="form-control"></textarea>
          </div>

          <div class="col-6">
            <label class="form-label">Resolved At</label>
            <input v-model="newComplaint.resolved_at" type="datetime-local" class="form-control">
          </div>
        </div>

        <div class="d-flex justify-content-end gap-2 mt-3">
          <button class="btn btn-outline-secondary" @click="closeForm">Cancel</button>
          <button class="btn btn-primary" @click="createComplaint" :disabled="loading">
            {{ loading ? 'Saving...' : 'Create Complaint' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="row g-3 mb-4">
      <div class="col" v-for="s in stats" :key="s.label">
        <div class="stat-pill" :style="{ borderColor: s.color }">
          <span class="stat-count" :style="{ color: s.color }">{{ s.value }}</span>
          <span class="stat-label">{{ s.label }}</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-bar mb-3">
      <select v-model="statusFilter" class="form-select"  style="width: 160px;" @change="fetchComplaints">
        <option value="">All Status</option>
        <option value="open">Open</option>
        <option value="in_progress">In Progress</option>
        <option value="resolved">Resolved</option>
        <option value="closed">Closed</option>
      </select>

      <select v-model="priorityFilter" class="form-select" style="width: 160px;" @change="fetchComplaints">
        <option value="">All Priority</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="urgent">Urgent</option>
      </select>
    </div>

    <!-- List -->
    <div class="row g-3">
      <div class="col-12" v-for="c in complaints" :key="c.id">
        <div class="complaint-item" @click="router.push(`/complaints/${c.id}`)">
          <div>
            <strong>{{ c.title }}</strong>
            <div class="text-muted small">
              {{ c.complaint_number }} • {{ c.date_lodged }}
            </div>
          </div>
          <div>
            <span class="badge" :class="priorityBadge(c.priority)">{{ c.priority }}</span>
            <span class="badge ms-1" :class="statusBadge(c.status)">{{ c.status }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const auth = useAuthStore()

const complaints = ref([])
const pwds = ref([])
const categories = ref([])

const showForm = ref(false)
const loading = ref(false)

const statusFilter = ref('')
const priorityFilter = ref('')

const summary = ref({ total: 0, open: 0, in_progress: 0, resolved: 0 })

const stats = computed(() => [
  { label: 'Total', value: summary.value.total, color: '#1a56db' },
  { label: 'Open', value: summary.value.open, color: '#ef4444' },
  { label: 'In Progress', value: summary.value.in_progress, color: '#f59e0b' },
  { label: 'Resolved', value: summary.value.resolved, color: '#10b981' },
])

const defaultForm = () => ({
  pwd: '',
  category: '',
  title: '',
  description: '',
  source: 'pwd',
  complainant_name: '',
  complainant_phone: '',
  priority: 'medium',
  status: 'open',
  resolution: '',
  resolved_at: ''
})

const newComplaint = ref(defaultForm())

// Fetch all data
const fetchAll = async () => {
  try {
    const [cr, sr, pr, cat] = await Promise.all([
      api.get('/complaints/'),
      api.get('/complaints/statistics/'),
      api.get('/pwds/'),
      api.get('/complaint-categories/')
    ])

    complaints.value = cr.data.results ?? cr.data
    summary.value = sr.data
    pwds.value = pr.data.results ?? pr.data
    categories.value = cat.data.results ?? cat.data
  } catch (err) {
    console.error(err)
  }
}

const fetchComplaints = async () => {
  const params = {}
  if (statusFilter.value) params.status = statusFilter.value
  if (priorityFilter.value) params.priority = priorityFilter.value

  const { data } = await api.get('/complaints/', { params })
  complaints.value = data.results ?? data
}

// Modal control
const openForm = () => {
  newComplaint.value = defaultForm()
  showForm.value = true
}

const closeForm = () => {
  showForm.value = false
}

// Create complaint
const createComplaint = async () => {
  loading.value = true
  try {
    const { data } = await api.post('/complaints/', newComplaint.value)
    complaints.value.unshift(data)
    closeForm()
  } catch (err) {
    console.error(err.response?.data || err)
    alert('Failed to create complaint')
  } finally {
    loading.value = false
  }
}

// UI helpers
const priorityBadge = p => ({
  low: 'bg-secondary-subtle text-secondary',
  medium: 'bg-warning-subtle text-warning',
  high: 'bg-danger-subtle text-danger',
  urgent: 'bg-danger text-white'
}[p] || '')

const statusBadge = s => ({
  open: 'bg-danger-subtle text-danger',
  in_progress: 'bg-warning-subtle text-warning',
  resolved: 'bg-success-subtle text-success',
  closed: 'bg-secondary-subtle text-secondary'
}[s] || '')

onMounted(fetchAll)
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
