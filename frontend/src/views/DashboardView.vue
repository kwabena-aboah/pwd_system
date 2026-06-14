<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">{{ settingsStore.settings.district_name || 'District' }} — PWD Overview</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="refreshStats" :disabled="loading">
        <i class="bi bi-arrow-clockwise me-1" :class="{ spin: loading }"></i>
        <span class="d-none d-sm-inline">Refresh</span>
      </button>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <KpiCard icon="bi-people-fill" color="primary" :value="stats.total" label="Total PWDs" />
      <KpiCard icon="bi-check-circle-fill" color="success" :value="stats.active" label="Active Records" />
      <KpiCard icon="bi-exclamation-triangle-fill" color="danger" :value="stats.high_risk" label="High Risk" />
      <KpiCard icon="bi-gift-fill" color="warning" :value="benefitStats.disbursed_count" label="Benefits Disbursed" />
      <KpiCard icon="bi-building-fill" color="info" :value="partnerCount" label="Dev. Partners" />
      <KpiCard icon="bi-chat-left-text-fill" color="secondary" :value="openComplaints" label="Open Complaints" />
    </div>

    <!-- Charts Row 1 -->
    <div class="charts-row-main">
      <div class="chart-card chart-wide">
        <div class="chart-card-header">
          <h3>Monthly Registrations</h3>
          <span class="badge bg-primary-subtle text-primary">Last 12 months</span>
        </div>
        <div class="chart-wrap">
          <Bar v-if="monthlyData.labels?.length" :data="monthlyData" :options="barOptions" />
          <div v-else class="chart-loading"><i class="bi bi-hourglass-split spin"></i></div>
        </div>
      </div>
      <div class="chart-card chart-narrow">
        <div class="chart-card-header"><h3>Disability Types</h3></div>
        <div class="chart-wrap chart-wrap-doughnut">
          <Doughnut v-if="disabilityData.labels?.length" :data="disabilityData" :options="doughnutOptions" />
          <div v-else class="chart-loading"><i class="bi bi-hourglass-split spin"></i></div>
        </div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="charts-row-three">
      <div class="chart-card">
        <div class="chart-card-header"><h3>Gender</h3></div>
        <div class="chart-wrap chart-wrap-sm">
          <Pie v-if="genderData.labels?.length" :data="genderData" :options="doughnutOptions" />
          <div v-else class="chart-loading"><i class="bi bi-hourglass-split spin"></i></div>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header"><h3>AI Risk Levels</h3></div>
        <div class="chart-wrap chart-wrap-sm">
          <Doughnut v-if="riskData.labels?.length" :data="riskData" :options="doughnutOptions" />
          <div v-else class="chart-loading"><i class="bi bi-hourglass-split spin"></i></div>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header"><h3>Employment Status</h3></div>
        <div class="chart-wrap chart-wrap-sm">
          <Bar v-if="employmentData.labels?.length" :data="employmentData" :options="hBarOptions" />
          <div v-else class="chart-loading"><i class="bi bi-hourglass-split spin"></i></div>
        </div>
      </div>
    </div>

    <!-- Bottom Row -->
    <div class="bottom-row">
      <div class="table-card bottom-card">
        <div class="chart-card-header">
          <h3>Top Districts</h3>
          <span class="badge bg-secondary-subtle text-secondary">by registered PWDs</span>
        </div>
        <div class="table-responsive">
          <table class="table mb-0">
            <tbody>
              <tr v-for="d in stats.by_district" :key="d.district">
                <td class="fw-semibold">{{ d.district || 'Unknown' }}</td>
                <td class="text-end"><strong>{{ d.count }}</strong></td>
                <td style="width:120px">
                  <div class="progress" style="height:6px">
                    <div class="progress-bar" :style="{ width: ((d.count / stats.total) * 100) + '%', background: 'var(--system-primary)' }"></div>
                  </div>
                </td>
                <td class="text-muted text-end small">{{ Math.round((d.count / (stats.total || 1)) * 100) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="table-card bottom-card">
        <div class="chart-card-header">
          <h3>Recent Registrations</h3>
          <router-link to="/pwds" class="btn btn-sm btn-outline-primary">View all</router-link>
        </div>
        <div v-for="p in recentPwds" :key="p.id" class="pwd-mini-row" @click="router.push(`/pwds/${p.id}`)">
          <img v-if="p.photo" :src="p.photo" class="pwd-mini-photo" :alt="p.first_name">
          <div v-else class="pwd-mini-initials">{{ p.first_name[0] }}{{ p.last_name[0] }}</div>
          <div class="pwd-mini-info">
            <strong>{{ p.first_name }} {{ p.last_name }}</strong>
            <small>{{ p.registration_number }} · {{ p.community }}</small>
          </div>
          <span class="badge" :class="riskBadge(p.ai_risk_label)">{{ p.ai_risk_label || '—' }}</span>
        </div>
        <div v-if="!recentPwds.length && !loading" class="text-center py-4 text-muted small">No records yet</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Bar, Doughnut, Pie } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  ArcElement, Tooltip, Legend
} from 'chart.js'
import KpiCard from '@/components/KpiCard.vue'
import { useSettingsStore } from '@/stores/settings'
import api from '@/services/api'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const router = useRouter()
const settingsStore = useSettingsStore()
const loading = ref(false)

