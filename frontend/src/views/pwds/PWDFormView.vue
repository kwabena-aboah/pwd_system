<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ isEdit ? 'Edit PWD Record' : 'Register New PWD' }}</h1>
        <p class="page-subtitle">Step {{ currentStep + 1 }} of {{ steps.length }}: {{ steps[currentStep] }}</p>
      </div>
      <button class="btn btn-outline-secondary btn-sm" @click="router.back()">
        <i class="bi bi-arrow-left me-1"></i>Cancel
      </button>
    </div>

    <!-- Step progress -->
    <div class="step-progress">
      <div v-for="(s, i) in steps" :key="i" class="step-item"
        :class="{ active: i === currentStep, done: i < currentStep }" @click="i < currentStep && (currentStep = i)">
        <div class="step-circle">
          <i v-if="i < currentStep" class="bi bi-check-lg"></i>
          <span v-else>{{ i + 1 }}</span>
        </div>
        <span class="step-name">{{ s }}</span>
      </div>
    </div>

    <!-- Step 0: Personal Info -->
    <div v-if="currentStep === 0" class="form-section">
      <div class="form-section-title"><i class="bi bi-person-fill me-2"></i>Personal Information</div>
      <div class="form-grid">
        <div class="fg-span-2">
          <label class="form-label">Profile Photo</label>
          <div class="photo-upload">
            <div class="photo-preview">
              <img v-if="previewUrl" :src="previewUrl" alt="Preview">
              <i v-else class="bi bi-person-fill text-muted fs-2"></i>
            </div>
            <div>
              <input type="file" id="photo-input" class="d-none" accept="image/*" @change="onPhotoChange">
              <label for="photo-input" class="btn btn-sm btn-outline-secondary"><i class="bi bi-camera me-1"></i>Upload Photo</label>
              <p class="text-muted small mt-1">JPG, PNG. Max 5MB</p>
            </div>
          </div>
        </div>
        <div>
          <label class="form-label required">First Name</label>
          <input v-model="form.first_name" type="text" class="form-control" required>
        </div>
        <div>
          <label class="form-label required">Last Name</label>
          <input v-model="form.last_name" type="text" class="form-control" required>
        </div>
        <div>
          <label class="form-label">Other Names</label>
          <input v-model="form.other_names" type="text" class="form-control">
        </div>
        <div>
          <label class="form-label required">Date of Birth</label>
          <input v-model="form.date_of_birth" type="date" class="form-control" required>
        </div>
        <div>
          <label class="form-label required">Gender</label>
          <select v-model="form.gender" class="form-select" required>
            <option value="M">Male</option>
            <option value="F">Female</option>
            <option value="O">Other</option>
          </select>
        </div>
        <div>
          <label class="form-label">Marital Status</label>
          <select v-model="form.marital_status" class="form-select">
            <option value="single">Single</option>
            <option value="married">Married</option>
            <option value="divorced">Divorced</option>
            <option value="widowed">Widowed</option>
          </select>
        </div>
        <div>
          <label class="form-label">National ID Type</label>
          <select v-model="form.national_id_type" class="form-select">
            <option value="ghana_card">Ghana Card</option>
            <option value="passport">Passport</option>
            <option value="nhis">NHIS Card</option>
            <option value="voter_id">Voter ID</option>
          </select>
        </div>
        <div>
          <label class="form-label">National ID Number</label>
          <input v-model="form.national_id" type="text" class="form-control">
        </div>
      </div>
    </div>

    <!-- Step 1: Contact -->
    <div v-if="currentStep === 1" class="form-section">
      <div class="form-section-title"><i class="bi bi-geo-alt-fill me-2"></i>Contact & Location</div>
      <div class="form-grid">
        <div>
          <label class="form-label">Phone Number</label>
          <input v-model="form.phone" type="tel" class="form-control" placeholder="0XX XXX XXXX">
        </div>
        <div>
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-control">
        </div>
        <div>
          <label class="form-label">Digital Address (GPS)</label>
          <input v-model="form.digital_address" type="text" class="form-control" placeholder="XX-000-0000">
        </div>
        <div>
          <label class="form-label">House Number</label>
          <input v-model="form.house_number" type="text" class="form-control">
        </div>
        <div>
          <label class="form-label">Street</label>
          <input v-model="form.street" type="text" class="form-control">
        </div>
        <div>
          <label class="form-label required">Community</label>
          <input v-model="form.community" type="text" class="form-control" required>
        </div>
        <div>
          <label class="form-label">Sub-District</label>
          <input v-model="form.sub_district" type="text" class="form-control">
        </div>
        <div>
          <label class="form-label required">District</label>
          <input v-model="form.district" type="text" class="form-control" required>
        </div>
        <div class="fg-span-2">
          <label class="form-label required">Region</label>
          <select v-model="form.region" class="form-select" required>
            <option v-for="r in ghanaRegions" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Step 2: Socioeconomic -->
    <div v-if="currentStep === 2" class="form-section">
      <div class="form-section-title"><i class="bi bi-briefcase-fill me-2"></i>Socioeconomic Details</div>
      <div class="form-grid">
        <div>
          <label class="form-label">Education Level</label>
          <select v-model="form.education_level" class="form-select">
            <option value="none">None</option>
            <option value="primary">Primary</option>
            <option value="jhs">JHS</option>
            <option value="shs">SHS</option>
            <option value="tertiary">Tertiary</option>
            <option value="vocational">Vocational</option>
          </select>
        </div>
        <div>
          <label class="form-label">Employment Status</label>
          <select v-model="form.employment_status" class="form-select">
            <option value="unemployed">Unemployed</option>
            <option value="employed">Employed</option>
            <option value="self_employed">Self Employed</option>
            <option value="student">Student</option>
            <option value="retired">Retired</option>
          </select>
        </div>
        <div>
          <label class="form-label">Occupation</label>
          <input v-model="form.occupation" type="text" class="form-control">
        </div>
        <div>
          <label class="form-label">Monthly Income (GHS)</label>
          <input v-model="form.monthly_income" type="number" class="form-control" step="0.01" min="0">
        </div>
        <div>
          <label class="form-label">Household Size</label>
          <input v-model="form.household_size" type="number" class="form-control" min="1">
        </div>
      </div>
      <div class="form-section-title mt-4"><i class="bi bi-people me-2"></i>Caregiver Information</div>
      <div class="form-grid">
        <div>
          <label class="form-label">Caregiver Name</label>
          <input v-model="form.caregiver_name" type="text" class="form-control">
        </div>
        <div>
          <label class="form-label">Caregiver Phone</label>
          <input v-model="form.caregiver_phone" type="tel" class="form-control">
        </div>
        <div>
          <label class="form-label">Relationship</label>
          <input v-model="form.caregiver_relationship" type="text" class="form-control" placeholder="e.g. Parent, Spouse">
        </div>
      </div>
    </div>

    <!-- Nav Buttons -->
    <div class="form-nav">
      <button type="button" class="btn btn-outline-secondary" @click="currentStep--" v-if="currentStep > 0">
        <i class="bi bi-arrow-left me-1"></i>Previous
      </button>
      <button type="button" class="btn btn-primary ms-auto" @click="currentStep++" v-if="currentStep < steps.length - 1">
        Next<i class="bi bi-arrow-right ms-1"></i>
      </button>
      <button type="button" class="btn btn-success ms-auto" v-else @click="submitForm" :disabled="saving">
        <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-check-lg me-1"></i>
        {{ isEdit ? 'Save Changes' : 'Register PWD' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const isEdit = computed(() => !!route.params.id && !route.path.endsWith('/new'))
const currentStep = ref(0)
const saving = ref(false)
const photoFile = ref(null)
const previewUrl = ref(null)
const steps = ['Personal Info', 'Contact & Location', 'Socioeconomic']
const ghanaRegions = ['Ahafo','Ashanti','Bono','Bono East','Central','Eastern','Greater Accra','North East','Northern','Oti','Savannah','Upper East','Upper West','Volta','Western','Western North']

const form = ref({
  first_name:'', last_name:'', other_names:'', date_of_birth:'',
  gender:'M', marital_status:'single', nationality:'Ghanaian',
  national_id:'', national_id_type:'ghana_card',
  phone:'', email:'', digital_address:'', house_number:'', street:'',
  community:'', sub_district:'', district:'', region:'Greater Accra',
  education_level:'primary', employment_status:'unemployed',
  occupation:'', monthly_income:'', household_size:1,
  caregiver_name:'', caregiver_phone:'', caregiver_relationship:'',
  status:'active',
})

function onPhotoChange(e) {
  photoFile.value = e.target.files[0]
  previewUrl.value = URL.createObjectURL(photoFile.value)
}

async function submitForm() {
  saving.value = true
  try {
    const fd = new FormData()
    Object.entries(form.value).forEach(([k,v]) => { if (v !== '' && v !== null && v !== undefined) fd.append(k, v) })
    if (photoFile.value) fd.append('photo', photoFile.value)
    const cfg = { headers: { 'Content-Type': 'multipart/form-data' } }
    if (isEdit.value) {
      await api.patch(`/pwds/${route.params.id}/`, fd, cfg)
      router.push(`/pwds/${route.params.id}`)
    } else {
      const { data } = await api.post('/pwds/', fd, cfg)
      router.push(`/pwds/${data.id}`)
    }
  } finally { saving.value = false }
}

onMounted(async () => {
  if (isEdit.value) {
    const { data } = await api.get(`/pwds/${route.params.id}/`)
    Object.assign(form.value, data)
    if (data.photo) previewUrl.value = data.photo
  }
})
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; gap: 12px; flex-wrap: wrap; }
.page-title { font-size: clamp(1.2rem,3vw,1.6rem); font-weight: 800; }
.page-subtitle { color: var(--text-secondary); font-size: 0.875rem; }

.step-progress {
  display: flex; align-items: center; background: white;
  border-radius: var(--radius); padding: 16px 20px;
  box-shadow: var(--shadow); margin-bottom: 18px; gap: 0;
  overflow-x: auto; -webkit-overflow-scrolling: touch;
}
.step-item {
  display: flex; align-items: center; gap: 8px; cursor: default;
  padding: 4px 12px; white-space: nowrap;
}
.step-item.done { cursor: pointer; }
.step-item + .step-item::before { content: ''; display: block; width: 24px; height: 1px; background: var(--border); margin-right: 12px; flex-shrink: 0; }
.step-circle {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--border); display: flex; align-items: center;
  justify-content: center; font-size: 0.78rem; font-weight: 700;
  color: var(--text-secondary); flex-shrink: 0;
}
.step-item.active .step-circle { background: var(--system-primary); color: white; }
.step-item.done .step-circle { background: #10b981; color: white; }
.step-name { font-size: 0.845rem; font-weight: 500; color: var(--text-secondary); }
.step-item.active .step-name { color: var(--system-primary); font-weight: 700; }

.form-section { background: white; border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow); margin-bottom: 16px; }
.form-section-title { font-size: 0.92rem; font-weight: 700; margin-bottom: 18px; display: flex; align-items: center; color: var(--text-primary); }
.form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.fg-span-2 { grid-column: 1 / -1; }
@media (max-width: 640px) { .form-grid { grid-template-columns: 1fr; } .fg-span-2 { grid-column: auto; } }

.photo-upload { display: flex; align-items: center; gap: 16px; }
.photo-preview { width: 72px; height: 72px; border-radius: 50%; background: var(--surface-secondary); border: 2px dashed var(--border); display: flex; align-items: center; justify-content: center; overflow: hidden; flex-shrink: 0; }
.photo-preview img { width: 100%; height: 100%; object-fit: cover; }

.form-label.required::after { content: ' *'; color: #ef4444; }

.form-nav { display: flex; align-items: center; padding: 4px 0; gap: 12px; }
</style>
