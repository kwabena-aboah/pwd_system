<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ settingsStore.settings.album_title || 'PWD Album' }}</h1>
        <p class="page-subtitle">{{ settingsStore.settings.album_subtitle }} — {{ filtered.length }} records</p>
      </div>
      <div class="album-actions">
        <select class="form-select form-select-sm" v-model="filterDistrict" @change="applyFilter" style="width:160px">
          <option value="">All Districts</option>
          <option v-for="d in districts" :key="d" :value="d">{{ d }}</option>
        </select>
        <div class="d-flex gap-2 flex-wrap">
          <button class="btn btn-outline-danger btn-sm" @click="exportPDF" :disabled="exporting">
            <i class="bi bi-file-earmark-pdf me-1"></i><span class="d-none d-sm-inline">PDF</span>
          </button>
          <button class="btn btn-outline-primary btn-sm" @click="exportPPTX" :disabled="exporting">
            <i class="bi bi-file-earmark-slides me-1"></i><span class="d-none d-sm-inline">PPTX</span>
          </button>
          <button class="btn btn-outline-secondary btn-sm" @click="printAlbum">
            <i class="bi bi-printer me-1"></i><span class="d-none d-sm-inline">Print</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border" style="color:var(--system-primary)"></div>
      <p class="mt-2 text-muted">Loading album…</p>
    </div>

    <div v-else id="album-printable" class="album-container">
      <!-- Print header -->
      <div class="album-print-header">
        <img v-if="settingsStore.settings.logo_url" :src="settingsStore.settings.logo_url" class="print-logo" alt="">
        <div>
          <h2>{{ settingsStore.settings.album_title }}</h2>
          <p>{{ settingsStore.settings.album_subtitle }}</p>
          <p v-if="settingsStore.settings.district_name"><strong>{{ settingsStore.settings.district_name }}</strong></p>
        </div>
      </div>

      <div v-if="!filtered.length" class="empty-state">
        <i class="bi bi-journal-richtext"></i>
        <p>No PWD records found{{ filterDistrict ? ' for ' + filterDistrict : '' }}.</p>
      </div>

      <div class="pwd-album-grid" v-else>
        <div v-for="pwd in filtered" :key="pwd.id" class="pwd-album-card"
          @click="router.push(`/pwds/${pwd.id}`)">
          <div class="album-photo-wrap">
            <img v-if="pwd.photo" :src="pwd.photo" :alt="pwd.first_name" class="album-photo">
            <div v-else class="album-photo-placeholder">
              <i class="bi bi-person-fill"></i>
            </div>
            <span v-if="pwd.ai_risk_label" class="album-risk-tag"
              :class="'risk-' + pwd.ai_risk_label">{{ pwd.ai_risk_label }}</span>
          </div>
          <div class="album-card-body">
            <h4 class="album-name">{{ pwd.first_name }} {{ pwd.last_name }}</h4>
            <p class="album-reg" v-if="settingsStore.settings.album_show_reg_number">
              {{ pwd.registration_number }}
            </p>
            <p class="album-detail" v-if="settingsStore.settings.album_show_disability && pwd.disability_summary">
              <i class="bi bi-accessibility"></i>{{ pwd.disability_summary }}
            </p>
            <p class="album-detail" v-if="settingsStore.settings.album_show_community">
              <i class="bi bi-geo-alt-fill"></i>{{ pwd.community }}, {{ pwd.district }}
            </p>
            <p class="album-detail" v-if="settingsStore.settings.album_show_phone && pwd.phone">
              <i class="bi bi-telephone-fill"></i>{{ pwd.phone }}
            </p>
          </div>
        </div>
      </div>

      <div class="album-print-footer">
        <p>{{ settingsStore.settings.system_name }} | Printed: {{ today }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'
import api from '@/services/api'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import PptxGenJS from 'pptxgenjs'
import dayjs from 'dayjs'

const router = useRouter()
const settingsStore = useSettingsStore()
const pwds = ref([])
const loading = ref(false)
const exporting = ref(false)
const filterDistrict = ref('')
const today = dayjs().format('DD MMMM YYYY')

const districts = computed(() => [...new Set(pwds.value.map(p => p.district).filter(Boolean))].sort())
const filtered = computed(() => filterDistrict.value ? pwds.value.filter(p => p.district === filterDistrict.value) : pwds.value)

function applyFilter() {} // reactive

async function loadAlbum() {
  loading.value = true
  try {
    const { data } = await api.get('/pwds/album/')
    pwds.value = data
  } finally { loading.value = false }
}

function printAlbum() { window.print() }

async function exportPDF() {
  exporting.value = true
  try {
    const doc = new jsPDF({ orientation: 'landscape', format: 'a4' })
    const W = doc.internal.pageSize.width
    const pc = settingsStore.settings.primary_color || '#1a56db'
    doc.setFillColor(pc); doc.rect(0,0,W,50,'F')
    doc.setTextColor(255,255,255); doc.setFontSize(20); doc.setFont('helvetica','bold')
    doc.text(settingsStore.settings.album_title || 'PWD Directory', W/2, 22, { align:'center' })
    doc.setFontSize(11); doc.setFont('helvetica','normal')
    doc.text(settingsStore.settings.district_name || '', W/2, 35, { align:'center' })
    doc.text(`Total: ${filtered.value.length} | ${today}`, W/2, 44, { align:'center' })
    doc.setTextColor(40,40,40)
    autoTable(doc, {
      startY: 60,
      head: [['#','Reg. No.','Full Name','Age','Gender','Disability','Community','District','Risk','Status']],
      body: filtered.value.map((p,i) => [i+1, p.registration_number, `${p.first_name} ${p.last_name}`, p.age||'', p.gender==='M'?'M':'F', p.disability_summary||'', p.community||'', p.district||'', p.ai_risk_label||'', p.status||'']),
      headStyles: { fillColor: pc, textColor: 255, fontStyle: 'bold', fontSize: 8 },
      bodyStyles: { fontSize: 7.5 },
      alternateRowStyles: { fillColor: [249,250,251] },
    })
    const pages = doc.internal.getNumberOfPages()
    for (let i=1;i<=pages;i++) { doc.setPage(i); doc.setFontSize(7); doc.setTextColor(150); doc.text(`${settingsStore.settings.system_name} | Page ${i}/${pages}`, W/2, doc.internal.pageSize.height-5, {align:'center'}) }
    doc.save(`PWD_Album_${dayjs().format('YYYYMMDD')}.pdf`)
  } finally { exporting.value = false }
}

async function exportPPTX() {
  exporting.value = true
  try {
    const pptx = new PptxGenJS()
    pptx.layout = 'LAYOUT_WIDE'; pptx.title = settingsStore.settings.album_title
    const pc = (settingsStore.settings.primary_color || '#1a56db').replace('#','')
    const title = pptx.addSlide()
    title.background = { color: pc }
    title.addText(settingsStore.settings.album_title || 'PWD Directory', { x:1,y:1.5,w:11,h:1.2,fontSize:34,bold:true,color:'FFFFFF',align:'center' })
    title.addText(settingsStore.settings.district_name || '', { x:1,y:3,w:11,h:0.7,fontSize:18,color:'FFFFFF',align:'center' })
    title.addText(`Records: ${filtered.value.length} | ${today}`, { x:1,y:4,w:11,h:0.5,fontSize:13,color:'DDDDDD',align:'center' })
    const perSlide = 10
    for (let i=0; i<filtered.value.length; i+=perSlide) {
      const chunk = filtered.value.slice(i, i+perSlide)
      const slide = pptx.addSlide()
      slide.addText(`PWD Records (${i+1}–${Math.min(i+perSlide, filtered.value.length)})`, {x:0.3,y:0.15,w:12.7,h:0.55,fontSize:15,bold:true,color:pc})
      const rows = [
        [{ text:'#',options:{bold:true,fill:pc,color:'FFFFFF',fontSize:8} },{ text:'Reg. No.',options:{bold:true,fill:pc,color:'FFFFFF',fontSize:8} },{ text:'Name',options:{bold:true,fill:pc,color:'FFFFFF',fontSize:8} },{ text:'Age/Gender',options:{bold:true,fill:pc,color:'FFFFFF',fontSize:8} },{ text:'Disability',options:{bold:true,fill:pc,color:'FFFFFF',fontSize:8} },{ text:'Community',options:{bold:true,fill:pc,color:'FFFFFF',fontSize:8} },{ text:'Risk',options:{bold:true,fill:pc,color:'FFFFFF',fontSize:8} }],
        ...chunk.map((p,idx) => { const bg = idx%2===0?'F8FAFF':'FFFFFF'; return [{ text:String(i+idx+1),options:{fontSize:8,fill:bg} },{ text:p.registration_number,options:{fontSize:8,fill:bg} },{ text:`${p.first_name} ${p.last_name}`,options:{fontSize:8,fill:bg} },{ text:`${p.age||'?'}/${p.gender}`,options:{fontSize:8,fill:bg} },{ text:p.disability_summary||'',options:{fontSize:8,fill:bg} },{ text:p.community||'',options:{fontSize:8,fill:bg} },{ text:p.ai_risk_label||'',options:{fontSize:8,fill:bg} }] })
      ]
      slide.addTable(rows, { x:0.2,y:0.8,w:13,colW:[0.5,1.8,2.5,1.2,2.5,2.2,1.3],border:{pt:0.5,color:'E2E8F0'} })
    }
    await pptx.writeFile({ fileName: `PWD_Album_${dayjs().format('YYYYMMDD')}.pptx` })
  } finally { exporting.value = false }
}

onMounted(loadAlbum)
</script>

<style scoped>
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; gap: 12px; flex-wrap: wrap; }
.album-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }

