<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Benefit Programmes</h1>
      <button class="btn btn-primary" v-if="auth.canEdit" @click="openForm">
        <i class="bi bi-plus-lg me-1"></i>Add Benefit
      </button>
    </div>

    <!-- Modal -->
    <div class="modal-overlay" v-if="showForm" @click.self="closeForm">
      <div class="modal-box">
        <h5 class="mb-3">Add New Benefit</h5>

        <div class="row g-3">
          <!-- Partner -->
          <div class="col-6">
            <label class="form-label">Partner *</label>
            <select v-model="newBenefit.partner" class="form-select">
              <option value="">Select partner</option>
              <option v-for="p in partners" :key="p.id" :value="p.id">
                {{ p.name }}
              </option>
            </select>
          </div>

          <!-- Category -->
          <div class="col-6">
            <label class="form-label">Category *</label>
            <select v-model="newBenefit.category" class="form-select">
              <option value="">Select category</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">
                {{ c.name }}
              </option>
            </select>
          </div>

          <div class="col-6">
            <label class="form-label">Name *</label>
            <input v-model="newBenefit.name" class="form-control" />
          </div>

          <div class="col-6">
            <label class="form-label">Description</label>
            <textarea v-model="newBenefit.description" class="form-control"></textarea>
          </div>

          <div class="col-6">
            <label class="form-label">Value</label>
            <input v-model="newBenefit.value" type="number" class="form-control" />
          </div>

          <div class="col-6">
            <label class="form-label">Value in kind</label>
            <input v-model="newBenefit.value_in_kind" class="form-control" />
          </div>

          <div class="col-6">
            <label class="form-label">Frequency *</label>
            <select v-model="newBenefit.frequency" class="form-select">
              <option value="once">One-Time</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="as_needed">As Needed</option>
            </select>
          </div>

          <div class="col-6">
            <label class="form-label">Eligibility Criteria</label>
            <textarea v-model="newBenefit.eligibility_criteria" class="form-control"></textarea>
          </div>

          <div class="col-6">
            <label class="form-label">Start Date *</label>
            <input v-model="newBenefit.start_date" type="date" class="form-control" />
          </div>

          <div class="col-6">
            <label class="form-label">End Date *</label>
            <input v-model="newBenefit.end_date" type="date" class="form-control" />
          </div>

          <div class="col-6">
            <label class="form-label">Status *</label>
            <select v-model="newBenefit.status" class="form-select">
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="completed">Completed</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <!-- Multi select -->
          <div class="col-6">
            <label class="form-label">Target Disability Types *</label>
            <select v-model="newBenefit.target_disability_types" multiple class="form-select">
              <option v-for="d in disabilityTypes" :key="d.id" :value="d.id">
                {{ d.name }}
              </option>
            </select>
          </div>

          <div class="col-6">
            <label class="form-label">Max Beneficiaries *</label>
            <input v-model="newBenefit.max_beneficiaries" type="number" class="form-control" />
          </div>
        </div>

        <div class="d-flex justify-content-end gap-2 mt-3">
          <button class="btn btn-outline-secondary" @click="closeForm">Cancel</button>
          <button class="btn btn-primary" @click="createBenefit" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save Benefit' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="table-card">
      <table class="table table-hover">
        <thead>
          <tr>
            <th>Name</th><th>Partner</th><th>Category</th><th>Value</th>
            <th>Frequency</th><th>Allocations</th><th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="b in benefits" :key="b.id">
            <td><strong>{{ b.name }}</strong></td>
            <td>{{ b.partner_name }}</td>
            <td>{{ b.category_name }}</td>
            <td>{{ b.value ? 'GHS ' + b.value : b.value_in_kind || '—' }}</td>
            <td>{{ b.frequency }}</td>
            <td>{{ b.allocation_count }}</td>
            <td>{{ b.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()

const benefits = ref([])
const partners = ref([])
const categories = ref([])
const disabilityTypes = ref([])

const showForm = ref(false)
const loading = ref(false)

const defaultForm = () => ({
  partner: '',
  category: '',
  name: '',
  description: '',
  value: '',
  value_in_kind: '',
  frequency: 'once',
  eligibility_criteria: '',
  start_date: '',
  end_date: '',
  status: 'active',
  target_disability_types: [],
  max_beneficiaries: ''
})

const newBenefit = ref(defaultForm())

// Fetch all data
const fetchData = async () => {
  try {
    const [b, p, c, d] = await Promise.all([
      api.get('/benefits/'),
      api.get('/partners/'),
      api.get('/benefit-categories/'),
      api.get('/disability-types/')
    ])

    benefits.value = b.data.results ?? b.data
    partners.value = p.data.results ?? p.data
    categories.value = c.data.results ?? c.data
    disabilityTypes.value = d.data.results ?? d.data
  } catch (err) {
    console.error(err)
  }
}

// Open form
const openForm = () => {
  newBenefit.value = defaultForm()
  showForm.value = true
}

// Close form
const closeForm = () => {
  showForm.value = false
}

// Create benefit
const createBenefit = async () => {
  loading.value = true
  try {
    const { data } = await api.post('/benefits/', newBenefit.value)

    benefits.value.unshift(data)
    closeForm()
  } catch (err) {
    console.error(err.response?.data || err)
    alert('Failed to create benefit')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>
<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.table-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.table thead th { background: var(--surface-secondary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); padding: 12px 16px; }
.table tbody td { padding: 12px 16px; font-size: 0.875rem; }
</style> 
