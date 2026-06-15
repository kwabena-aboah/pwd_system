<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Complaints & Grievances</h1>

      <button
        v-if="auth.canEdit"
        class="btn btn-primary"
        @click="openForm"
      >
        <i class="bi bi-plus-lg me-1"></i>
        Log Complaint
      </button>
    </div>

    <!-- Stats -->
    <div class="row g-3 mb-4">
      <div
        class="col"
        v-for="s in stats"
        :key="s.label"
      >
        <div
          class="stat-pill"
          :style="{ borderColor: s.color }"
        >
          <span
            class="stat-count"
            :style="{ color: s.color }"
          >
            {{ s.value }}
          </span>

          <span class="stat-label">
            {{ s.label }}
          </span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-bar mb-3">
      <select
        v-model="statusFilter"
        class="form-select"
        style="width: 160px"
        @change="fetchComplaints"
      >
        <option value="">All Status</option>
        <option value="open">Open</option>
        <option value="in_progress">In Progress</option>
        <option value="resolved">Resolved</option>
        <option value="closed">Closed</option>
      </select>

      <select
        v-model="priorityFilter"
        class="form-select"
        style="width: 160px"
        @change="fetchComplaints"
      >
        <option value="">All Priority</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
        <option value="urgent">Urgent</option>
      </select>
    </div>

    <!-- Complaint List -->
    <div class="row g-3">
      <div
        class="col-12"
        v-for="c in complaints"
        :key="c.id"
      >
        <div
          class="complaint-item"
          @click="router.push(`/complaints/${c.id}`)"
        >
          <div class="complaint-left">
            <span
              class="priority-dot"
              :class="'priority-' + c.priority"
            ></span>

            <div>
              <strong>{{ c.title }}</strong>

              <div class="text-muted small">
                {{ c.complaint_number }}
                •
                {{ c.date_lodged }}
                •
                {{ c.source }}
              </div>

              <div
                v-if="c.pwd_name"
                class="text-muted small"
              >
                <i class="bi bi-person me-1"></i>
                {{ c.pwd_name }}
              </div>
            </div>
          </div>

          <div class="complaint-right">
            <span
              class="badge"
              :class="priorityBadge(c.priority)"
            >
              {{ c.priority }}
            </span>

            <span
              class="badge ms-1"
              :class="statusBadge(c.status)"
            >
              {{ c.status }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div
      v-if="showForm"
      class="modal fade show d-block"
      tabindex="-1"
    >
      <div
        class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable"
      >
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">
              Log Complaint
            </h5>

            <button
              type="button"
              class="btn-close"
              @click="closeForm"
            ></button>
          </div>

          <form @submit.prevent="saveComplaint">

            <div class="modal-body">

              <div class="row g-3">

                <!-- PWD -->
                <div class="col-md-6">
                  <label class="form-label">
                    PWD
                  </label>

                  <Multiselect
                    v-model="form.pwd"
                    :options="pwds"
                    label="display_name"
                    track-by="id"
                    :internal-search="false"
                    :loading="loadingPwds"
                    @search-change="searchPwds"
                  />
                </div>

                <!-- Category -->
                <div class="col-md-6">
                  <label class="form-label">
                    Category
                  </label>

                  <Multiselect
                    v-model="form.category"
                    :options="categories"
                    label="name"
                    track-by="id"
                    :internal-search="false"
                    :loading="loadingCat"
                    @search-change="loadCategories"
                  />
                </div>

                <!-- Title -->
                <div class="col-md-12">
                  <label class="form-label">
                    Title
                  </label>

                  <input
                    v-model="form.title"
                    class="form-control"
                    required
                  />
                </div>

                <!-- Description -->
                <div class="col-md-12">
                  <label class="form-label">
                    Description
                  </label>

                  <textarea
                    v-model="form.description"
                    rows="4"
                    class="form-control"
                  ></textarea>
                </div>

                <!-- Source -->
                <div class="col-md-6">
                  <label class="form-label">
                    Source
                  </label>

                  <Multiselect
                    v-model="form.source"
                    :options="sourceOptions"
                    label="label"
                    track-by="value"
                  />
                </div>

                <!-- Priority -->
                <div class="col-md-6">
                  <label class="form-label">
                    Priority
                  </label>

                  <Multiselect
                    v-model="form.priority"
                    :options="priorityOptions"
                    label="label"
                    track-by="value"
                  />
                </div>

                <!-- Complainant -->
                <div class="col-md-6">
                  <label class="form-label">
                    Complainant Name
                  </label>

                  <input
                    v-model="form.complainant_name"
                    class="form-control"
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label">
                    Complainant Phone
                  </label>

                  <input
                    v-model="form.complainant_phone"
                    class="form-control"
                  />
                </div>

                <!-- Status -->
                <div class="col-md-6">
                  <label class="form-label">
                    Status
                  </label>

                  <Multiselect
                    v-model="form.status"
                    :options="statusOptions"
                    label="label"
                    track-by="value"
                  />
                </div>

                <!-- Resolved At -->
                <div class="col-md-6">
                  <label class="form-label">
                    Resolved At
                  </label>

                  <input
                    v-model="form.resolved_at"
                    type="datetime-local"
                    class="form-control"
                  />
                </div>

                <!-- Resolution -->
                <div class="col-md-12">
                  <label class="form-label">
                    Resolution
                  </label>

                  <textarea
                    v-model="form.resolution"
                    rows="3"
                    class="form-control"
                  ></textarea>
                </div>

              </div>

            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                @click="closeForm"
              >
                Cancel
              </button>

              <button
                type="submit"
                class="btn btn-primary"
                :disabled="saving"
              >
                <span
                  v-if="saving"
                  class="spinner-border spinner-border-sm me-2"
                ></span>

                Save Complaint
              </button>
            </div>

          </form>

        </div>
      </div>
    </div>

    <div
      v-if="showForm"
      class="modal-backdrop fade show"
    ></div>

  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'

import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const auth = useAuthStore()

const complaints = ref([])
const showForm = ref(false)
const saving = ref(false)

const pwds = ref([])
const categories = ref([])

const statusFilter = ref('')
const priorityFilter = ref('')

const loadingPwds = ref(false)
const loadingCat = ref(false)

const summary = ref({
  total: 0,
  open: 0,
  in_progress: 0,
  resolved: 0
})

const sourceOptions = [
  { value: 'pwd', label: 'PWD Self' },
  { value: 'caregiver', label: 'Caregiver' },
  { value: 'community', label: 'Community' },
  { value: 'partner', label: 'Partner' },
  { value: 'anonymous', label: 'Anonymous' }
]

const priorityOptions = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' }
]

