```vue
<template>
  <div>
    <!-- Header -->
    <div class="page-header">
      <h1 class="page-title">Benefit Allocations</h1>

      <div class="d-flex gap-2 align-items-center">
        <span class="badge bg-warning-subtle text-warning fs-6">
          {{ pendingCount }} pending approval
        </span>

        <button
          v-if="auth.canEdit"
          class="btn btn-primary"
          @click="openForm"
        >
          <i class="bi bi-plus-lg me-1"></i>
          New Allocation
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filter-bar mb-3">
      <select
        v-model="statusFilter"
        class="form-select"
        style="width: 180px"
        @change="fetchAllocations"
      >
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="disbursed">Disbursed</option>
        <option value="rejected">Rejected</option>
      </select>
    </div>

    <!-- Table -->
    <div class="table-card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead>
            <tr>
              <th>PWD</th>
              <th>Benefit</th>
              <th>Partner</th>
              <th>Amount</th>
              <th>Date</th>
              <th>Status</th>
              <th width="120">Actions</th>
            </tr>
          </thead>

          <tbody v-if="!loading">
            <tr
              v-for="allocation in allocations"
              :key="allocation.id"
            >
              <td>
                <strong>{{ allocation.pwd_name }}</strong>
                <br>
                <small class="text-muted">
                  {{ allocation.pwd_reg }}
                </small>
              </td>

              <td>{{ allocation.benefit_name }}</td>

              <td>
                {{ allocation.partner_name || '—' }}
              </td>

              <td>
                {{
                  allocation.amount_disbursed
                    ? `GHS ${allocation.amount_disbursed}`
                    : allocation.in_kind_description || '—'
                }}
              </td>

              <td>{{ allocation.allocation_date }}</td>

              <td>
                <span
                  class="badge"
                  :class="badge(allocation.status)"
                >
                  {{ allocation.status }}
                </span>
              </td>

              <td>
                <button
                  v-if="
                    allocation.status === 'pending' &&
                    auth.canEdit
                  "
                  class="btn btn-sm btn-outline-success me-1"
                  @click="approveAllocation(allocation.id)"
                >
                  <i class="bi bi-check-lg"></i>
                </button>

                <button
                  v-if="
                    allocation.status === 'approved' &&
                    auth.canEdit
                  "
                  class="btn btn-sm btn-outline-primary"
                  @click="disburseAllocation(allocation.id)"
                >
                  <i class="bi bi-cash"></i>
                </button>
              </td>
            </tr>

            <tr v-if="!allocations.length">
              <td colspan="7" class="text-center py-4">
                No allocations found
              </td>
            </tr>
          </tbody>

          <tbody v-else>
            <tr>
              <td colspan="7" class="text-center py-4">
                Loading allocations...
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

<!-- Modal -->
<div v-if="showForm" class="modal-overlay">
  <div class="allocation-modal">

    <div class="modal-header">
      <h5>New Benefit Allocation</h5>

      <button
        class="btn-close"
        @click="showForm = false"
      ></button>
    </div>

    <form @submit.prevent="createAllocation">

      <div class="modal-body">

        <div class="row">

          <!-- PWD -->
          <div class="col-md-6 mb-3">
            <label class="form-label">PWD</label>

            <Multiselect
              v-model="selectedPwd"
              :options="pwdOptions"
              :loading="loadingPwds"
              :internal-search="false"
              :searchable="true"
              label="display_name"
              track-by="id"
              placeholder="Search PWD"
              @search-change="searchPwds"
            />
          </div>

          <!-- Benefit -->
          <div class="col-md-6 mb-3">
            <label class="form-label">Benefit</label>

            <Multiselect
              v-model="selectedBenefit"
              :options="benefitOptions"
              :loading="loadingBenefits"
              :internal-search="false"
              :searchable="true"
              label="name"
              track-by="id"
              placeholder="Search Benefit"
              @search-change="searchBenefits"
            />
          </div>

          <!-- Allocation Date -->
          <div class="col-md-6 mb-3">
            <label class="form-label">
              Allocation Date
            </label>

            <input
              v-model="form.allocation_date"
              type="date"
              class="form-control"
            >
          </div>

          <!-- Disbursement Date -->
          <div class="col-md-6 mb-3">
            <label class="form-label">
              Disbursement Date
            </label>

            <input
              v-model="form.disbursement_date"
              type="date"
              class="form-control"
            >
          </div>

          <!-- Amount -->
          <div class="col-md-6 mb-3">
            <label class="form-label">
              Amount Disbursed
            </label>

            <input
              v-model="form.amount_disbursed"
              type="number"
              step="0.01"
              class="form-control"
            >
          </div>

          <!-- Status -->
          <div class="col-md-6 mb-3">
            <label class="form-label">
              Status
            </label>

            <Multiselect
              v-model="form.status"
              :options="statusOptions"
              label="label"
              track-by="value"
              placeholder="Select status"
            />
          </div>

          <!-- Approval Date -->
          <div class="col-md-6 mb-3">
            <label class="form-label">
              Approval Date
            </label>

            <input
              v-model="form.approval_date"
              type="datetime-local"
              class="form-control"
            >
          </div>

          <!-- Receipt -->
          <div class="col-md-6 mb-3">
            <label class="form-label">
              Receipt Document
            </label>

            <input
              type="file"
              class="form-control"
              @change="handleReceiptUpload"
            >
          </div>

          <!-- In Kind -->
          <div class="col-md-12 mb-3">
            <label class="form-label">
              In-Kind Description
            </label>

            <textarea
              v-model="form.in_kind_description"
              rows="3"
              class="form-control"
            ></textarea>
          </div>

          <!-- Notes -->
          <div class="col-md-12 mb-3">
            <label class="form-label">
              Notes
            </label>

            <textarea
              v-model="form.notes"
              rows="4"
              class="form-control"
            ></textarea>
          </div>

        </div>

      </div>

      <div class="modal-footer">
        <button
          type="button"
          class="btn btn-secondary"
          @click="showForm = false"
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

          Save Allocation
        </button>
      </div>

    </form>

  </div>
          </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'

import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()

const allocations = ref([])
const loading = ref(false)
const saving = ref(false)

const showForm = ref(false)
const statusFilter = ref('')

const selectedPwd = ref(null)
const selectedBenefit = ref(null)

const pwdOptions = ref([])
const benefitOptions = ref([])

const loadingPwds = ref(false)
const loadingBenefits = ref(false)

const statusOptions = [
  {
    value: 'pending',
    label: 'Pending'
  },
  {
    value: 'approved',
    label: 'Approved'
  },
  {
    value: 'disbursed',
    label: 'Disbursed'
  },
  {
    value: 'rejected',
    label: 'Rejected'
  }
]

const form = ref({
  allocation_date: '',
  disbursement_date: '',
  amount_disbursed: '',
  in_kind_description: '',
  approval_date: '',
  notes: '',
  receipt_document: null,
  status: null
})

const pendingCount = computed(() =>
  allocations.value.filter(
    item => item.status === 'pending'
  ).length
)

const badge = status => ({
  disbursed: 'bg-success-subtle text-success',
  approved: 'bg-info-subtle text-info',
  pending: 'bg-warning-subtle text-warning',
  rejected: 'bg-danger-subtle text-danger'
}[status] || 'bg-secondary-subtle text-secondary')

async function fetchAllocations() {
  loading.value = true

  try {
    const params = {}

    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    const { data } = await api.get(
      '/benefit-allocations/',
      { params }
    )

    allocations.value = data.results || data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

function handleReceiptUpload(event) {
  form.value.receipt_document =
    event.target.files[0]
}

async function searchPwds(query) {
  if (!query || query.length < 2) return

  loadingPwds.value = true

  try {
    const { data } = await api.get('/pwds/', {
      params: { search: query }
    })

    pwdOptions.value = (
      data.results || data
    ).map(item => ({
      ...item,
      display_name:
        `${item.first_name} ${item.last_name} (${item.registration_number})`
    }))
  } finally {
    loadingPwds.value = false
  }
}

async function searchBenefits(query) {
  if (!query || query.length < 2) return

  loadingBenefits.value = true

  try {
    const { data } = await api.get('/benefits/', {
      params: { search: query }
    })

    benefitOptions.value = data.results || data
  } finally {
    loadingBenefits.value = false
  }
}

function openForm() {
  selectedPwd.value = null
  selectedBenefit.value = null

  form.value = {
    allocation_date:
      new Date().toISOString().split('T')[0],

    disbursement_date: '',

    amount_disbursed: '',

    in_kind_description: '',

    approval_date: '',

    notes: '',

    receipt_document: null,

    status: statusOptions[0]
  }

  showForm.value = true
}

async function createAllocation() {

  if (!selectedPwd.value) {
    alert('Please select a PWD')
    return
  }

  if (!selectedBenefit.value) {
    alert('Please select a benefit')
    return
  }

  saving.value = true

  try {

    const payload = new FormData()

    payload.append(
      'pwd',
      selectedPwd.value.id
    )

    payload.append(
      'benefit',
      selectedBenefit.value.id
    )

    payload.append(
      'allocation_date',
      form.value.allocation_date
    )

    payload.append(
      'disbursement_date',
      form.value.disbursement_date || ''
    )

    payload.append(
      'amount_disbursed',
      form.value.amount_disbursed || ''
    )

    payload.append(
      'in_kind_description',
      form.value.in_kind_description || ''
    )

    payload.append(
      'approval_date',
      form.value.approval_date || ''
    )

    payload.append(
      'notes',
      form.value.notes || ''
    )

    payload.append(
      'status',
      form.value.status?.value || 'pending'
    )

    if (form.value.receipt_document) {
      payload.append(
        'receipt_document',
        form.value.receipt_document
      )
    }

    await api.post(
      '/benefit-allocations/',
      payload,
      {
        headers: {
          'Content-Type':
            'multipart/form-data'
        }
      }
    )

    showForm.value = false

    await fetchAllocations()

  } catch (error) {

    console.error(error)

    alert(
      error.response?.data?.detail ||
      'Failed to save allocation'
    )

  } finally {
    saving.value = false
  }
}

async function approveAllocation(id) {
  await api.post(
    `/benefit-allocations/${id}/approve/`
  )

  await fetchAllocations()
}

async function disburseAllocation(id) {
  await api.post(
    `/benefit-allocations/${id}/disburse/`
  )

  await fetchAllocations()
}

onMounted(fetchAllocations)
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
}

.table-card {
  background: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.allocation-modal {
  width: 100%;
  max-width: 700px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}

.modal-header,
.modal-footer {
  padding: 1rem;
}

.modal-body {
  padding: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
```
