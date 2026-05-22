// stores/settings.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref({
    system_name: 'PWD Management System',
    short_name: 'PWDMS',
    district_name: '',
    region: '',
    logo: null,
    primary_color: '#1a56db',
    secondary_color: '#7e3af2',
    accent_color: '#ff5a1f',
    text_on_primary: '#ffffff',
    album_title: 'PWD Directory',
    album_subtitle: 'Registered Persons with Disability',
  })

  const isLoaded = ref(false)

  async function fetchSettings() {
    try {
      const { data } = await api.get('/settings/')
      settings.value = data
      applyTheme()
      isLoaded.value = true
    } catch {}
  }

  function applyTheme() {
    const root = document.documentElement
    root.style.setProperty('--bs-primary', settings.value.primary_color)
    root.style.setProperty('--bs-primary-rgb', hexToRgb(settings.value.primary_color))
    root.style.setProperty('--system-secondary', settings.value.secondary_color)
    root.style.setProperty('--system-accent', settings.value.accent_color)
    root.style.setProperty('--text-on-primary', settings.value.text_on_primary)

    // Update page title
    document.title = settings.value.system_name

    // Update manifest theme
    const meta = document.querySelector('meta[name="theme-color"]')
    if (meta) meta.setAttribute('content', settings.value.primary_color)
  }

  function hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)
    return `${r},${g},${b}`
  }

  async function updateSettings(formData) {
    const { data } = await api.patch('/settings/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    settings.value = data
    applyTheme()
    return data
  }

  return { settings, isLoaded, fetchSettings, updateSettings, applyTheme }
})