.album-container { background: white; border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); }

.pwd-album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}
@media (max-width: 480px) { .pwd-album-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; } }

.pwd-album-card {
  background: var(--surface-secondary); border-radius: 10px;
  overflow: hidden; cursor: pointer; border: 2px solid transparent;
  transition: border-color 0.18s, transform 0.18s, box-shadow 0.18s;
}
.pwd-album-card:hover { border-color: var(--system-primary); transform: translateY(-3px); box-shadow: var(--shadow-md); }

.album-photo-wrap { position: relative; }
.album-photo { width: 100%; height: 160px; object-fit: cover; display: block; }
.album-photo-placeholder {
  width: 100%; height: 160px;
  background: linear-gradient(135deg, var(--system-primary) 0%, #7e3af2 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 2.6rem; color: rgba(255,255,255,0.5);
}
@media (max-width: 480px) { .album-photo, .album-photo-placeholder { height: 130px; } }

.album-risk-tag {
  position: absolute; top: 6px; right: 6px;
  padding: 2px 7px; border-radius: 12px;
  font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
}
.risk-low { background: #d1fae5; color: #065f46; }
.risk-medium { background: #fef3c7; color: #92400e; }
.risk-high { background: #fee2e2; color: #991b1b; }
.risk-critical { background: #991b1b; color: white; }

.album-card-body { padding: 10px 11px; }
.album-name { font-size: 0.845rem; font-weight: 700; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.album-reg { font-size: 0.68rem; color: var(--text-secondary); margin-bottom: 3px; font-family: monospace; }
.album-detail { font-size: 0.72rem; color: var(--text-secondary); margin-bottom: 2px; display: flex; align-items: flex-start; gap: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.album-detail i { flex-shrink: 0; color: var(--system-primary); margin-top: 2px; }

/* Print */
.album-print-header { display: none; }
.album-print-footer { display: none; }

@media print {
  .page-header, nav, .topbar { display: none !important; }
  .album-container { padding: 0; box-shadow: none; }
  .album-print-header { display: flex !important; align-items: center; gap: 16px; margin-bottom: 16px; border-bottom: 3px solid #1a56db; padding-bottom: 12px; }
  .album-print-footer { display: block !important; text-align: center; margin-top: 20px; font-size: 0.75rem; color: #666; border-top: 1px solid #ddd; padding-top: 10px; }
  .print-logo { height: 50px; object-fit: contain; }
  .pwd-album-grid { grid-template-columns: repeat(4, 1fr); gap: 10px; }
  .pwd-album-card { break-inside: avoid; border: 1px solid #ddd; }
}
</style>
