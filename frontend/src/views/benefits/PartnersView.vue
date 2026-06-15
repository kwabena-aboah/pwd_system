<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Development Partners</h1>
        <p class="page-subtitle">{{ total }} partners registered</p>
      </div>

      <button
        v-if="auth.canEdit"
        class="btn btn-primary"
        @click="openForm"
      >
        <i class="bi bi-plus-lg me-1"></i>
        Add Partner
      </button>
    </div>

    <!-- Partner Cards -->
    <div class="row g-4">
      <div
        class="col-md-4"
        v-for="partner in partners"
        :key="partner.id"
      >
        <div class="partner-card">
          <div class="partner-header">
            <img
              v-if="partner.logo"
              :src="partner.logo"
              class="partner-logo"
              :alt="partner.name"
            />

            <div
              v-else
              class="partner-logo-placeholder"
            >
              <i class="bi bi-building-fill"></i>
            </div>

            <div>
              <h5 class="mb-1">{{ partner.name }}</h5>

              <span class="badge bg-primary-subtle text-primary">
                {{ partner.partner_type }}
              </span>

              <span
                v-if="partner.acronym"
                class="badge bg-secondary-subtle text-secondary ms-1"
              >
                {{ partner.acronym }}
              </span>
            </div>
          </div>

          <div class="partner-body">
            <p v-if="partner.contact_person" class="mb-1">
              <i class="bi bi-person me-2 text-primary"></i>
              {{ partner.contact_person }}
            </p>

            <p v-if="partner.contact_phone" class="mb-1">
              <i class="bi bi-telephone me-2 text-primary"></i>
              {{ partner.contact_phone }}
            </p>

            <p v-if="partner.district" class="mb-1">
              <i class="bi bi-geo-alt me-2 text-primary"></i>
              {{ partner.district }}, {{ partner.region }}
            </p>

            <p class="mb-0">
              <i class="bi bi-gift me-2 text-primary"></i>
              {{ partner.benefit_count }} benefits
            </p>
          </div>

          <div class="partner-footer">
            <span
              class="badge"
              :class="partner.is_active
                ? 'bg-success-subtle text-success'
                : 'bg-danger-subtle text-danger'"
            >
              {{ partner.is_active ? 'Active' : 'Inactive' }}
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
      <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">
              Add Development Partner
            </h5>

            <button
              type="button"
              class="btn-close"
              @click="closeForm"
            ></button>
          </div>

          <form @submit.prevent="savePartner">
            <div class="modal-body">

              <div class="row g-3">

                <div class="col-md-6">
                  <label class="form-label">
                    Name
                  </label>
                  <input
                    v-model="form.name"
                    class="form-control"
                    required
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label">
                    Partner Type
                  </label>

                  <Multiselect
                    v-model="form.partner_type"
                    :options="partnerTypeOptions"
                    label="label"
                    track-by="value"
                    placeholder="Select partner type"
                  />
                </div>

                <div class="col-md-4">
                  <label class="form-label">
                    Acronym
                  </label>

                  <input
                    v-model="form.acronym"
                    class="form-control"
                  />
                </div>

                <div class="col-md-8">
                  <label class="form-label">
                    Registration Number
                  </label>

                  <input
                    v-model="form.registration_number"
                    class="form-control"
                  />
                </div>

                <div class="col-md-12">
                  <label class="form-label">
                    Logo
                  </label>

                  <input
                    type="file"
                    class="form-control"
                    accept="image/*"
                    @change="handleLogo"
                  />
                </div>

                <div class="col-md-4">
                  <label class="form-label">
                    Contact Person
                  </label>

                  <input
                    v-model="form.contact_person"
                    class="form-control"
                  />
                </div>

                <div class="col-md-4">
                  <label class="form-label">
                    Contact Email
                  </label>

                  <input
                    v-model="form.contact_email"
                    type="email"
                    class="form-control"
                  />
                </div>

                <div class="col-md-4">
                  <label class="form-label">
                    Contact Phone
                  </label>

                  <input
                    v-model="form.contact_phone"
                    class="form-control"
                  />
                </div>

                <div class="col-md-12">
                  <label class="form-label">
                    Address
                  </label>

                  <textarea
                    v-model="form.address"
                    rows="3"
                    class="form-control"
                  ></textarea>
                </div>

                <div class="col-md-6">
                  <label class="form-label">
                    District
                  </label>

                  <input
                    v-model="form.district"
                    class="form-control"
                  />
                </div>

                <div class="col-md-6">
                  <label class="form-label">
                    Region
                  </label>

                  <input
                    v-model="form.region"
                    class="form-control"
                  />
                </div>

                <div class="col-md-12">
                  <div class="form-check">
                    <input
                      id="active"
                      v-model="form.is_active"
                      type="checkbox"
                      class="form-check-input"
                    />

                    <label
                      for="active"
                      class="form-check-label"
                    >
                      Active Partner
                    </label>
                  </div>
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

                Save Partner
              </button>
            </div>
          </form>

        </div>
      </div>
    </div>

    <!-- Backdrop -->
    <div
      v-if="showForm"
      class="modal-backdrop fade show"
    ></div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Multiselect from 'vue-multiselect'
