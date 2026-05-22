<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Benefit Allocations</h1>
      <div class="d-flex gap-2 align-items-center">
        <span class="badge bg-warning-subtle text-warning fs-6">
          {{ pendingCount }} pending approval
        </span>
        <button class="btn btn-primary" v-if="auth.canEdit" @click="openForm">
          <i class="bi bi-plus-lg me-1"></i>New Allocation
        </button>
      </div>
    </div>

    <!-- Modal -->
    <div class="modal-overlay" v-if="showForm" @click.self="closeForm">
      <div class="modal-box">
        <h5 class="mb-3">Add New Allocation</h5>

        <div class="row g-3">
          <!-- PWD -->
          <div class="col-6">
            <label class="form-label">PWD Name *</label>
            <select v-model="newAllocation.pwd" class="form-select">
              <option value="">Select PWD</option>
              <option v-for="p in pwds" :key="p.id" :value="p.id">
                {{ p.first_name }} {{ p.last_name }}
              </option>
            </select>
          </div>

          <!-- Benefit -->
          <div class="col-6">
            <label class="form-label">Benefit *</label>
            <select v-model="newAllocation.benefit" class="form-select">
              <option value="">Select Benefit</option>
              <option v-for="b in benefits" :key="b.id" :value="b.id">
                {{ b.name }}
              </option>
            </select>
          </div>

          <div class="col-6">
            <label class="form-label">Allocation Date *</label>
            <input v-model="newAllocation.allocation_date" type="date" class="form-control">
          </div>

          <div class="col-6">
            <label class="form-label">Disbursement Date</label>
            <input v-model="newAllocation.disbursement_date" type="date" class="form-control">
          </div>

          <div class="col-6">
            <label class="form-label">Amount Disbursed</label>
            <input v-model="newAllocation.amount_disbursed" type="number" class="form-control">
          </div>

          <div class="col-6">
            <label class="form-label">In Kind Description</label>
            <textarea v-model="newAllocation.in_kind_description" class="form-control"></textarea>
          </div>

          <div class="col-6">
            <label class="form-label">Status *</label>
            <select v-model="newAllocation.status" class="form-select">
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="disbursed">Disbursed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <div class="col-6">
            <label class="form-label">Approval Date</label>
            <input v-model="newAllocation.approval_date" type="date" class="form-control">
          </div>

          <div class="col-6">
            <label class="form-label">Notes</label>
            <textarea v-model="newAllocation.notes" class="form-control"></textarea>
          </div>

          <!-- File Upload -->
          <div class="col-6">
            <label class="form-label">Receipt Document</label>
            <input type="file" class="form-control" @change="onFileChange">
          </div>
        </div>

        <div class="d-flex justify-content-end gap-2 mt-3">
          <button class="btn btn-outline-secondary" @click="closeForm">Cancel</button>
          <button class="btn btn-primary" @click="createAllocation" :disabled="loading">
            {{ loading ? 'Saving...' : 'Create Allocation' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Filter -->
    <div class="filter-bar mb-3">
      <select v-model="statusFilter" class="form-select" style="width:160px" @change="fetchAllocations">
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="disbursed">Disbursed</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>

    <!-- Table -->
    <div class="table-card">
      <table class="table table-hover">
        <thead>
          <tr>
            <th>PWD</th><th>Benefit</th><th>Partner</th>
            <th>Amount</th><th>Date</th><th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in allocations" :key="a.id">
            <td><strong>{{ a.pwd_name }}</strong></td>
            <td>{{ a.benefit_name }}</td>
            <td>{{ a.partner_name }}</td>
            <td>{{ a.amount_disbursed ? 'GHS ' + a.amount_disbursed : a.in_kind_description || '—' }}</td>
            <td>{{ a.allocation_date }}</td>
            <td><span class="badge" :class="badge(a.status)">{{ a.status }}</span></td>
            <td>
              <button v-if="a.status === 'pending' && auth.canEdit" class="btn btn-sm btn-outline-success" @click="approve(a.id)">
                ✔
              </button>
              <button v-if="a.status === 'approved' && auth.canEdit" class="btn btn-sm btn-outline-primary" @click="disburse(a.id)">
                💰
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()

const allocations = ref([])
const pwds = ref([])
const benefits = ref([])

const showForm = ref(false)
const loading = ref(false)
const statusFilter = ref('')
const receiptFile = ref(null)

const defaultForm = () => ({
  pwd: '',
  benefit: '',
  allocation_date: '',
  disbursement_date: '',
  amount_disbursed: '',
  in_kind_description: '',
  status: 'pending',
  approval_date: '',
  notes: ''
})

const newAllocation = ref(defaultForm())

const pendingCount = computed(() =>
  allocations.value.filter(a => a.status === 'pending').length
)

const badge = s => ({
  disbursed: 'bg-success-subtle text-success',
  approved: 'bg-info-subtle text-info',
  pending: 'bg-warning-subtle text-warning',
  rejected: 'bg-danger-subtle text-danger'
}[s] || 'bg-secondary-subtle text-secondary')

// Fetch all required data
const fetchAll = async () => {
  try {
    const [a, p, b] = await Promise.all([
      api.get('/benefit-allocations/'),
      api.get('/pwds/'),
      api.get('/benefits/')
    ])

    allocations.value = a.data.results ?? a.data
    pwds.value = p.data.results ?? p.data
    benefits.value = b.data.results ?? b.data
  } catch (err) {
    console.error(err)
  }
}

// Filter fetch
const fetchAllocations = async () => {
  const params = statusFilter.value ? { status: statusFilter.value } : {}
  const { data } = await api.get('/benefit-allocations/', { params })
  allocations.value = data.results ?? data
}

// File handler
const onFileChange = (e) => {
  receiptFile.value = e.target.files[0]
}

// Open / Close
const openForm = () => {
  newAllocation.value = defaultForm()
  receiptFile.value = null
  showForm.value = true
}

const closeForm = () => {
  showForm.value = false
}

// Create allocation
const createAllocation = async () => {
  loading.value = true
  try {
    const formData = new FormData()

    Object.entries(newAllocation.value).forEach(([key, value]) => {
      if (value !== '' && value !== null) formData.append(key, value)
    })

    if (receiptFile.value) {
      formData.append('receipt', receiptFile.value)
    }

    const { data } = await api.post('/benefit-allocations/', formData)

    allocations.value.unshift(data)
    closeForm()
  } catch (err) {
    console.error(err.response?.data || err)
    alert('Failed to create allocation')
  } finally {
    loading.value = false
  }
}

// Actions
const approve = async (id) => {
  await api.post(`/benefit-allocations/${id}/approve/`)
  fetchAllocations()
}

const disburse = async (id) => {
  await api.post(`/benefit-allocations/${id}/disburse/`)
  fetchAllocations()
}

onMounted(fetchAll)
</script>
<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.table-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.table thead th { background: var(--surface-secondary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); padding: 12px 16px; }
.table tbody td { padding: 12px 16px; font-size: 0.875rem; }
</style>
