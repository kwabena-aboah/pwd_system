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
  const canEdit = computed(() => !!user.value?.can_edit)

  // Keep store + localStorage in sync
  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh

    if (access) localStorage.setItem('pwd_access', access)
    else localStorage.removeItem('pwd_access')

    if (refresh) localStorage.setItem('pwd_refresh', refresh)
    else localStorage.removeItem('pwd_refresh')
  }

  async function login(email, password) {
    try {
      const { data } = await api.post('/auth/login/', { email, password })

      setTokens(data.access, data.refresh)
      await fetchUser()

      return data
    } catch (err) {
      // Clean state on failed login
      setTokens(null, null)
      user.value = null
      localStorage.removeItem('pwd_user')
      throw err
    }
  }

  async function fetchUser() {
    try {
      const { data } = await api.get('/auth/me/')
      user.value = data
      localStorage.setItem('pwd_user', JSON.stringify(data))
      return data
    } catch (err) {
      // If this fails, user is not valid anymore
      logout(false)
      throw err
    }
  }

  async function logout(callApi = true) {
    try {
      if (callApi && refreshToken.value) {
        await api.post('/auth/logout/', { refresh: refreshToken.value })
      }
    } catch {
      // ignore API failure
    }

    user.value = null
    setTokens(null, null)
    localStorage.removeItem('pwd_user')

    router.push('/login')
  }

  function hasRole(...roles) {
    return roles.includes(user.value?.role)
  }

  // 🔥 CRITICAL: run this on app startup
  async function initAuth() {
    if (!refreshToken.value) return

    try {
      // try getting user (interceptor will refresh if needed)
      await fetchUser()
    } catch {
      logout(false)
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isAdmin,
    canEdit,
    login,
    logout,
    fetchUser,
    hasRole,
    initAuth,
  }
})