<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">PWD Records</h1>
        <p class="page-subtitle">{{ total.toLocaleString() }} persons registered</p>
      </div>
      <div class="d-flex gap-2 flex-wrap">
        <button class="btn btn-outline-secondary btn-sm" @click="exportCSV">
          <i class="bi bi-download me-1"></i><span class="d-none d-sm-inline">Export CSV</span>
        </button>
        <router-link to="/pwds/new" class="btn btn-primary btn-sm" v-if="auth.canEdit">
          <i class="bi bi-plus-lg me-1"></i><span class="d-none d-sm-inline">Register PWD</span><span class="d-sm-none">Add</span>
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-panel">
      <div class="filter-search">
        <i class="bi bi-search"></i>
        <input v-model="search" type="text" placeholder="Search name, reg. no., ID..." class="form-control" @input="debouncedFetch">
      </div>
      <div class="filter-selects">
        <select v-model="filters.status" class="form-select form-select-sm" @change="fetchPWDs">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="deceased">Deceased</option>
          <option value="relocated">Relocated</option>
          <option value="inactive">Inactive</option>
        </select>
        <select v-model="filters.gender" class="form-select form-select-sm" @change="fetchPWDs">
          <option value="">All Gender</option>
          <option value="M">Male</option>
          <option value="F">Female</option>
        </select>
        <select v-model="filters.ai_risk_label" class="form-select form-select-sm" @change="fetchPWDs">
          <option value="">All Risk</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
        <input v-model="filters.district" type="text" placeholder="District..." class="form-control form-control-sm district-input" @change="fetchPWDs">
      </div>
    </div>

    <!-- Content -->
    <div class="table-card">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border" style="color:var(--system-primary)"></div>
        <p class="mt-2 text-muted small">Loading records...</p>
      </div>

      <div v-else-if="!pwds.length" class="empty-state">
        <i class="bi bi-people"></i>
        <p>No PWD records found</p>
        <router-link to="/pwds/new" class="btn btn-primary btn-sm" v-if="auth.canEdit">Register First PWD</router-link>
      </div>

      <!-- Desktop Table -->
      <div v-else class="d-none d-md-block table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Photo</th>
              <th>Reg. No.</th>
              <th>Full Name</th>
              <th>Age/Gender</th>
              <th>Disability</th>
              <th>Community</th>
              <th>District</th>
              <th>Risk</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pwd in pwds" :key="pwd.id" @click="router.push(`/pwds/${pwd.id}`)" style="cursor:pointer">
              <td>
                <img v-if="pwd.photo" :src="pwd.photo" class="table-photo" :alt="pwd.first_name">
                <div v-else class="table-photo-placeholder">{{ pwd.first_name[0] }}{{ pwd.last_name[0] }}</div>
              </td>
              <td><code class="reg-code">{{ pwd.registration_number }}</code></td>
              <td class="fw-semibold">{{ pwd.first_name }} {{ pwd.last_name }}</td>
              <td class="text-muted">{{ pwd.age }} / {{ pwd.gender === 'M' ? 'M' : pwd.gender === 'F' ? 'F' : '?' }}</td>
              <td><span class="text-truncate-cell">{{ pwd.disability_summary || '—' }}</span></td>
              <td>{{ pwd.community }}</td>
              <td>{{ pwd.district }}</td>
              <td><span class="badge" :class="riskBadge(pwd.ai_risk_label)">{{ pwd.ai_risk_label || '—' }}</span></td>
              <td><span class="badge" :class="statusBadge(pwd.status)">{{ pwd.status }}</span></td>
              <td @click.stop>
                <div class="d-flex gap-1">
                  <router-link :to="`/pwds/${pwd.id}`" class="btn btn-sm btn-outline-primary"><i class="bi bi-eye"></i></router-link>
                  <router-link :to="`/pwds/${pwd.id}/edit`" class="btn btn-sm btn-outline-secondary" v-if="auth.canEdit"><i class="bi bi-pencil"></i></router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile Cards -->
      <div class="d-md-none">
        <div v-for="pwd in pwds" :key="pwd.id" class="pwd-card-mobile" @click="router.push(`/pwds/${pwd.id}`)">
          <div class="pwd-card-mobile-left">
            <img v-if="pwd.photo" :src="pwd.photo" class="pwd-card-photo" :alt="pwd.first_name">
            <div v-else class="pwd-card-photo-placeholder">{{ pwd.first_name[0] }}{{ pwd.last_name[0] }}</div>
          </div>
          <div class="pwd-card-mobile-body">
            <div class="d-flex justify-content-between align-items-start">
              <strong class="pwd-card-name">{{ pwd.first_name }} {{ pwd.last_name }}</strong>
              <span class="badge" :class="riskBadge(pwd.ai_risk_label)">{{ pwd.ai_risk_label || '—' }}</span>
            </div>
            <code class="text-muted" style="font-size:0.72rem">{{ pwd.registration_number }}</code>
            <div class="pwd-card-details">
              <span v-if="pwd.disability_summary"><i class="bi bi-accessibility me-1"></i>{{ pwd.disability_summary }}</span>
              <span><i class="bi bi-geo-alt me-1"></i>{{ pwd.community }}, {{ pwd.district }}</span>
            </div>
            <span class="badge mt-1" :class="statusBadge(pwd.status)">{{ pwd.status }}</span>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination-bar" v-if="totalPages > 1">
        <button class="btn btn-sm btn-outline-secondary" :disabled="page === 1" @click="changePage(page - 1)">
          <i class="bi bi-chevron-left"></i>
        </button>
        <span class="page-info">Page {{ page }} of {{ totalPages }}</span>
        <button class="btn btn-sm btn-outline-secondary" :disabled="page === totalPages" @click="changePage(page + 1)">
          <i class="bi bi-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const pwds = ref([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const totalPages = ref(1)
