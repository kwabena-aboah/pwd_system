// src/services/api.js
import axios from 'axios'

// Use env variable in production, fallback to relative path
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/_backend/api'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('pwd_access')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Token refresh handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true

      try {
        const refresh = localStorage.getItem('pwd_refresh')

        // IMPORTANT: use BASE_URL, not raw axios
        const { data } = await axios.post(
          `${BASE_URL}/auth/refresh/`,
          { refresh }
        )

        localStorage.setItem('pwd_access', data.access)

        // Update headers
        api.defaults.headers.Authorization = `Bearer ${data.access}`
        original.headers.Authorization = `Bearer ${data.access}`

        return api(original)
      } catch (refreshError) {
        // Hard reset if refresh fails
        localStorage.removeItem('pwd_access')
        localStorage.removeItem('pwd_refresh')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default api