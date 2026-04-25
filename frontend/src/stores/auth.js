// stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('pwd_user') || 'null'))
  const accessToken = ref(localStorage.getItem('pwd_access') || null)
  const refreshToken = ref(localStorage.getItem('pwd_refresh') || null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.role === 'super_admin')
  const canEdit = computed(() => user.value?.can_edit)

  async function login(email, password) {
    const { data } = await api.post('/auth/login/', { email, password })
    accessToken.value = data.access
    refreshToken.value = data.refresh
    localStorage.setItem('pwd_access', data.access)
    localStorage.setItem('pwd_refresh', data.refresh)
    await fetchUser()
    return data
  }

  async function fetchUser() {
    const { data } = await api.get('/auth/me/')
    user.value = data
    localStorage.setItem('pwd_user', JSON.stringify(data))
  }

  async function logout() {
    try {
      await api.post('/auth/logout/', { refresh: refreshToken.value })
    } catch {}
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('pwd_access')
    localStorage.removeItem('pwd_refresh')
    localStorage.removeItem('pwd_user')
    router.push('/login')
  }

  function hasRole(...roles) {
    return roles.includes(user.value?.role)
  }

  return { user, accessToken, refreshToken, isAuthenticated, isAdmin, canEdit, login, logout, fetchUser, hasRole }
})
