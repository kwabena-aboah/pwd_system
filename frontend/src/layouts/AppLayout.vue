<template>
  <div class="app-wrapper" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- Offline Banner -->
    <div v-if="!offlineStore.isOnline" class="offline-banner">
      <i class="bi bi-wifi-off me-2"></i>
      You are offline. Changes will sync when connection is restored.
      <span v-if="offlineStore.pendingCount > 0" class="badge bg-warning text-dark ms-2">
        {{ offlineStore.pendingCount }} pending
      </span>
    </div>

    <!-- Sidebar -->
    <nav class="sidebar" id="sidebar">
      <div class="sidebar-brand">
        <img v-if="settings.logo" :src="settings.logo" alt="Logo" class="brand-logo">
        <div v-else class="brand-icon">
          <i class="bi bi-heart-pulse-fill"></i>
        </div>
        <div class="brand-text">
          <span class="brand-name">{{ settings.short_name }}</span>
          <span class="brand-sub">{{ settings.district_name || 'PWD System' }}</span>
        </div>
      </div>

      <div class="sidebar-content">
        <div class="sidebar-section">
          <span class="sidebar-label">Main</span>
          <NavItem to="/dashboard" icon="bi-grid-fill" label="Dashboard" />
          <NavItem to="/pwds" icon="bi-people-fill" label="PWD Records" badge-color="primary" />
          <NavItem to="/album" icon="bi-journal-richtext" label="PWD Album" />
        </div>

        <div class="sidebar-section">
          <span class="sidebar-label">Welfare</span>
          <NavItem to="/partners" icon="bi-building-fill" label="Dev. Partners" />
          <NavItem to="/benefits" icon="bi-gift-fill" label="Benefits" />
          <NavItem to="/allocations" icon="bi-check2-circle" label="Allocations" />
          <NavItem to="/complaints" icon="bi-chat-square-text-fill" label="Complaints" :badge="openComplaints" />
        </div>

        <div class="sidebar-section">
          <span class="sidebar-label">Analytics</span>
          <NavItem to="/reports" icon="bi-bar-chart-fill" label="Reports" />
        </div>

        <div class="sidebar-section" v-if="auth.hasRole('super_admin', 'auditor')">
          <span class="sidebar-label">Administration</span>
          <NavItem to="/audit" icon="bi-shield-check" label="Audit Log" v-if="auth.hasRole('super_admin', 'auditor')" />
          <NavItem to="/users" icon="bi-person-badge-fill" label="Users" v-if="auth.isAdmin" />
          <NavItem to="/settings" icon="bi-gear-fill" label="Settings" v-if="auth.isAdmin" />
        </div>
      </div>

      <div class="sidebar-footer">
        <div class="user-card">
          <img v-if="auth.user?.profile_photo" :src="auth.user.profile_photo" class="user-avatar" alt="">
          <div v-else class="user-avatar-placeholder">{{ initials }}</div>
          <div class="user-info">
            <span class="user-name">{{ auth.user?.full_name }}</span>
            <span class="user-role">{{ auth.user?.role?.replace('_', ' ') }}</span>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Top Bar -->
      <header class="topbar">
        <button class="btn-collapse" @click="sidebarCollapsed = !sidebarCollapsed">
          <i class="bi bi-list"></i>
        </button>

        <div class="topbar-search">
          <i class="bi bi-search"></i>
          <input type="text" placeholder="Quick search PWDs..." v-model="globalSearch"
            @keyup.enter="doSearch" class="search-input">
        </div>

        <div class="topbar-actions">
          <!-- Sync indicator -->
          <button v-if="offlineStore.pendingCount > 0" class="btn-icon" @click="offlineStore.sync()" title="Sync pending">
            <i class="bi bi-arrow-repeat" :class="{ 'spin': offlineStore.isSyncing }"></i>
            <span class="badge-dot warning">{{ offlineStore.pendingCount }}</span>
          </button>

          <!-- Notifications -->
          <button class="btn-icon" @click="router.push('/notifications')" title="Notifications">
            <i class="bi bi-bell-fill"></i>
            <span v-if="unreadNotifications > 0" class="badge-dot danger">{{ unreadNotifications }}</span>
          </button>

          <!-- User menu -->
          <div class="user-menu-wrapper" ref="userMenuRef">
            <button class="btn-icon user-btn" @click="userMenuOpen = !userMenuOpen">
              <img v-if="auth.user?.profile_photo" :src="auth.user.profile_photo" class="topbar-avatar">
              <div v-else class="topbar-avatar-placeholder">{{ initials }}</div>
              <i class="bi bi-chevron-down ms-1"></i>
            </button>
            <div class="user-dropdown" v-if="userMenuOpen">
              <div class="dropdown-header">
                <strong>{{ auth.user?.full_name }}</strong>
                <small>{{ auth.user?.email }}</small>
              </div>
              <button class="dropdown-item" @click="router.push('/settings')">
                <i class="bi bi-gear me-2"></i>Settings
              </button>
              <hr class="dropdown-divider">
              <button class="dropdown-item text-danger" @click="auth.logout()">
                <i class="bi bi-box-arrow-right me-2"></i>Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSettingsStore } from '@/stores/settings'
