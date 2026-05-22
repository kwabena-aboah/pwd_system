<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">User Management</h1>
      <button class="btn btn-primary" @click="showForm = true"><i class="bi bi-plus-lg me-1"></i>Add User</button>
    </div>

    <!-- Add User Modal -->
    <div class="modal-overlay" v-if="showForm" @click.self="showForm = false">
      <div class="modal-box">
        <h5 class="mb-3">Add New User</h5>
        <div class="row g-3">
          <div class="col-6"><label class="form-label">First Name</label><input v-model="newUser.first_name" class="form-control"></div>
          <div class="col-6"><label class="form-label">Last Name</label><input v-model="newUser.last_name" class="form-control"></div>
          <div class="col-6"><label class="form-label">Username</label><input v-model="newUser.username" class="form-control"></div>
          <div class="col-6"><label class="form-label">Email</label><input v-model="newUser.email" type="email" class="form-control"></div>
          <div class="col-6"><label class="form-label">Role</label>
            <select v-model="newUser.role" class="form-select">
              <option value="district_officer">District Officer</option>
              <option value="data_entry">Data Entry Officer</option>
              <option value="social_worker">Social Worker</option>
              <option value="ngo_partner">NGO Partner</option>
              <option value="govt_officer">Government Officer</option>
              <option value="auditor">Auditor</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>
          <div class="col-6"><label class="form-label">District</label><input v-model="newUser.district" class="form-control"></div>
          <div class="col-12"><label class="form-label">Password</label><input v-model="newUser.password" type="password" class="form-control"></div>
        </div>
        <div class="d-flex justify-content-end gap-2 mt-3">
          <button class="btn btn-outline-secondary" @click="showForm = false">Cancel</button>
          <button class="btn btn-primary" @click="createUser">Create User</button>
        </div>
      </div>
    </div>

    <div class="table-card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>District</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td><strong>{{ u.full_name }}</strong></td>
              <td>{{ u.email }}</td>
              <td><span class="badge bg-primary-subtle text-primary">{{ u.role?.replace('_', ' ') }}</span></td>
              <td>{{ u.district || '—' }}</td>
              <td><span class="badge" :class="u.is_active ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">{{ u.is_active ? 'Active' : 'Inactive' }}</span></td>
              <td>
                <button class="btn btn-sm btn-outline-danger" @click="toggleActive(u)">
                  {{ u.is_active ? 'Deactivate' : 'Activate' }}
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
import { ref, onMounted } from 'vue'
import api from '@/services/api'
const users = ref([])
const showForm = ref(false)
const newUser = ref({ first_name: '', last_name: '', username: '', email: '', role: 'data_entry', district: '', password: '' })
async function fetchUsers() {
  const { data } = await api.get('/users/')
  users.value = data.results ?? data
}
async function createUser() {
  await api.post('/users/', newUser.value)
  showForm.value = false
  fetchUsers()
}
async function toggleActive(u) {
  await api.patch(`/users/${u.id}/`, { is_active: !u.is_active })
  fetchUsers()
}
onMounted(fetchUsers)
</script>
<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title { font-size: 1.75rem; font-weight: 800; }
.table-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.table thead th { background: var(--surface-secondary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-secondary); padding: 12px 16px; }
.table tbody td { padding: 12px 16px; font-size: 0.875rem; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center; }
.modal-box { background: white; border-radius: 16px; padding: 28px; width: 100%; max-width: 500px; box-shadow: var(--shadow-lg); }
</style>
