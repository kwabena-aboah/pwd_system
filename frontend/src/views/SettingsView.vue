<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">System Settings</h1>
        <p class="page-subtitle">Configure branding, colors and album layout</p>
      </div>
    </div>

    <div class="settings-grid">
      <!-- Branding -->
      <div class="settings-card">
        <h5 class="settings-title"><i class="bi bi-building me-2"></i>District Identity</h5>
        <div class="field-stack">
          <div class="field-row">
            <label>System Name</label>
            <input v-model="form.system_name" type="text" class="form-control form-control-sm">
          </div>
          <div class="field-row">
            <label>Short Name</label>
            <input v-model="form.short_name" type="text" class="form-control form-control-sm">
          </div>
          <div class="field-row">
            <label>District Assembly</label>
            <input v-model="form.district_name" type="text" class="form-control form-control-sm">
          </div>
          <div class="field-row">
            <label>Region</label>
            <input v-model="form.region" type="text" class="form-control form-control-sm">
          </div>
          <div class="field-col">
            <label>Primary Logo</label>
            <input type="file" class="form-control form-control-sm" accept="image/*" @change="onLogo">
            <div v-if="currentLogoUrl" class="logo-preview mt-2">
              <img :src="currentLogoUrl" alt="Logo" class="logo-preview-img">
            </div>
          </div>
          <div class="field-col">
            <label>Secondary Logo <small class="text-muted">(optional)</small></label>
            <input type="file" class="form-control form-control-sm" accept="image/*" @change="onLogo2">
          </div>
        </div>
      </div>

      <!-- Colors -->
      <div class="settings-card">
        <h5 class="settings-title"><i class="bi bi-palette me-2"></i>Color Scheme</h5>
        <div class="color-preview-bar" :style="{ background: form.primary_color }">
          <span :style="{ color: form.text_on_primary }">{{ form.system_name || 'Preview' }}</span>
        </div>
        <div class="color-grid">
          <div v-for="c in colorFields" :key="c.key" class="color-field">
            <label>{{ c.label }}</label>
            <div class="color-row">
              <input :value="form[c.key]" type="color" class="color-swatch" @input="form[c.key] = $event.target.value">
              <input v-model="form[c.key]" type="text" class="form-control form-control-sm" maxlength="7">
            </div>
          </div>
        </div>
        <div class="theme-section">
          <p class="theme-label">Quick Themes</p>
          <div class="theme-swatches">
            <button v-for="t in themes" :key="t.name" class="theme-swatch" :style="{ background: t.primary }"
              :title="t.name" @click="applyTheme(t)" type="button"></button>
          </div>
        </div>
      </div>

      <!-- Album settings -->
      <div class="settings-card settings-card-wide">
        <h5 class="settings-title"><i class="bi bi-journal-richtext me-2"></i>Album Configuration</h5>
        <div class="album-fields">
          <div>
            <label class="form-label form-label-sm">Album Title</label>
            <input v-model="form.album_title" type="text" class="form-control form-control-sm">
          </div>
          <div>
            <label class="form-label form-label-sm">Album Subtitle</label>
            <input v-model="form.album_subtitle" type="text" class="form-control form-control-sm">
          </div>
          <div>
            <label class="form-label form-label-sm">Photos per Page</label>
            <input v-model="form.album_photos_per_page" type="number" class="form-control form-control-sm" min="4" max="24">
          </div>
        </div>
        <div class="toggle-row">
          <div class="toggle-item" v-for="t in toggleFields" :key="t.key">
            <div class="form-check form-switch mb-0">
              <input v-model="form[t.key]" class="form-check-input" type="checkbox" :id="t.key">
              <label class="form-check-label" :for="t.key">{{ t.label }}</label>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact -->
      <div class="settings-card">
        <h5 class="settings-title"><i class="bi bi-telephone me-2"></i>Contact Details</h5>
        <div class="field-stack">
          <div class="field-col">
            <label>Contact Email</label>
            <input v-model="form.contact_email" type="email" class="form-control form-control-sm">
          </div>
          <div class="field-col">
            <label>Contact Phone</label>
            <input v-model="form.contact_phone" type="text" class="form-control form-control-sm">
          </div>
          <div class="field-col">
            <label>Address</label>
            <textarea v-model="form.address" class="form-control form-control-sm" rows="2"></textarea>
          </div>
          <div class="field-col">
            <label>Website</label>
            <input v-model="form.website" type="url" class="form-control form-control-sm">
          </div>
        </div>
      </div>
    </div>

    <!-- Save Bar -->
    <div class="save-bar">
      <button class="btn btn-primary" @click="saveSettings" :disabled="saving">
        <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="bi bi-check-lg me-2"></i>Save Settings
      </button>
      <transition name="fade">
        <div v-if="saved" class="save-success">
          <i class="bi bi-check-circle-fill me-2"></i>Saved successfully!
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

