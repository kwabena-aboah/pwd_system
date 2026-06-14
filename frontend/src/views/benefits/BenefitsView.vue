<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Benefit Programmes</h1>
      <button class="btn btn-primary" v-if="auth.canEdit" @click="showForm = true">
        <i class="bi bi-plus-lg me-1"></i>Add Benefit
      </button>
    </div>
    <div class="table-card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
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
              <td><span class="badge bg-primary-subtle text-primary">{{ b.allocation_count }}</span></td>
              <td><span class="badge" :class="b.status === 'active' ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary'">{{ b.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
const auth = useAuthStore()
const benefits = ref([])
const showForm = ref(false)
onMounted(async () => {
  const { data } = await api.get('/benefits/')
  benefits.value = data.results ?? data
})
</script>
<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.table-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.table thead th { background: var(--surface-secondary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); padding: 12px 16px; }
.table tbody td { padding: 12px 16px; font-size: 0.875rem; }
</style>