import 'vue-multiselect/dist/vue-multiselect.min.css'

import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()

const partners = ref([])
const total = ref(0)

const showForm = ref(false)
const saving = ref(false)

const partnerTypeOptions = [
  { value: 'government', label: 'Government' },
  { value: 'ngo', label: 'NGO' },
  { value: 'ingo', label: 'INGO' },
  { value: 'foundation', label: 'Foundation' },
  { value: 'corporate', label: 'Corporate' },
  { value: 'faith_based', label: 'Faith Based Organisation' },
  { value: 'individual', label: 'Individual Donor' }
]

const form = ref({
  name: '',
  partner_type: null,
  acronym: '',
  logo: null,
  contact_person: '',
  contact_email: '',
  contact_phone: '',
  address: '',
  district: '',
  region: '',
  registration_number: '',
  is_active: true
})

function resetForm() {
  form.value = {
    name: '',
    partner_type: null,
    acronym: '',
    logo: null,
    contact_person: '',
    contact_email: '',
    contact_phone: '',
    address: '',
    district: '',
    region: '',
    registration_number: '',
    is_active: true
  }
}

function openForm() {
  resetForm()
  showForm.value = true
}

function closeForm() {
  showForm.value = false
}

function handleLogo(event) {
  form.value.logo = event.target.files[0]
}

async function loadPartners() {
  const { data } = await api.get('/partners/')

  partners.value = data.results ?? data
  total.value = data.count ?? data.length
}

async function savePartner() {
  saving.value = true

  try {
    const payload = new FormData()

    payload.append('name', form.value.name)

    payload.append(
      'partner_type',
      form.value.partner_type?.value || ''
    )

    payload.append(
      'acronym',
      form.value.acronym
    )

    payload.append(
      'contact_person',
      form.value.contact_person
    )

    payload.append(
      'contact_email',
      form.value.contact_email
    )

    payload.append(
      'contact_phone',
      form.value.contact_phone
    )

    payload.append(
      'address',
      form.value.address
    )

    payload.append(
      'district',
      form.value.district
    )

    payload.append(
      'region',
      form.value.region
    )

    payload.append(
      'registration_number',
      form.value.registration_number
    )

    payload.append(
      'is_active',
      form.value.is_active
    )

    if (form.value.logo) {
      payload.append(
        'logo',
        form.value.logo
      )
    }

    await api.post('/partners/', payload, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    closeForm()
    await loadPartners()

  } catch (error) {
    console.error(error)
    alert('Failed to save partner')
  } finally {
    saving.value = false
  }
}

onMounted(loadPartners)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.page-subtitle { color: var(--text-secondary); font-size: 0.9rem; }
.partner-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; height: 100%; transition: box-shadow 0.2s; }
.partner-card:hover { box-shadow: var(--shadow-md); }
.partner-header { display: flex; align-items: center; gap: 14px; padding: 20px; border-bottom: 1px solid var(--border); }
.partner-logo { width: 52px; height: 52px; object-fit: contain; border-radius: 10px; border: 1px solid var(--border); }
.partner-logo-placeholder { width: 52px; height: 52px; border-radius: 10px; background: var(--bs-primary, #1a56db); display: flex; align-items: center; justify-content: center; color: white; font-size: 1.4rem; flex-shrink: 0; }
.partner-body { padding: 16px 20px; font-size: 0.875rem; }
.partner-footer { padding: 12px 20px; background: var(--surface-secondary); }
.modal-content {
  border: none;
  border-radius: 16px;
}

.modal-header {
  border-bottom: 1px solid #e5e7eb;
}

.modal-footer {
  border-top: 1px solid #e5e7eb;
}

.form-label {
  font-weight: 600;
  margin-bottom: 6px;
}
</style>