const saving = ref(false)
const saved = ref(false)
const error = ref(null)

const currentLogoUrl = ref(null)
const logoFile = ref(null)
const logo2File = ref(null)

let objectUrl = null // for cleanup

const form = ref({
  system_name: '',
  short_name: '',
  district_name: '',
  region: '',
  primary_color: '#1a56db',
  secondary_color: '#7e3af2',
  accent_color: '#ff5a1f',
  text_on_primary: '#ffffff',
  album_title: '',
  album_subtitle: '',
  album_photos_per_page: 12,
  album_show_reg_number: true,
  album_show_disability: true,
  album_show_community: true,
  album_show_phone: false,
  contact_email: '',
  contact_phone: '',
  address: '',
  website: '',
})

const colorFields = [
  { key: 'primary_color', label: 'Primary' },
  { key: 'secondary_color', label: 'Secondary' },
  { key: 'accent_color', label: 'Accent' },
  { key: 'text_on_primary', label: 'Text on Primary' },
]

const toggleFields = [
  { key: 'album_show_reg_number', label: 'Show Reg. Number' },
  { key: 'album_show_disability', label: 'Show Disability' },
  { key: 'album_show_community', label: 'Show Community' },
  { key: 'album_show_phone', label: 'Show Phone' },
]

const themes = [
  { name: 'Blue', primary: '#1a56db', secondary: '#7e3af2', accent: '#ff5a1f' },
  { name: 'Green', primary: '#059669', secondary: '#0284c7', accent: '#f59e0b' },
  { name: 'Purple', primary: '#7c3aed', secondary: '#db2777', accent: '#f97316' },
  { name: 'Red', primary: '#dc2626', secondary: '#ea580c', accent: '#16a34a' },
  { name: 'Teal', primary: '#0891b2', secondary: '#0d9488', accent: '#f59e0b' },
  { name: 'Slate Dark', primary: '#1e293b', secondary: '#334155', accent: '#38bdf8' },
  { name: 'Ghana Gold', primary: '#c8a214', secondary: '#006b3c', accent: '#ce1126' },
]

// Apply theme
function applyTheme(t) {
  form.value.primary_color = t.primary
  form.value.secondary_color = t.secondary
  form.value.accent_color = t.accent
}

// Logo handlers
function onLogo(e) {
  const file = e.target.files[0]
  if (!file) return

  // revoke old preview
  if (objectUrl) URL.revokeObjectURL(objectUrl)

  logoFile.value = file
  objectUrl = URL.createObjectURL(file)
  currentLogoUrl.value = objectUrl
}

function onLogo2(e) {
  const file = e.target.files[0]
  if (!file) return
  logo2File.value = file
}

// Basic validation (keep it simple but useful)
function validate() {
  if (!form.value.system_name) return 'System name is required'
  if (!form.value.district_name) return 'District name is required'
  if (form.value.contact_email && !form.value.contact_email.includes('@')) {
    return 'Invalid email address'
  }
  return null
}

