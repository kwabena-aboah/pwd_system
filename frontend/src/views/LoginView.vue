<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-blob blob-1"></div>
      <div class="bg-blob blob-2"></div>
    </div>

    <div class="login-card">
      <div class="login-brand">
        <div class="brand-mark">
          <img v-if="logoUrl" :src="logoUrl" alt="Logo" class="login-logo">
          <div v-else class="login-icon"><i class="bi bi-heart-pulse-fill"></i></div>
        </div>
        <h1 class="login-title">{{ systemName }}</h1>
        <p class="login-sub">Persons With Disability Management System</p>
      </div>

      <form @submit.prevent="handleLogin" novalidate>
        <div class="field-group">
          <label class="field-label">Email Address</label>
          <div class="field-input-wrap">
            <i class="bi bi-envelope field-icon"></i>
            <input v-model="form.email" type="email" class="field-input" :class="{ error: hasError }"
              placeholder="you@example.com" required autocomplete="email" :disabled="loading">
          </div>
        </div>

        <div class="field-group">
          <label class="field-label">Password</label>
          <div class="field-input-wrap">
            <i class="bi bi-lock field-icon"></i>
            <input v-model="form.password" :type="showPwd ? 'text' : 'password'"
              class="field-input" :class="{ error: hasError }"
              placeholder="••••••••" required autocomplete="current-password" :disabled="loading">
            <button type="button" class="field-toggle" @click="showPwd = !showPwd" tabindex="-1">
              <i :class="showPwd ? 'bi-eye-slash' : 'bi-eye'"></i>
            </button>
          </div>
        </div>

        <div v-if="errorMsg" class="error-alert">
          <i class="bi bi-exclamation-circle-fill me-2"></i>{{ errorMsg }}
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          <span>{{ loading ? 'Signing in…' : 'Sign In' }}</span>
          <i v-if="!loading" class="bi bi-arrow-right ms-2"></i>
        </button>
      </form>

      <p class="login-footer">
        <i class="bi bi-shield-check me-1" style="color:#10b981"></i>
        Secure access — Authorised users only
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const auth = useAuthStore()

const form = ref({ email: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')
const hasError = ref(false)
const showPwd = ref(false)
const systemName = ref('PWD Management System')
const logoUrl = ref(null)

onMounted(async () => {
  if (auth.isAuthenticated) { router.push('/dashboard'); return }
  try {
    const { data } = await api.get('/settings/')
    systemName.value = data.system_name || 'PWD Management System'
    logoUrl.value = data.logo_url || null
    if (data.primary_color) {
      document.documentElement.style.setProperty('--system-primary', data.primary_color)
    }
  } catch {}
})

async function handleLogin() {
  loading.value = true
  errorMsg.value = ''
  hasError.value = false
  try {
    await auth.login(form.value.email, form.value.password)
    router.push('/dashboard')
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || 'Invalid email or password. Please try again.'
    hasError.value = true
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; display: flex;
  align-items: center; justify-content: center;
  background: #f0f4ff; padding: 20px; position: relative; overflow: hidden;
}

.login-bg { position: fixed; inset: 0; pointer-events: none; }
.bg-blob {
  position: absolute; border-radius: 50%;
  background: var(--system-primary, #1a56db);
  filter: blur(60px); opacity: 0.12;
}
.blob-1 { width: 500px; height: 500px; top: -180px; right: -100px; }
.blob-2 { width: 350px; height: 350px; bottom: -100px; left: -80px; opacity: 0.09; }

.login-card {
  background: white; border-radius: 20px;
  padding: clamp(28px, 5vw, 48px) clamp(24px, 5vw, 44px);
  width: 100%; max-width: 420px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.12), 0 4px 16px rgba(0,0,0,0.06);
  position: relative; z-index: 1;
}

.login-brand { text-align: center; margin-bottom: 32px; }
.brand-mark { display: flex; justify-content: center; margin-bottom: 14px; }
.login-logo { height: 60px; object-fit: contain; }
.login-icon {
  width: 68px; height: 68px; border-radius: 18px;
  background: var(--system-primary, #1a56db);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.9rem; color: white;
  box-shadow: 0 8px 20px rgba(26,86,219,0.3);
}
.login-title { font-size: clamp(1.15rem, 3vw, 1.35rem); font-weight: 800; margin-bottom: 6px; color: #0f172a; }
.login-sub { color: #64748b; font-size: 0.845rem; }

.field-group { margin-bottom: 18px; }
.field-label { display: block; font-size: 0.845rem; font-weight: 600; color: #0f172a; margin-bottom: 7px; }
.field-input-wrap { position: relative; }
.field-icon {
  position: absolute; left: 13px; top: 50%;
  transform: translateY(-50%); color: #94a3b8;
  font-size: 0.9rem; pointer-events: none;
}
.field-input {
  width: 100%; padding: 11px 42px 11px 38px;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 0.9rem; outline: none; transition: border-color 0.15s, box-shadow 0.15s;
  color: #0f172a; background: #f8fafc;
}
.field-input:focus {
  border-color: var(--system-primary, #1a56db); background: white;
  box-shadow: 0 0 0 3px rgba(26,86,219,0.1);
}
.field-input.error { border-color: #ef4444; background: #fff5f5; }
.field-input::placeholder { color: #cbd5e1; }
.field-toggle {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  background: none; border: none; color: #94a3b8;
  cursor: pointer; padding: 4px; font-size: 0.95rem;
}

.error-alert {
  background: #fef2f2; border: 1px solid #fecaca; border-radius: 9px;
  padding: 10px 14px; color: #dc2626; font-size: 0.845rem; margin-bottom: 16px;
}

.login-btn {
  width: 100%; padding: 12px;
  background: var(--system-primary, #1a56db); color: white;
  border: none; border-radius: 10px; font-size: 0.92rem; font-weight: 700;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: opacity 0.15s, transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 4px 12px rgba(26,86,219,0.25);
  margin-top: 4px;
}
.login-btn:hover:not(:disabled) {
  opacity: 0.92; transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(26,86,219,0.32);
}
.login-btn:active:not(:disabled) { transform: translateY(0); }
.login-btn:disabled { opacity: 0.65; cursor: not-allowed; transform: none; }

.login-footer { text-align: center; margin-top: 20px; font-size: 0.79rem; color: #94a3b8; }

@media (max-width: 380px) {
  .login-card { padding: 24px 18px; }
}
</style>