const search = ref(route.query.search || '')
const filters = ref({ status: '', gender: '', ai_risk_label: '', district: '' })

let debounceTimer = null
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; fetchPWDs() }, 400)
}

async function fetchPWDs() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize, search: search.value, ...filters.value }
    Object.keys(params).forEach(k => !params[k] && delete params[k])
    const { data } = await api.get('/pwds/', { params })
    pwds.value = data.results ?? data
    total.value = data.count ?? data.length
    totalPages.value = Math.ceil(total.value / pageSize) || 1
  } finally { loading.value = false }
}

function changePage(p) { page.value = p; fetchPWDs(); window.scrollTo(0, 0) }

const riskBadge = l => ({ low:'bg-success-subtle text-success', medium:'bg-warning-subtle text-warning', high:'bg-danger-subtle text-danger', critical:'bg-danger text-white' }[l] || 'bg-secondary-subtle text-secondary')
const statusBadge = s => ({ active:'bg-success-subtle text-success', deceased:'bg-dark text-white', relocated:'bg-info-subtle text-info', inactive:'bg-secondary-subtle text-secondary' }[s] || 'bg-secondary-subtle text-secondary')

function exportCSV() {
  const headers = ['Reg No','First Name','Last Name','Age','Gender','Community','District','Status','Risk']
  const rows = pwds.value.map(p => [p.registration_number,p.first_name,p.last_name,p.age,p.gender,p.community,p.district,p.status,p.ai_risk_label])
  const csv = [headers,...rows].map(r => r.join(',')).join('\n')
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(new Blob([csv],{type:'text/csv'})), download: 'pwds.csv' })
  a.click()
}

onMounted(fetchPWDs)
watch(() => route.query.search, v => { search.value = v || ''; fetchPWDs() })
</script>

<style scoped>
.filter-panel {
  background: white; border-radius: var(--radius);
  padding: 14px 16px; box-shadow: var(--shadow);
  margin-bottom: 16px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
}
.filter-search { position: relative; flex: 1; min-width: 200px; }
.filter-search i { position: absolute; left: 11px; top: 50%; transform: translateY(-50%); color: var(--text-secondary); font-size: 0.875rem; pointer-events: none; }
.filter-search .form-control { padding-left: 34px; }
.filter-selects { display: flex; gap: 8px; flex-wrap: wrap; }
.filter-selects .form-select { width: 130px; }
.district-input { width: 130px; }

.table-photo { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; }
.table-photo-placeholder { width: 38px; height: 38px; border-radius: 50%; background: var(--system-primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.78rem; }
.text-truncate-cell { display: block; max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.reg-code { font-size: 0.78rem; color: var(--system-primary); background: #eff6ff; padding: 2px 6px; border-radius: 4px; }

/* Mobile cards */
.pwd-card-mobile {
  display: flex; gap: 12px; padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  cursor: pointer; transition: background 0.12s;
}
.pwd-card-mobile:hover { background: var(--surface-secondary); }
.pwd-card-mobile:last-child { border-bottom: none; }
.pwd-card-photo { width: 52px; height: 52px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.pwd-card-photo-placeholder { width: 52px; height: 52px; border-radius: 50%; background: var(--system-primary); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.9rem; flex-shrink: 0; }
.pwd-card-mobile-body { flex: 1; min-width: 0; }
.pwd-card-name { font-size: 0.9rem; display: block; }
.pwd-card-details { display: flex; flex-direction: column; gap: 2px; margin-top: 4px; }
.pwd-card-details span { font-size: 0.76rem; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

@media (max-width: 575px) {
  .filter-selects .form-select, .district-input { width: 100px; font-size: 0.78rem; }
  .filter-panel { padding: 10px 12px; }
}
</style>
