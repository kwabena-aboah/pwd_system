<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Benefit Allocations</h1>
      <div class="d-flex gap-2 align-items-center">
        <span class="badge bg-warning-subtle text-warning fs-6">{{ pendingCount }} pending approval</span>
        <button class="btn btn-primary" v-if="auth.canEdit" @click="showForm = true">
          <i class="bi bi-plus-lg me-1"></i>New Allocation
        </button>
      </div>
    </div>
    <div class="filter-bar mb-3">
      <select v-model="statusFilter" class="form-select" style="width:160px" @change="fetch">
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="disbursed">Disbursed</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>
    <div class="table-card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr><th>PWD</th><th>Benefit</th><th>Partner</th><th>Amount</th><th>Date</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            <tr v-for="a in allocations" :key="a.id">
              <td><strong>{{ a.pwd_name }}</strong><br><small class="text-muted">{{ a.pwd_reg }}</small></td>
              <td>{{ a.benefit_name }}</td>
              <td>{{ a.partner_name }}</td>
              <td>{{ a.amount_disbursed ? 'GHS ' + a.amount_disbursed : a.in_kind_description || '—' }}</td>
              <td>{{ a.allocation_date }}</td>
              <td><span class="badge" :class="badge(a.status)">{{ a.status }}</span></td>
              <td>
                <button v-if="a.status === 'pending' && auth.canEdit" class="btn btn-sm btn-outline-success me-1" @click="approve(a.id)">
                  <i class="bi bi-check-lg"></i>
                </button>
                <button v-if="a.status === 'approved' && auth.canEdit" class="btn btn-sm btn-outline-primary" @click="disburse(a.id)">
                  <i class="bi bi-cash"></i>
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
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
const auth = useAuthStore()
const allocations = ref([])
const statusFilter = ref('')
const showForm = ref(false)
const pendingCount = computed(() => allocations.value.filter(a => a.status === 'pending').length)
const badge = s => ({ disbursed: 'bg-success-subtle text-success', approved: 'bg-info-subtle text-info', pending: 'bg-warning-subtle text-warning', rejected: 'bg-danger-subtle text-danger' }[s] || 'bg-secondary-subtle text-secondary')
async function fetch() {
  const p = statusFilter.value ? { status: statusFilter.value } : {}
  const { data } = await api.get('/benefit-allocations/', { params: p })
  allocations.value = data.results ?? data
}
async function approve(id) { await api.post(`/benefit-allocations/${id}/approve/`); fetch() }
async function disburse(id) { await api.post(`/benefit-allocations/${id}/disburse/`); fetch() }
onMounted(fetch)
</script>
<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.table-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.table thead th { background: var(--surface-secondary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); padding: 12px 16px; }
.table tbody td { padding: 12px 16px; font-size: 0.875rem; }
</style>