const statusOptions = [
  { value: 'open', label: 'Open' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'resolved', label: 'Resolved' },
  { value: 'closed', label: 'Closed' },
  { value: 'escalated', label: 'Escalated' }
]

const form = ref({
  pwd: null,
  category: null,
  title: '',
  description: '',
  source: null,
  complainant_name: '',
  complainant_phone: '',
  priority: null,
  status: null,
  resolution: '',
  resolved_at: ''
})

const stats = computed(() => [
  { label: 'Total', value: summary.value.total, color: '#1a56db' },
  { label: 'Open', value: summary.value.open, color: '#ef4444' },
  { label: 'In Progress', value: summary.value.in_progress, color: '#f59e0b' },
  { label: 'Resolved', value: summary.value.resolved, color: '#10b981' }
])

function openForm() {
  resetForm()
  showForm.value = true
}

function closeForm() {
  showForm.value = false
}

function resetForm() {
  form.value = {
    pwd: null,
    category: null,
    title: '',
    description: '',
    source: null,
    complainant_name: '',
    complainant_phone: '',
    priority: null,
    status: statusOptions[0],
    resolution: '',
    resolved_at: ''
  }
}

async function saveComplaint() {
  saving.value = true

  try {
    await api.post('/complaints/', {
      pwd: form.value.pwd?.id || null,
      category: form.value.category?.id || null,
      title: form.value.title,
      description: form.value.description,
      source: form.value.source?.value,
      complainant_name: form.value.complainant_name,
      complainant_phone: form.value.complainant_phone,
      priority: form.value.priority?.value,
      status: form.value.status?.value,
      resolution: form.value.resolution,
      resolved_at: form.value.resolved_at || null
    })

    closeForm()
    await fetchComplaints()

  } catch (error) {
    console.error(error)
    alert('Failed to save complaint')
  } finally {
    saving.value = false
  }
}

async function fetchComplaints() {
  const params = {}

  if (statusFilter.value) {
    params.status = statusFilter.value
  }

  if (priorityFilter.value) {
    params.priority = priorityFilter.value
  }

  const [cr, sr] = await Promise.all([
    api.get('/complaints/', { params }),
    api.get('/complaints/statistics/')
  ])

  complaints.value = cr.data.results ?? cr.data
  summary.value = sr.data
}

async function searchPwds(query) {
  if (!query || query.length < 2) return

  loadingPwds.value = true

  try {
    const { data } = await api.get('/pwds/', {
      params: {
        search: query
      }
    })

    pwds.value = (data.results ?? data).map(item => ({
      ...item,
      display_name:
        item.full_name ||
        item.name ||
        `${item.first_name || ''} ${item.last_name || ''}`.trim()
    }))
  } finally {
    loadingPwds.value = false
  }
}

async function loadCategories(query) {
  if (!query || query.length < 2) return

  loadingCat.value = true

  try {
    const { data } = await api.get('/complaint-categories/', {
      params: {
        search: query
      }
    })

    categories.value = (data.results ?? data).map(item => ({
      ...item,
      display_name:
        item.name ||
        `${item.name || ''} || ''}`.trim()
    }))
  } finally {
    loadingCat.value = false
  }
}


const priorityBadge = p =>
({
  low: 'bg-secondary-subtle text-secondary',
  medium: 'bg-warning-subtle text-warning',
  high: 'bg-danger-subtle text-danger',
  urgent: 'bg-danger text-white'
}[p] || '')

const statusBadge = s =>
({
  open: 'bg-danger-subtle text-danger',
  in_progress: 'bg-warning-subtle text-warning',
  resolved: 'bg-success-subtle text-success',
  closed: 'bg-secondary-subtle text-secondary',
  escalated: 'bg-dark text-white'
}[s] || '')

onMounted(async () => {
  await Promise.all([
    fetchComplaints(),
    loadPwds(),
    loadCategories()
  ])
})
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
.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal-card {
  background: #fff;
  width: 600px;
  max-width: 95%;
  border-radius: 10px;
  overflow: hidden;
}

.modal-header,
.modal-body {
  padding: 15px;
}
</style>
