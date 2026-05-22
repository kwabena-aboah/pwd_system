<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Development Partners</h1>
        <p class="page-subtitle">{{ total }} partners registered</p>
      </div>
      <button class="btn btn-primary" @click.self="showForm = true" v-if="auth.canEdit">
        <i class="bi bi-plus-lg me-1"></i>Add Partner
      </button>
    </div>

     <!-- Add Partner Modal -->
    <div class="modal-overlay" v-if="showForm" @click.self="showForm = false">
      <div class="modal-box">
        <h5 class="mb-3">Add New Partner</h5>
        <div class="row g-3">
          <div class="col-6"><label class="form-label">Name *</label><input v-model="newPartner.name" class="form-control"></div>
          <div class="col-6"><label class="form-label">Partner Type *</label>
            <select v-model="newPartner.partner_type" class="form-select">
              <option value="ngo">NGO</option>
              <option value="government">Government Institution</option>
              <option value="international">International Organization</option>
              <option value="faith_based">Faith-Based Organization</option>
              <option value="private">Private Sector</option>
            </select>
          </div>
          <div class="col-6"><label class="form-label">Acronym</label><input v-model="newPartner.acronym" class="form-control"></div>
          <div class="col-6">
              <input type="file" id="photo-input" class="d-none" accept="image/*" @change="onPhotoChange">
              <label for="photo-input" class="btn btn-sm btn-outline-secondary"><i class="bi bi-camera me-1"></i>Upload Logo</label>
              <p class="text-muted small mt-1">JPG, PNG. Max 5MB</p>
          </div>
          <div class="col-6"><label class="form-label">Contact Person</label><input v-model="newPartner.contact_person" type="text" class="form-control"></div>
          <div class="col-6"><label class="form-label">Contact Email</label><input v-model="newPartner.contact_email" type="email" class="form-control"></div>
          <div class="col-6"><label class="form-label">Contact Phone</label><input v-model="newPartner.contact_phone" type="text" class="form-control"></div>
          <div class="col-6"><label class="form-label">Address</label><textarea v-model="newPartner.address" type="text" class="form-control"></textarea></div>
          <div class="col-6"><label class="form-label">District</label><input v-model="newPartner.district" type="text" class="form-control"></div>
          <div class="col-6"><label class="form-label">Region</label><input v-model="newPartner.region" type="text" class="form-control"></div>
          <div class="col-6"><label class="form-label">Registration Number</label><input v-model="newPartner.registration_number" type="text" class="form-control"></div>
        </div>
        <div class="d-flex justify-content-end gap-2 mt-3">
          <button class="btn btn-outline-secondary" @click="showForm = false">Cancel</button>
          <button class="btn btn-primary" @click="createPartner">Create Partner</button>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-md-4" v-for="p in partners" :key="p.id">
        <div class="partner-card">
          <div class="partner-header">
            <img v-if="p.logo" :src="p.logo" class="partner-logo" :alt="p.name">
            <div v-else class="partner-logo-placeholder"><i class="bi bi-building-fill"></i></div>
            <div>
              <h5 class="mb-1">{{ p.name }}</h5>
              <span class="badge bg-primary-subtle text-primary">{{ p.partner_type }}</span>
              <span v-if="p.acronym" class="badge bg-secondary-subtle text-secondary ms-1">{{ p.acronym }}</span>
            </div>
          </div>
          <div class="partner-body">
            <p v-if="p.contact_person" class="mb-1"><i class="bi bi-person me-2 text-primary"></i>{{ p.contact_person }}</p>
            <p v-if="p.contact_phone" class="mb-1"><i class="bi bi-telephone me-2 text-primary"></i>{{ p.contact_phone }}</p>
            <p v-if="p.district" class="mb-1"><i class="bi bi-geo-alt me-2 text-primary"></i>{{ p.district }}, {{ p.region }}</p>
            <p class="mb-0"><i class="bi bi-gift me-2 text-primary"></i>{{ p.benefit_count }} benefits</p>
          </div>
          <div class="partner-footer">
            <span class="badge" :class="p.is_active ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">
              {{ p.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()
const partners = ref([])
const total = ref(0)
const showForm = ref(false)
const photoFile = ref(null)
const newPartner = ref({ name: '', partner_type: 'ngo', contact_person: '', contact_phone: '', contact_email: '', district: '', region: '', registration_number: '' })

async function fetchPartners() {
  const { data } = await api.get('/partners/')
  partners.value = data.results ?? data
  total.value = data.count ?? data.length
}

function onPhotoChange(e) {
  photoFile.value = e.target.files[0]
}

async function createPartner() {
  const fd = new FormData()

  // Append all fields
  Object.keys(newPartner.value).forEach(key => {
    if (newPartner.value[key] !== null && newPartner.value[key] !== '') {
      fd.append(key, newPartner.value[key])
    }
  })

  // Append file separately
  if (photoFile.value) {
    fd.append('photo', photoFile.value)
  }

  try {
    await api.post('/partners/', fd, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    showForm.value = false

    // Reset form (important for UX)
    newPartner.value = {
      name: '',
      partner_type: 'ngo',
      contact_person: '',
      contact_phone: '',
      contact_email: '',
      district: '',
      region: '',
      registration_number: ''
    }
    photoFile.value = null

    await fetchPartners()
  } catch (err) {
    console.error(err.response?.data || err)
  }
}

onMounted(fetchPartners)
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
</style>
