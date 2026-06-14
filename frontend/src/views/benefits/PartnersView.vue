<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Development Partners</h1>
        <p class="page-subtitle">{{ total }} partners registered</p>
      </div>
      <button class="btn btn-primary" @click="showForm = true" v-if="auth.canEdit">
        <i class="bi bi-plus-lg me-1"></i>Add Partner
      </button>
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

onMounted(async () => {
  const { data } = await api.get('/partners/')
  partners.value = data.results ?? data
  total.value = data.count ?? data.length
})
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