// Save
async function saveSettings() {
  error.value = validate()
  if (error.value) {
    alert(error.value)
    return
  }

  saving.value = true
  error.value = null

  try {
    const fd = new FormData()

    Object.entries(form.value).forEach(([k, v]) => {
      // Convert booleans properly for DRF
      if (typeof v === 'boolean') {
        fd.append(k, v ? 'true' : 'false')
      } else if (v !== null && v !== '') {
        fd.append(k, v)
      }
    })

    if (logoFile.value) fd.append('logo', logoFile.value)
    if (logo2File.value) fd.append('logo_secondary', logo2File.value)

    await settingsStore.updateSettings(fd)

    saved.value = true
    setTimeout(() => (saved.value = false), 3000)

  } catch (err) {
    console.error(err)
    error.value = 'Failed to save settings'
    alert(error.value)
  } finally {
    saving.value = false
  }
}

// Load
onMounted(async () => {
  try {
    await settingsStore.fetchSettings()

    if (settingsStore.settings) {
      Object.keys(form.value).forEach(key => {
        if (settingsStore.settings[key] !== undefined) {
          form.value[key] = settingsStore.settings[key]
        }
      })

      currentLogoUrl.value = settingsStore.settings.logo_url || null
    }
  } catch (err) {
    console.error(err)
    error.value = 'Failed to load settings'
  }
})

// Cleanup (important)
onBeforeUnmount(() => {
  if (objectUrl) URL.revokeObjectURL(objectUrl)
})
</script>

<style scoped>
.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px; margin-bottom: 20px;
}
.settings-card-wide { grid-column: 1 / -1; }
@media (max-width: 900px) { .settings-grid { grid-template-columns: 1fr; } .settings-card-wide { grid-column: auto; } }

.settings-card { background: white; border-radius: var(--radius); padding: 22px; box-shadow: var(--shadow); }
.settings-title { font-size: 0.95rem; font-weight: 700; margin-bottom: 18px; padding-bottom: 12px; border-bottom: 1px solid var(--border); }

.field-stack { display: flex; flex-direction: column; gap: 12px; }
.field-row { display: flex; align-items: center; gap: 12px; }
.field-row label { font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); min-width: 120px; flex-shrink: 0; }
.field-row .form-control { flex: 1; }
.field-col label { font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); display: block; margin-bottom: 5px; }

.logo-preview { display: flex; align-items: center; }
.logo-preview-img { height: 48px; object-fit: contain; border-radius: 8px; border: 1px solid var(--border); padding: 4px; background: var(--surface-secondary); }

.color-preview-bar { border-radius: 10px; padding: 16px 20px; font-weight: 700; font-size: 1rem; margin-bottom: 16px; transition: background 0.3s; }

.color-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.color-field label { font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); display: block; margin-bottom: 5px; }
.color-row { display: flex; align-items: center; gap: 8px; }
.color-swatch { width: 38px; height: 34px; border: 1px solid var(--border); border-radius: 7px; cursor: pointer; padding: 2px; flex-shrink: 0; }
.color-row .form-control { flex: 1; font-family: monospace; font-size: 0.82rem; }

.theme-section { border-top: 1px solid var(--border); padding-top: 14px; }
.theme-label { font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 10px; }
.theme-swatches { display: flex; gap: 10px; flex-wrap: wrap; }
.theme-swatch { width: 34px; height: 34px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 0 2px var(--border); cursor: pointer; transition: transform 0.18s; }
.theme-swatch:hover { transform: scale(1.18); }

.album-fields { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
@media (max-width: 640px) { .album-fields { grid-template-columns: 1fr; } }
.toggle-row { display: flex; gap: 24px; flex-wrap: wrap; border-top: 1px solid var(--border); padding-top: 14px; }
.toggle-item { flex: 1; min-width: 140px; }

.save-bar { display: flex; align-items: center; gap: 16px; padding: 16px 0; flex-wrap: wrap; }
.save-success { display: flex; align-items: center; background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 8px 14px; color: #15803d; font-size: 0.855rem; font-weight: 500; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 575px) {
  .field-row { flex-direction: column; align-items: flex-start; }
  .field-row label { min-width: auto; }
  .color-grid { grid-template-columns: 1fr; }
}
</style>
