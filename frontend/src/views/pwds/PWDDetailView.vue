<template>
  <div v-if="pwd" class="pwd-detail">
    <!-- Header Card -->
    <div class="detail-header-card">
      <button class="btn btn-sm btn-outline-secondary back-btn" @click="router.back()">
        <i class="bi bi-arrow-left me-1"></i><span class="d-none d-sm-inline">Back</span>
      </button>

      <div class="detail-identity">
        <div class="photo-wrap">
          <img v-if="pwd.photo" :src="pwd.photo" class="detail-photo" alt="">
          <div v-else class="detail-photo-placeholder"><i class="bi bi-person-fill"></i></div>
        </div>
        <div class="identity-info">
          <h1 class="detail-name">{{ pwd.first_name }} {{ pwd.last_name }}
            <span class="other-names" v-if="pwd.other_names">{{ pwd.other_names }}</span>
          </h1>
          <div class="identity-badges">
            <code class="reg-badge">{{ pwd.registration_number }}</code>
            <span class="badge" :class="statusBadge(pwd.status)">{{ pwd.status }}</span>
            <span class="badge" :class="riskBadge(pwd.ai_risk_label)" v-if="pwd.ai_risk_label">
              <i class="bi bi-robot me-1"></i>{{ pwd.ai_risk_label }} risk
            </span>
          </div>
          <div class="identity-meta">
            <span><i class="bi bi-calendar3 me-1"></i>{{ pwd.age }} years</span>
            <span><i class="bi bi-geo-alt me-1"></i>{{ pwd.community }}, {{ pwd.district }}</span>
            <span v-if="pwd.phone"><i class="bi bi-telephone me-1"></i>{{ pwd.phone }}</span>
          </div>
        </div>
      </div>

      <div class="detail-actions">
        <button class="btn btn-outline-info btn-sm" @click="generateAI" :disabled="aiLoading">
          <span v-if="aiLoading" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-robot me-1"></i>
          <span class="d-none d-sm-inline">{{ aiLoading ? 'Analysing…' : 'AI Analysis' }}</span>
        </button>
        <router-link :to="`/pwds/${pwd.id}/edit`" class="btn btn-primary btn-sm" v-if="auth.canEdit">
          <i class="bi bi-pencil me-1"></i><span class="d-none d-sm-inline">Edit</span>
        </router-link>
      </div>
    </div>

    <!-- Stats row -->
    <div class="detail-stats">
      <div class="dstat"><span class="dstat-val">{{ pwd.benefit_count }}</span><span class="dstat-lbl">Benefits</span></div>
      <div class="dstat"><span class="dstat-val">{{ pwd.complaint_count }}</span><span class="dstat-lbl">Complaints</span></div>
      <div class="dstat"><span class="dstat-val">{{ pwd.household_size || 1 }}</span><span class="dstat-lbl">Household</span></div>
      <div class="dstat" v-if="pwd.monthly_income"><span class="dstat-val">GHS{{ pwd.monthly_income }}</span><span class="dstat-lbl">Income</span></div>
    </div>

    <!-- Tabs -->
    <div class="tabs-wrap">
      <div class="tabs-scroll">
        <button v-for="tab in tabs" :key="tab.id" class="tab-btn"
          :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id">
          <i :class="['bi', tab.icon]"></i>
          <span>{{ tab.label }}</span>
        </button>
      </div>
    </div>

    <!-- Personal Tab -->
    <div v-if="activeTab === 'personal'" class="tab-content">
      <div class="info-grid">
        <InfoCard title="Personal Information" icon="bi-person-fill">
          <InfoRow label="Date of Birth" :value="pwd.date_of_birth" />
          <InfoRow label="Age" :value="pwd.age + ' years'" />
          <InfoRow label="Gender" :value="pwd.gender === 'M' ? 'Male' : pwd.gender === 'F' ? 'Female' : 'Other'" />
          <InfoRow label="Nationality" :value="pwd.nationality" />
          <InfoRow label="Marital Status" :value="pwd.marital_status" />
          <InfoRow label="National ID" :value="pwd.national_id || '—'" />
        </InfoCard>
        <InfoCard title="Contact & Location" icon="bi-geo-alt-fill">
          <InfoRow label="Phone" :value="pwd.phone || '—'" />
          <InfoRow label="Email" :value="pwd.email || '—'" />
          <InfoRow label="Digital Address" :value="pwd.digital_address || '—'" />
          <InfoRow label="Community" :value="pwd.community" />
          <InfoRow label="District" :value="pwd.district" />
          <InfoRow label="Region" :value="pwd.region" />
        </InfoCard>
        <InfoCard title="Socioeconomic" icon="bi-briefcase-fill">
          <InfoRow label="Education" :value="pwd.education_level" />
          <InfoRow label="Employment" :value="pwd.employment_status?.replace('_',' ')" />
          <InfoRow label="Occupation" :value="pwd.occupation || '—'" />
          <InfoRow label="Monthly Income" :value="pwd.monthly_income ? 'GHS ' + pwd.monthly_income : '—'" />
          <InfoRow label="Household Size" :value="pwd.household_size" />
        </InfoCard>
        <InfoCard title="Caregiver" icon="bi-people-fill">
          <InfoRow label="Name" :value="pwd.caregiver_name || '—'" />
          <InfoRow label="Phone" :value="pwd.caregiver_phone || '—'" />
          <InfoRow label="Relationship" :value="pwd.caregiver_relationship || '—'" />
        </InfoCard>
      </div>
    </div>

    <!-- Medical Tab -->
    <div v-if="activeTab === 'medical'" class="tab-content">
      <div v-if="!pwd.medical_records?.length" class="empty-state">
        <i class="bi bi-clipboard2-pulse"></i>
        <p>No medical record added yet.</p>
        <button class="btn btn-primary btn-sm" v-if="auth.canEdit">Add Medical Record</button>
      </div>
      <div v-else class="info-grid" v-for="med in pwd.medical_records" :key="med.id">
        <InfoCard title="Disability Details" icon="bi-accessibility">
          <InfoRow label="Disability Types" :value="med.disability_types?.map(d => d.name).join(', ')" />
          <InfoRow label="Severity" :value="med.disability_severity" />
          <InfoRow label="Onset" :value="med.disability_onset" />
          <InfoRow label="Cause" :value="med.cause_of_disability || '—'" />
        </InfoCard>
        <InfoCard title="Health Support" icon="bi-heart-pulse-fill">
          <InfoRow label="Assistive Device" :value="med.has_assistive_device ? (med.assistive_device_type || 'Yes') : 'No'" />
          <InfoRow label="Device Condition" :value="med.device_condition || '—'" />
          <InfoRow label="Health Insurance" :value="med.health_insurance ? 'Yes (NHIS: ' + (med.nhis_number || 'N/A') + ')' : 'No'" />
          <InfoRow label="Last Checkup" :value="med.last_medical_checkup || '—'" />
          <InfoRow label="Hospital/Facility" :value="med.hospital_facility || '—'" />
        </InfoCard>
      </div>
    </div>

    <!-- Benefits Tab -->
    <div v-if="activeTab === 'benefits'" class="tab-content">
      <div v-if="!allocations.length" class="empty-state">
        <i class="bi bi-gift"></i><p>No benefits recorded yet.</p>
      </div>
      <div class="cards-grid" v-else>
        <div class="benefit-item" v-for="a in allocations" :key="a.id">
          <div class="d-flex justify-content-between align-items-start">
            <strong class="benefit-name">{{ a.benefit_name }}</strong>
            <span class="badge" :class="allocBadge(a.status)">{{ a.status }}</span>
          </div>
          <p class="text-muted small mb-1">{{ a.partner_name }}</p>
          <div class="benefit-meta">
            <span v-if="a.amount_disbursed"><i class="bi bi-cash me-1"></i>GHS {{ a.amount_disbursed }}</span>
            <span><i class="bi bi-calendar3 me-1"></i>{{ a.allocation_date }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Complaints Tab -->
    <div v-if="activeTab === 'complaints'" class="tab-content">
      <div v-if="!complaints.length" class="empty-state">
        <i class="bi bi-chat-left-text"></i><p>No complaints recorded.</p>
      </div>
      <div class="complaints-list" v-else>
        <div class="complaint-item" v-for="c in complaints" :key="c.id" @click="router.push(`/complaints/${c.id}`)">
          <div class="d-flex justify-content-between align-items-start gap-2">
            <strong>{{ c.title }}</strong>
            <div class="d-flex gap-1 flex-shrink-0">
              <span class="badge" :class="priorityBadge(c.priority)">{{ c.priority }}</span>
              <span class="badge" :class="statusBadge(c.status)">{{ c.status }}</span>
            </div>
          </div>
          <p class="text-muted small mt-1 mb-0">{{ c.complaint_number }} · {{ c.date_lodged }}</p>
        </div>
      </div>
    </div>

    <!-- AI Tab -->
    <div v-if="activeTab === 'ai'" class="tab-content">
      <div v-if="pwd.ai_summary" class="ai-panel">
        <div class="ai-header">
          <div class="ai-robot-icon"><i class="bi bi-robot"></i></div>
          <div>
            <h5>AI Profile Analysis</h5>
            <small class="text-muted">Powered by GPT-4o-mini</small>
          </div>
          <div class="ms-auto">
            <span class="risk-score-badge" :class="riskBadge(pwd.ai_risk_label)">
              Score: {{ pwd.ai_risk_score?.toFixed(0) }}/100
            </span>
          </div>
        </div>
        <div class="ai-section"><h6><i class="bi bi-file-text me-2"></i>Summary</h6><p>{{ pwd.ai_summary }}</p></div>
        <div class="ai-section" v-if="pwd.ai_recommendations">
          <h6><i class="bi bi-lightbulb me-2"></i>Recommendations</h6>
          <ul>
            <li v-for="(rec, i) in pwd.ai_recommendations.split('\n').filter(r => r.trim())" :key="i">{{ rec }}</li>
          </ul>
        </div>
      </div>
      <div v-else class="empty-state">
        <i class="bi bi-robot"></i>
        <p>No AI analysis generated yet.</p>
        <button class="btn btn-primary btn-sm" @click="generateAI" :disabled="aiLoading">
          <span v-if="aiLoading" class="spinner-border spinner-border-sm me-1"></span>
          Run AI Analysis
        </button>
      </div>
    </div>

    <!-- Documents Tab -->
    <div v-if="activeTab === 'documents'" class="tab-content">
      <div v-if="!pwd.documents?.length" class="empty-state">
        <i class="bi bi-folder2-open"></i><p>No documents uploaded.</p>
      </div>
      <div class="cards-grid" v-else>
        <div class="doc-item" v-for="doc in pwd.documents" :key="doc.id">
          <i class="bi bi-file-earmark-text-fill text-primary fs-2"></i>
          <div class="flex-1 min-width-0">
            <strong class="d-block">{{ doc.title }}</strong>
            <small class="text-muted">{{ doc.doc_type }} · {{ doc.uploaded_at?.slice(0,10) }}</small>
          </div>
          <a :href="doc.file" target="_blank" class="btn btn-sm btn-outline-primary flex-shrink-0">
            <i class="bi bi-download"></i>
          </a>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="text-center py-5">
    <div class="spinner-border" style="color:var(--system-primary)"></div>
    <p class="mt-2 text-muted">Loading record…</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import InfoCard from '@/components/InfoCard.vue'
import InfoRow from '@/components/InfoRow.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const pwd = ref(null)
const allocations = ref([])
const complaints = ref([])
const activeTab = ref('personal')
const aiLoading = ref(false)

const tabs = [
  { id: 'personal', label: 'Personal', icon: 'bi-person-fill' },
  { id: 'medical', label: 'Medical', icon: 'bi-clipboard2-pulse' },
  { id: 'benefits', label: 'Benefits', icon: 'bi-gift-fill' },
  { id: 'complaints', label: 'Complaints', icon: 'bi-chat-left-text' },
  { id: 'ai', label: 'AI', icon: 'bi-robot' },
  { id: 'documents', label: 'Docs', icon: 'bi-folder2-open' },
]

const statusBadge = s => ({ active:'bg-success-subtle text-success', deceased:'bg-dark text-white', relocated:'bg-info-subtle text-info', inactive:'bg-secondary-subtle text-secondary' }[s] || 'bg-secondary-subtle text-secondary')
const riskBadge = l => ({ low:'bg-success-subtle text-success', medium:'bg-warning-subtle text-warning', high:'bg-danger-subtle text-danger', critical:'bg-danger text-white' }[l] || 'bg-secondary-subtle text-secondary')
const allocBadge = s => ({ disbursed:'bg-success-subtle text-success', approved:'bg-info-subtle text-info', pending:'bg-warning-subtle text-warning', rejected:'bg-danger-subtle text-danger' }[s] || 'bg-secondary-subtle text-secondary')
const priorityBadge = p => ({ low:'bg-secondary-subtle text-secondary', medium:'bg-warning-subtle text-warning', high:'bg-danger-subtle text-danger', urgent:'bg-danger text-white' }[p] || '')

async function loadPWD() {
  const { data } = await api.get(`/pwds/${route.params.id}/`)
  pwd.value = data
  const [ab, cb] = await Promise.all([
    api.get('/benefit-allocations/', { params: { pwd: data.id } }),
    api.get('/complaints/', { params: { pwd: data.id } }),
  ])
  allocations.value = ab.data.results ?? ab.data
  complaints.value = cb.data.results ?? cb.data
}

async function generateAI() {
  aiLoading.value = true
  try {
    await api.post(`/pwds/${route.params.id}/generate-ai-summary/`)
    await loadPWD()
    activeTab.value = 'ai'
  } finally { aiLoading.value = false }
}

onMounted(loadPWD)
</script>

<style scoped>
.detail-header-card {
  background: white; border-radius: var(--radius); padding: 20px 24px;
  margin-bottom: 14px; box-shadow: var(--shadow);
  display: flex; align-items: flex-start; gap: 16px; flex-wrap: wrap;
}
.back-btn { flex-shrink: 0; }
.detail-identity { display: flex; align-items: flex-start; gap: 16px; flex: 1; min-width: 0; flex-wrap: wrap; }
.photo-wrap { flex-shrink: 0; }
.detail-photo { width: 76px; height: 76px; border-radius: 50%; object-fit: cover; }
.detail-photo-placeholder {
  width: 76px; height: 76px; border-radius: 50%;
  background: linear-gradient(135deg, var(--system-primary), #7e3af2);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.8rem; color: rgba(255,255,255,0.7);
}
.identity-info { flex: 1; min-width: 0; }
.detail-name { font-size: clamp(1.1rem, 2.5vw, 1.4rem); font-weight: 800; margin-bottom: 8px; }
.other-names { font-weight: 400; color: var(--text-secondary); font-size: 0.9em; }
.identity-badges { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.reg-badge { font-size: 0.78rem; color: var(--system-primary); background: #eff6ff; padding: 3px 8px; border-radius: 5px; }
.identity-meta { display: flex; gap: 12px; flex-wrap: wrap; }
.identity-meta span { font-size: 0.8rem; color: var(--text-secondary); }
.detail-actions { display: flex; gap: 8px; flex-shrink: 0; align-self: flex-start; }

.detail-stats {
  display: flex; gap: 12px; margin-bottom: 14px; flex-wrap: wrap;
}
.dstat {
  background: white; border-radius: var(--radius-sm); padding: 12px 20px;
  box-shadow: var(--shadow); display: flex; flex-direction: column; align-items: center;
  min-width: 80px; flex: 1;
}
.dstat-val { font-size: 1.4rem; font-weight: 800; color: var(--system-primary); line-height: 1; }
.dstat-lbl { font-size: 0.72rem; color: var(--text-secondary); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.04em; }

.tabs-wrap { background: white; border-radius: var(--radius); box-shadow: var(--shadow); margin-bottom: 16px; overflow: hidden; }
.tabs-scroll { display: flex; overflow-x: auto; -webkit-overflow-scrolling: touch; }
.tabs-scroll::-webkit-scrollbar { display: none; }
.tab-btn {
  display: flex; align-items: center; gap: 6px; padding: 13px 18px;
  background: none; border: none; border-bottom: 2px solid transparent;
  color: var(--text-secondary); font-size: 0.85rem; font-weight: 500;
  cursor: pointer; white-space: nowrap; transition: color 0.15s, border-color 0.15s;
}
.tab-btn:hover { color: var(--text-primary); }
.tab-btn.active { color: var(--system-primary); border-bottom-color: var(--system-primary); }
.tab-btn i { font-size: 0.95rem; }

.tab-content { animation: fadeUp 0.18s ease; }
@keyframes fadeUp { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

.info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
@media (max-width: 768px) { .info-grid { grid-template-columns: 1fr; } }

.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }

.benefit-item {
  background: white; border-radius: var(--radius); padding: 16px; box-shadow: var(--shadow);
}
.benefit-name { font-size: 0.9rem; display: block; margin-bottom: 3px; }
.benefit-meta { display: flex; gap: 12px; font-size: 0.78rem; color: var(--text-secondary); margin-top: 8px; }

.complaints-list { display: flex; flex-direction: column; gap: 10px; }
.complaint-item {
  background: white; border-radius: var(--radius); padding: 14px 18px;
  box-shadow: var(--shadow); cursor: pointer; transition: box-shadow 0.15s;
}
.complaint-item:hover { box-shadow: var(--shadow-md); }

.ai-panel { background: white; border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow); }
.ai-header { display: flex; align-items: center; gap: 14px; margin-bottom: 22px; padding-bottom: 16px; border-bottom: 1px solid var(--border); flex-wrap: wrap; }
.ai-robot-icon { width: 48px; height: 48px; border-radius: 12px; background: #eff6ff; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; color: var(--system-primary); flex-shrink: 0; }
.ai-header h5 { margin: 0; font-size: 1rem; font-weight: 700; }
.risk-score-badge { padding: 6px 14px; border-radius: 20px; font-size: 0.82rem; font-weight: 700; }
.ai-section { margin-bottom: 18px; }
.ai-section h6 { font-weight: 700; margin-bottom: 8px; font-size: 0.9rem; }
.ai-section ul { padding-left: 20px; }
.ai-section li { margin-bottom: 5px; font-size: 0.875rem; }

.doc-item { background: white; border-radius: var(--radius); padding: 14px 16px; box-shadow: var(--shadow); display: flex; align-items: center; gap: 12px; }
</style>
