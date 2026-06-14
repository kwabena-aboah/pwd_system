<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">Reports & Analytics</h1>
        <p class="page-subtitle">Summary statistics and performance overview</p>
      </div>
      <div class="d-flex gap-2 align-items-center flex-wrap">
        <select v-model="district" class="form-select form-select-sm" style="width:180px" @change="loadReports">
          <option value="">All Districts</option>
        </select>
        <button class="btn btn-outline-danger btn-sm" @click="exportPDF">
          <i class="bi bi-file-pdf me-1"></i><span class="d-none d-sm-inline">Export PDF</span>
        </button>
      </div>
    </div>

    <!-- PWD KPIs -->
    <div class="report-section-label">PWD Summary</div>
    <div class="kpi-grid-report">
      <div class="report-kpi" v-for="k in pwdKpis" :key="k.label" :style="{ borderColor: k.color }">
        <div class="report-kpi-val" :style="{ color: k.color }">{{ k.value }}</div>
        <div class="report-kpi-lbl">{{ k.label }}</div>
      </div>
    </div>

    <!-- Charts -->
    <div class="charts-row-report">
      <div class="chart-card">
        <div class="chart-card-header"><h3>Disability Breakdown</h3></div>
        <div style="max-height:240px"><Bar v-if="disabilityChart.labels?.length" :data="disabilityChart" :options="chartOpts" /></div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header"><h3>Age Groups</h3></div>
        <div style="max-height:240px"><Bar v-if="ageChart.labels?.length" :data="ageChart" :options="chartOpts" /></div>
      </div>
    </div>

    <!-- Benefits KPIs -->
    <div class="report-section-label mt-4">Benefits Summary</div>
    <div class="kpi-grid-report">
      <div class="report-kpi" v-for="k in benefitKpis" :key="k.label" :style="{ borderColor: k.color }">
        <div class="report-kpi-val" :style="{ color: k.color }">{{ k.value }}</div>
        <div class="report-kpi-lbl">{{ k.label }}</div>
      </div>
    </div>

    <div class="charts-row-report">
      <div class="chart-card">
        <div class="chart-card-header"><h3>Top Partners by Disbursement</h3></div>
        <div style="max-height:240px"><Bar v-if="partnerChart.labels?.length" :data="partnerChart" :options="{ ...chartOpts, indexAxis: 'y' }" /></div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header"><h3>Benefits by Category</h3></div>
        <div style="max-height:240px"><Bar v-if="categoryChart.labels?.length" :data="categoryChart" :options="chartOpts" /></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
import api from '@/services/api'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import dayjs from 'dayjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const district = ref('')
const pwdReport = ref({})
const benefitReport = ref({})

const chartOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: '#f1f5f9' } }, x: { grid: { display: false } } } }

const pwdKpis = computed(() => [
  { label: 'Total PWDs', value: pwdReport.value.total || 0, color: '#1a56db' },
  { label: 'Active', value: pwdReport.value.active || 0, color: '#10b981' },
  { label: 'Male', value: pwdReport.value.by_gender?.find(g => g.gender === 'M')?.count || 0, color: '#0ea5e9' },
  { label: 'Female', value: pwdReport.value.by_gender?.find(g => g.gender === 'F')?.count || 0, color: '#ec4899' },
])
const benefitKpis = computed(() => [
  { label: 'Total Allocations', value: benefitReport.value.total_allocations || 0, color: '#1a56db' },
  { label: 'Disbursed', value: benefitReport.value.disbursed || 0, color: '#10b981' },
  { label: 'Total GHS', value: 'GHS ' + Number(benefitReport.value.total_value_ghs || 0).toLocaleString(), color: '#f59e0b' },
  { label: 'Pending', value: benefitReport.value.pending || 0, color: '#ef4444' },
])

const disabilityChart = computed(() => {
  const d = (pwdReport.value.by_disability || []).filter(x => x['medical_records__disability_types__name'])
  return d.length ? { labels: d.map(x => x['medical_records__disability_types__name']), datasets: [{ data: d.map(x => x.count), backgroundColor: '#1a56dbaa', borderRadius: 4 }] } : {}
})
const ageChart = computed(() => {
  const d = pwdReport.value.by_age_group || []
  return d.length ? { labels: d.map(x => x.age_group), datasets: [{ data: d.map(x => x.count), backgroundColor: '#10b981aa', borderRadius: 4 }] } : {}
})
const partnerChart = computed(() => {
  const d = (benefitReport.value.by_partner || []).slice(0, 8)
  return d.length ? { labels: d.map(x => x['benefit__partner__name']), datasets: [{ data: d.map(x => x.total || 0), backgroundColor: '#f59e0baa', borderRadius: 4 }] } : {}
})
const categoryChart = computed(() => {
  const d = (benefitReport.value.by_category || []).slice(0, 8)
  return d.length ? { labels: d.map(x => x['benefit__category__name']), datasets: [{ data: d.map(x => x.count), backgroundColor: '#7e3af2aa', borderRadius: 4 }] } : {}
})

async function loadReports() {
  const [pr, br] = await Promise.all([
    api.get('/reports/pwd-summary/', { params: district.value ? { district: district.value } : {} }),
    api.get('/reports/benefits-summary/')
  ])
  pwdReport.value = pr.data
  benefitReport.value = br.data
}

async function exportPDF() {
  const doc = new jsPDF()
  doc.setFontSize(16); doc.setFont('helvetica','bold')
  doc.text('PWDMS Analytics Report', 14, 18)
  doc.setFontSize(10); doc.setFont('helvetica','normal')
  doc.text(`Generated: ${dayjs().format('DD MMMM YYYY')}`, 14, 26)
  autoTable(doc, { startY: 34, head: [['Metric','Value']], body: [...pwdKpis.value, ...benefitKpis.value].map(k => [k.label, k.value.toString()]), headStyles: { fillColor: '#1a56db' } })
  doc.save(`Report_${dayjs().format('YYYYMMDD')}.pdf`)
}

onMounted(loadReports)
</script>

<style scoped>
.report-section-label { font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.07em; padding-bottom: 10px; border-bottom: 1px solid var(--border); margin-bottom: 14px; }
.kpi-grid-report { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
@media (max-width: 900px) { .kpi-grid-report { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .kpi-grid-report { grid-template-columns: 1fr 1fr; } }
.report-kpi { background: white; border-radius: var(--radius); padding: 16px 18px; box-shadow: var(--shadow); border-left: 4px solid; }
.report-kpi-val { font-size: 1.7rem; font-weight: 800; line-height: 1; }
.report-kpi-lbl { font-size: 0.77rem; color: var(--text-secondary); margin-top: 5px; }
.charts-row-report { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 768px) { .charts-row-report { grid-template-columns: 1fr; } }
.chart-card { background: white; border-radius: var(--radius); padding: 18px; box-shadow: var(--shadow); }
.chart-card-header { margin-bottom: 14px; }
.chart-card-header h3 { font-size: 0.9rem; font-weight: 700; margin: 0; }
</style>
