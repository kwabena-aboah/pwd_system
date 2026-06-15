<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Benefit Programmes</h1>

      <button
        class="btn btn-primary"
        v-if="auth.canEdit"
        @click="openForm"
      >
        <i class="bi bi-plus-lg me-1"></i>
        Add Benefit
      </button>
    </div>

    <div class="table-card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>Name</th>
              <th>Partner</th>
              <th>Category</th>
              <th>Value</th>
              <th>Frequency</th>
              <th>Allocations</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="b in benefits" :key="b.id">
              <td><strong>{{ b.name }}</strong></td>
              <td>{{ b.partner_name }}</td>
              <td>{{ b.category_name }}</td>
              <td>
                {{ b.value ? 'GHS ' + b.value : b.value_in_kind || '—' }}
              </td>
              <td>{{ b.frequency }}</td>
              <td>
                <span class="badge bg-primary-subtle text-primary">
                  {{ b.allocation_count }}
                </span>
              </td>
              <td>
                <span
                  class="badge"
                  :class="b.status === 'active'
                    ? 'bg-success-subtle text-success'
                    : 'bg-secondary-subtle text-secondary'"
                >
                  {{ b.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL -->
    <div v-if="showForm" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-lg modal-dialog-centered">

        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">Add Benefit Programme</h5>
            <button class="btn-close" @click="closeForm"></button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="submitForm">

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label>Name</label>
                  <input v-model="form.name" class="form-control" required />
                </div>

                <div class="col-md-6 mb-3">
                  <label>Partner</label>
                  <Multiselect
                    v-model="form.partner"
                    :options="partners"
                    label="name"
                    track-by="id"
                  />
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label>Category</label>
                  <Multiselect
                    v-model="form.category"
                    :options="categories"
                    label="name"
                    track-by="id"
                  />
                </div>

                <div class="col-md-6 mb-3">
                  <label>Frequency</label>
                  <Multiselect
                    v-model="form.frequency"
                    :options="frequencyOptions"
                    label="label"
                    track-by="value"
                  />
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label>Status</label>
                  <Multiselect
                    v-model="form.status"
                    :options="statusOptions"
                    label="label"
                    track-by="value"
                  />
                </div>

                <div class="col-md-6 mb-3">
                  <label>Disability Types</label>
                  <Multiselect
                    v-model="form.disability_types"
                    :options="disabilityTypes"
                    label="name"
                    track-by="id"
                    :multiple="true"
                  />
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label>Value</label>
                  <input v-model="form.value" type="number" class="form-control" />
                </div>

                <div class="col-md-6 mb-3">
                  <label>Value in Kind</label>
                  <input v-model="form.value_in_kind" class="form-control" />
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label>Start Date</label>
                  <input v-model="form.start_date" type="date" class="form-control" />
                </div>

                <div class="col-md-6 mb-3">
                  <label>End Date</label>
                  <input v-model="form.end_date" type="date" class="form-control" />
                </div>
              </div>

              <div class="mb-3">
                <label>Description</label>
                <textarea v-model="form.description" class="form-control"></textarea>
              </div>

              <div class="mb-3">
                <label>Eligibility Criteria</label>
                <textarea v-model="form.eligibility_criteria" class="form-control"></textarea>
              </div>

              <div class="mb-3">
                <label>Max Beneficiaries</label>
                <input v-model="form.max_beneficiaries" type="number" class="form-control" />
              </div>

              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary" @click="closeForm">
                  Cancel
                </button>

                <button type="submit" class="btn btn-primary" :disabled="saving">
                  Save
                </button>
              </div>

            </form>
          </div>

        </div>
        </div>
    </div>

  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'

import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()

const benefits = ref([])
const showForm = ref(false)
const loading = ref(false)
const saving = ref(false)

const partners = ref([])
const categories = ref([])
const disabilityTypes = ref([])

const frequencyOptions = [
  { value: 'once', label: 'One Time' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'quarterly', label: 'Quarterly' },
  { value: 'annual', label: 'Annual' }
]

const statusOptions = [
  { value: 'active', label: 'Active' },
  { value: 'suspended', label: 'Suspended' },
  { value: 'completed', label: 'Completed' },
  { value: 'pending', label: 'Pending' }
]

const form = ref({
  name: '',
  partner: null,
  category: null,
  frequency: null,
  status: null,
  disability_types: [],
  value: '',
  value_in_kind: '',
  start_date: '',
  end_date: '',
  description: '',
  eligibility_criteria: '',
  max_beneficiaries: ''
})

function openForm() {
  showForm.value = true
}

function closeForm() {
  showForm.value = false
}

function resetForm() {
  form.value = {
    name: '',
    partner: null,
    category: null,
    frequency: null,
    status: null,
    disability_types: [],
    value: '',
    value_in_kind: '',
    start_date: '',
    end_date: '',
    description: '',
    eligibility_criteria: '',
    max_beneficiaries: ''
  }
}

async function submitForm() {
  saving.value = true

  try {
    await api.post('/benefits/', {
      name: form.value.name,
      description: form.value.description,

      start_date: form.value.start_date,
      end_date: form.value.end_date,

      value: form.value.value || null,
      value_in_kind: form.value.value_in_kind || '',

      eligibility_criteria: form.value.eligibility_criteria,

      max_beneficiaries:
        form.value.max_beneficiaries || null,

      partner: form.value.partner?.id,

      category: form.value.category?.id,

      frequency: form.value.frequency?.value,

      status: form.value.status?.value,

      target_disability_types:
        form.value.disability_types.map(
          item => item.id
        )
    })

    await fetchBenefits()

    resetForm()

    closeForm()

  } catch (error) {
    console.error(error)

    alert(
      error.response?.data?.detail ||
      'Failed to save benefit'
    )
  } finally {
    saving.value = false
  }
}

async function fetchBenefits() {
  const { data } = await api.get('/benefits/')
  benefits.value = data.results || data
}

async function loadPartners() {
  const { data } = await api.get('/partners/')
  partners.value = data.results || data
}

async function loadCategories() {
  const { data } = await api.get('/benefit-categories/')
  categories.value = data.results || data
}

async function loadDisabilityTypes() {
  const { data } = await api.get('/disability-types/')
  disabilityTypes.value = data.results || data
}

onMounted(async () => {
  await Promise.all([
    fetchBenefits(),
    loadPartners(),
    loadCategories(),
    loadDisabilityTypes()
  ])
})
</script>
<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.table-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.table thead th { background: var(--surface-secondary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); padding: 12px 16px; }
.table tbody td { padding: 12px 16px; font-size: 0.875rem; }
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