const stats = ref({ total: 0, active: 0, high_risk: 0, by_district: [], monthly_registrations: [], by_disability_type: [], by_gender: [], by_risk: [], by_employment: [] })
const benefitStats = ref({ disbursed_count: 0 })
const partnerCount = ref(0)
const openComplaints = ref(0)
const recentPwds = ref([])

const PRIMARY = '#1a56db'
const COLORS = ['#1a56db','#7e3af2','#0ea5e9','#10b981','#f59e0b','#ef4444','#ec4899','#14b8a6','#f97316','#8b5cf6']

const monthlyData = computed(() => {
  const items = stats.value.monthly_registrations || []
  if (!items.length) return {}
  return {
    labels: items.map(i => { const d = new Date(i.month); return d.toLocaleString('default', { month: 'short', year: '2-digit' }) }),
    datasets: [{ label: 'Registrations', data: items.map(i => i.count), backgroundColor: PRIMARY + 'bb', borderColor: PRIMARY, borderWidth: 2, borderRadius: 5, borderSkipped: false }]
  }
})

const disabilityData = computed(() => {
  const items = stats.value.by_disability_type || []
  if (!items.length) return {}
  return { labels: items.map(i => i.name), datasets: [{ data: items.map(i => i.count), backgroundColor: COLORS, borderWidth: 0 }] }
})

const genderData = computed(() => {
  const items = stats.value.by_gender || []
  if (!items.length) return {}
  const labels = { M: 'Male', F: 'Female', O: 'Other' }
  return { labels: items.map(i => labels[i.gender] || i.gender), datasets: [{ data: items.map(i => i.count), backgroundColor: ['#1a56db','#ec4899','#10b981'], borderWidth: 0 }] }
})

const riskData = computed(() => {
  const items = stats.value.by_risk || []
  if (!items.length) return {}
  const colors = { low: '#10b981', medium: '#f59e0b', high: '#ef4444', critical: '#7c2d12', '': '#94a3b8' }
  return { labels: items.map(i => i.ai_risk_label || 'Not rated'), datasets: [{ data: items.map(i => i.count), backgroundColor: items.map(i => colors[i.ai_risk_label] || '#94a3b8'), borderWidth: 0 }] }
})

const employmentData = computed(() => {
  const items = stats.value.by_employment || []
  if (!items.length) return {}
  return { labels: items.map(i => i.employment_status?.replace('_', ' ')), datasets: [{ data: items.map(i => i.count), backgroundColor: COLORS, borderRadius: 4 }] }
})