import { useOfflineStore } from '@/stores/offline'
import NavItem from '@/components/NavItem.vue'
import api from '@/services/api'

const router = useRouter()
const auth = useAuthStore()
const settingsStore = useSettingsStore()
const offlineStore = useOfflineStore()

const { settings } = settingsStore
const sidebarCollapsed = ref(false)
const globalSearch = ref('')
const userMenuOpen = ref(false)
const openComplaints = ref(0)
const unreadNotifications = ref(0)

const initials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  return `${u.first_name?.[0] || ''}${u.last_name?.[0] || ''}`.toUpperCase()
})

function doSearch() {
  if (globalSearch.value.trim()) {
    router.push({ path: '/pwds', query: { search: globalSearch.value } })
  }
}

onMounted(async () => {
  await settingsStore.fetchSettings()
  try {
    const [cmp, notif] = await Promise.all([
      api.get('/complaints/?status=open&page_size=1'),
      api.get('/notifications/?is_read=false&page_size=1'),
    ])
    openComplaints.value = cmp.data.count || 0
    unreadNotifications.value = notif.data.count || 0
  } catch {}
})
</script>

<style lang="scss">
:root {
  --sidebar-width: 260px;
  --sidebar-collapsed-width: 72px;
  --topbar-height: 64px;
  --system-primary: var(--bs-primary, #1a56db);
  --system-secondary: #7e3af2;
  --system-accent: #ff5a1f;
  --sidebar-bg: #0f172a;
  --sidebar-text: #94a3b8;
  --sidebar-active: #ffffff;
  --sidebar-active-bg: rgba(255,255,255,0.12);
  --surface: #ffffff;
  --surface-secondary: #f8fafc;
  --border: #e2e8f0;
  --text-primary: #0f172a;
  --text-secondary: #64748b;
  --radius: 12px;
  --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: var(--surface-secondary); color: var(--text-primary); }

.app-wrapper {
 /* display: flex; */
  min-height: 100vh;
}

/* Offline Banner */
.offline-banner {
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  background: #dc2626; color: white;
  padding: 8px 20px; text-align: center; font-size: 0.875rem; font-weight: 500;
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  min-height: 100vh;
  background: var(--sidebar-bg);
  display: flex; flex-direction: column;
  position: fixed; left: 0; top: 0; bottom: 0; z-index: 100;
  transition: width 0.25s ease;
  overflow: hidden;
}

.app-wrapper.sidebar-collapsed .sidebar { width: var(--sidebar-collapsed-width); }
.app-wrapper.sidebar-collapsed .main-content { margin-left: var(--sidebar-collapsed-width); }

.sidebar-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 20px 16px; border-bottom: 1px solid rgba(255,255,255,0.08);
  min-height: 72px;
}
.brand-logo { width: 40px; height: 40px; object-fit: contain; border-radius: 8px; flex-shrink: 0; }
.brand-icon {
  width: 40px; height: 40px; border-radius: 10px;
  background: var(--system-primary, #1a56db);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  font-size: 1.2rem; color: white;
}
.brand-text { overflow: hidden; }
.brand-name { display: block; color: white; font-weight: 700; font-size: 0.95rem; white-space: nowrap; }
.brand-sub { display: block; color: var(--sidebar-text); font-size: 0.72rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.sidebar-content { flex: 1; overflow-y: auto; padding: 12px 0; }
.sidebar-section { margin-bottom: 8px; }
.sidebar-label {
  display: block; padding: 8px 20px 4px;
  font-size: 0.65rem; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; color: rgba(148,163,184,0.6);
  white-space: nowrap;
}

.sidebar-footer {
  padding: 12px 16px; border-top: 1px solid rgba(255,255,255,0.08);
}
.user-card { display: flex; align-items: center; gap: 10px; }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.user-avatar-placeholder {
  width: 36px; height: 36px; border-radius: 50%; background: var(--system-primary, #1a56db);
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 0.8rem; flex-shrink: 0;
}
.user-info { overflow: hidden; }
.user-name { display: block; color: white; font-size: 0.82rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { display: block; color: var(--sidebar-text); font-size: 0.7rem; text-transform: capitalize; white-space: nowrap; }

/* Main */
.main-content { margin-left: var(--sidebar-width); min-height: 100vh; display: flex; flex-direction: column; transition: margin-left 0.25s ease; }

/* Topbar */
.topbar {
  height: var(--topbar-height); background: white; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 16px; padding: 0 24px;
  position: sticky; top: 0; z-index: 50;
  box-shadow: 0 1px 0 rgba(0,0,0,0.06);
}
.btn-collapse { background: none; border: none; font-size: 1.4rem; cursor: pointer; color: var(--text-secondary); padding: 4px 8px; border-radius: 8px; }
.btn-collapse:hover { background: var(--surface-secondary); }
.topbar-search { flex: 1; max-width: 360px; position: relative; }
.topbar-search i { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-secondary); }
.search-input { width: 100%; padding: 8px 12px 8px 36px; border: 1px solid var(--border); border-radius: 10px; background: var(--surface-secondary); font-size: 0.875rem; outline: none; }
.search-input:focus { border-color: var(--system-primary, #1a56db); background: white; }
.topbar-actions { display: flex; align-items: center; gap: 8px; margin-left: auto; }
.btn-icon { background: none; border: none; width: 40px; height: 40px; border-radius: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; color: var(--text-secondary); position: relative; }
.btn-icon:hover { background: var(--surface-secondary); color: var(--text-primary); }
.badge-dot { position: absolute; top: 4px; right: 4px; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.6rem; font-weight: 700; color: white; }
.badge-dot.warning { background: #f59e0b; }
.badge-dot.danger { background: #ef4444; }
.topbar-avatar { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; }
.topbar-avatar-placeholder { width: 32px; height: 32px; border-radius: 50%; background: var(--system-primary, #1a56db); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.75rem; }
.user-btn { width: auto; padding: 4px 8px; gap: 6px; }

.user-menu-wrapper { position: relative; }
.user-dropdown {
  position: absolute; right: 0; top: 48px; width: 220px;
  background: white; border: 1px solid var(--border); border-radius: var(--radius);
  box-shadow: var(--shadow-lg); padding: 8px 0; z-index: 100;
}
.dropdown-header { padding: 10px 16px 8px; border-bottom: 1px solid var(--border); margin-bottom: 4px; }
.dropdown-header strong { display: block; font-size: 0.875rem; }
.dropdown-header small { color: var(--text-secondary); font-size: 0.75rem; }
.dropdown-item { display: flex; align-items: center; width: 100%; padding: 8px 16px; background: none; border: none; font-size: 0.875rem; cursor: pointer; color: var(--text-primary); text-align: left; }
.dropdown-item:hover { background: var(--surface-secondary); }
.dropdown-divider { border-color: var(--border); margin: 4px 0; }

/* Page content */
.page-content { flex: 1; padding: 28px 28px; }

/* Transitions */
.page-fade-enter-active, .page-fade-leave-active { transition: opacity 0.2s, transform 0.2s; }
.page-fade-enter-from { opacity: 0; transform: translateY(8px); }
.page-fade-leave-to { opacity: 0; }

.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.show { transform: translateX(0); }
  .main-content { margin-left: 0; }
  .app-wrapper.sidebar-collapsed .main-content { margin-left: 0; }
}
</style>
