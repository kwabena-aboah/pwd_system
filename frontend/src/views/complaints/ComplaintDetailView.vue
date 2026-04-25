<template>
  <div v-if="complaint">
    <div class="d-flex align-items-center gap-3 mb-4">
      <button class="btn btn-outline-secondary btn-sm" @click="router.back()"><i class="bi bi-arrow-left"></i></button>
      <div>
        <h1 class="page-title mb-0">{{ complaint.title }}</h1>
        <small class="text-muted">{{ complaint.complaint_number }}</small>
      </div>
      <div class="ms-auto d-flex gap-2">
        <span class="badge fs-6" :class="priorityBadge(complaint.priority)">{{ complaint.priority }}</span>
        <span class="badge fs-6" :class="statusBadge(complaint.status)">{{ complaint.status }}</span>
      </div>
    </div>
    <div class="row g-4">
      <div class="col-md-8">
        <div class="detail-card">
          <h6 class="mb-3 fw-bold"><i class="bi bi-file-text me-2 text-primary"></i>Description</h6>
          <p>{{ complaint.description }}</p>
          <hr>
          <div class="row g-2">
            <div class="col-6"><small class="text-muted d-block">Source</small><strong>{{ complaint.source }}</strong></div>
            <div class="col-6"><small class="text-muted d-block">Date Lodged</small><strong>{{ complaint.date_lodged }}</strong></div>
            <div class="col-6" v-if="complaint.pwd_name"><small class="text-muted d-block">PWD</small><strong>{{ complaint.pwd_name }}</strong></div>
            <div class="col-6" v-if="complaint.complainant_name"><small class="text-muted d-block">Complainant</small><strong>{{ complaint.complainant_name }}</strong></div>
          </div>
        </div>
        <!-- Notes -->
        <div class="detail-card mt-4">
          <h6 class="mb-3 fw-bold"><i class="bi bi-chat-left-dots me-2 text-primary"></i>Notes ({{ complaint.notes?.length || 0 }})</h6>
          <div v-for="n in complaint.notes" :key="n.id" class="note-item">
            <strong>{{ n.added_by_name }}</strong>
            <p>{{ n.note }}</p>
            <small class="text-muted">{{ new Date(n.created_at).toLocaleString() }}</small>
          </div>
          <div v-if="auth.canEdit" class="mt-3">
            <textarea v-model="newNote" class="form-control mb-2" rows="2" placeholder="Add a note..."></textarea>
            <button class="btn btn-sm btn-primary" @click="addNote"><i class="bi bi-plus me-1"></i>Add Note</button>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="detail-card">
          <h6 class="mb-3 fw-bold">Actions</h6>
          <div v-if="complaint.status === 'open'" class="mb-3">
            <label class="form-label small fw-semibold">Assign To</label>
            <select v-model="assignTo" class="form-select form-select-sm mb-2">
              <option v-for="u in users" :key="u.id" :value="u.id">{{ u.full_name }}</option>
            </select>
            <button class="btn btn-sm btn-outline-primary w-100" @click="assign">Assign</button>
          </div>
          <div v-if="complaint.status === 'in_progress'">
            <label class="form-label small fw-semibold">Resolution</label>
            <textarea v-model="resolution" class="form-control form-control-sm mb-2" rows="3"></textarea>
            <button class="btn btn-sm btn-success w-100" @click="resolve"><i class="bi bi-check-lg me-1"></i>Mark Resolved</button>
          </div>
          <div v-if="complaint.assigned_to_name" class="mt-3">
            <small class="text-muted">Assigned to</small>
            <div class="fw-semibold">{{ complaint.assigned_to_name }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
const router = useRouter(); const route = useRoute(); const auth = useAuthStore()
const complaint = ref(null); const users = ref([]); const newNote = ref(''); const assignTo = ref(null); const resolution = ref('')
const priorityBadge = p => ({ low: 'bg-secondary-subtle text-secondary', medium: 'bg-warning-subtle text-warning', high: 'bg-danger-subtle text-danger', urgent: 'bg-danger text-white' }[p] || '')
const statusBadge = s => ({ open: 'bg-danger-subtle text-danger', in_progress: 'bg-warning-subtle text-warning', resolved: 'bg-success-subtle text-success', closed: 'bg-secondary-subtle text-secondary' }[s] || '')
async function load() {
  const [c, u] = await Promise.all([api.get(`/complaints/${route.params.id}/`), api.get('/users/')])
  complaint.value = c.data; users.value = u.data.results ?? u.data
}
async function addNote() { await api.post(`/complaints/${route.params.id}/add-note/`, { note: newNote.value }); newNote.value = ''; load() }
async function assign() { await api.post(`/complaints/${route.params.id}/assign/`, { user_id: assignTo.value }); load() }
async function resolve() { await api.post(`/complaints/${route.params.id}/resolve/`, { resolution: resolution.value }); load() }
onMounted(load)
</script>
<style scoped>
.page-title { font-size: 1.4rem; font-weight: 800; }
.detail-card { background: white; border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); }
.note-item { padding: 10px 0; border-bottom: 1px solid var(--border); }
.note-item:last-child { border: none; }
.note-item p { margin: 4px 0; font-size: 0.875rem; }
</style>