const baseOpts = { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } } }
const barOptions = { ...baseOpts, scales: { y: { beginAtZero: true, grid: { color: '#f1f5f9' }, ticks: { font: { size: 11 } } }, x: { grid: { display: false }, ticks: { font: { size: 10 } } } } }
const doughnutOptions = { ...baseOpts, cutout: '62%', plugins: { legend: { display: true, position: 'bottom', labels: { font: { size: 11 }, padding: 10, boxWidth: 10 } } } }
const hBarOptions = { ...barOptions, indexAxis: 'y', scales: { ...barOptions.scales, y: { grid: { display: false }, ticks: { font: { size: 10 } } } } }

function riskBadge(label) {
  return { low: 'bg-success-subtle text-success', medium: 'bg-warning-subtle text-warning', high: 'bg-danger-subtle text-danger', critical: 'bg-danger text-white' }[label] || 'bg-secondary-subtle text-secondary'
}

async function refreshStats() {
  loading.value = true
  try {
    const [s, r, p, c, b] = await Promise.all([
      api.get('/pwds/statistics/'),
      api.get('/pwds/', { params: { ordering: '-registration_date', page_size: 6 } }),
      api.get('/partners/', { params: { page_size: 1 } }),
      api.get('/complaints/', { params: { status: 'open', page_size: 1 } }),
      api.get('/benefits/statistics/'),
    ])
    stats.value = s.data
    recentPwds.value = r.data.results ?? r.data
    partnerCount.value = p.data.count ?? 0
    openComplaints.value = c.data.count ?? 0
    benefitStats.value = b.data
  } catch {} finally { loading.value = false }
}

onMounted(refreshStats)
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px; margin-bottom: 20px;
}
@media (max-width: 1400px) { .kpi-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; } }
@media (max-width: 400px) { .kpi-grid { grid-template-columns: 1fr; } }

.charts-row-main {
  display: grid; grid-template-columns: 2fr 1fr;
  gap: 16px; margin-bottom: 16px;
}
@media (max-width: 900px) { .charts-row-main { grid-template-columns: 1fr; } }

.charts-row-three {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 16px; margin-bottom: 16px;
}
@media (max-width: 1024px) { .charts-row-three { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 640px) { .charts-row-three { grid-template-columns: 1fr; } }

.bottom-row {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 900px) { .bottom-row { grid-template-columns: 1fr; } }

.chart-card {
  background: white; border-radius: var(--radius);
  padding: 18px; box-shadow: var(--shadow);
}
.chart-card-header {
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 14px;
}
.chart-card-header h3 { font-size: 0.9rem; font-weight: 700; margin: 0; }
.chart-wrap { position: relative; }
.chart-wrap-doughnut { max-height: 220px; }
.chart-wrap-sm { max-height: 180px; }
.chart-loading {
  height: 160px; display: flex; align-items: center;
  justify-content: center; color: var(--text-secondary); font-size: 1.5rem;
}

.bottom-card { overflow: hidden; }
.table tbody td { padding: 9px 14px; font-size: 0.845rem; border-color: var(--border); }

.pwd-mini-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 18px; border-bottom: 1px solid var(--border);
  cursor: pointer; transition: background 0.12s;
}
.pwd-mini-row:hover { background: var(--surface-secondary); }
.pwd-mini-row:last-child { border-bottom: none; }
.pwd-mini-photo { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.pwd-mini-initials {
  width: 38px; height: 38px; border-radius: 50%;
  background: var(--system-primary); display: flex;
  align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 0.8rem; flex-shrink: 0;
}
.pwd-mini-info { flex: 1; min-width: 0; }
.pwd-mini-info strong { display: block; font-size: 0.855rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pwd-mini-info small { color: var(--text-secondary); font-size: 0.75rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block; }
</style>
