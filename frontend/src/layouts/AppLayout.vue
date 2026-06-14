<template>
  <div class="app-wrapper" :class="{ 'sidebar-collapsed': sidebarCollapsed }">

    <!-- Always-in-DOM overlay; toggled by CSS .active -->
    <div
      class="sidebar-overlay"
      :class="{ active: mobileOpen }"
      @click="closeSidebar"
      aria-hidden="true"
    ></div>

    <!-- Offline Banner -->
    <div v-if="!offlineStore.isOnline" class="offline-banner">
      <i class="bi bi-wifi-off me-2"></i>
      <span class="d-none d-sm-inline">You are offline — changes will sync when connection is restored.</span>
      <span class="d-sm-none">Offline</span>
      <span v-if="offlineStore.pendingCount > 0" class="badge bg-warning text-dark ms-2">
        {{ offlineStore.pendingCount }}
      </span>
    </div>

    <!-- Sidebar -->
    <nav class="sidebar" :class="{ 'sidebar-open': mobileOpen }" aria-label="Main navigation">
      <button class="sidebar-close-btn" @click="closeSidebar" aria-label="Close menu">
        <i class="bi bi-x-lg"></i>
      </button>

      <!-- Brand -->
      <div class="sidebar-brand">
        <img v-if="settingsStore.settings.logo_url" :src="settingsStore.settings.logo_url" alt="Logo" class="brand-logo">
        <div v-else class="brand-icon"><i class="bi bi-heart-pulse-fill"></i></div>
        <div class="brand-text">
          <span class="brand-name">{{ settingsStore.settings.short_name || 'PWDMS' }}</span>
          <span class="brand-sub">{{ settingsStore.settings.district_name || 'PWD System' }}</span>
        </div>
      </div>

      <!-- Nav -->
      <div class="sidebar-content">
        <div class="sidebar-section">
          <span class="sidebar-label">Main</span>
          <NavItem to="/dashboard"   icon="bi-grid-fill"           label="Dashboard"   />
          <NavItem to="/pwds"        icon="bi-people-fill"         label="PWD Records" />
          <NavItem to="/album"       icon="bi-journal-richtext"    label="PWD Album"   />
        </div>

        <div class="sidebar-section">
          <span class="sidebar-label">Welfare</span>
          <NavItem to="/partners"    icon="bi-building-fill"         label="Dev. Partners" />
          <NavItem to="/benefits"    icon="bi-gift-fill"             label="Benefits"      />
          <NavItem to="/allocations" icon="bi-check2-circle"         label="Allocations"   />
          <NavItem to="/complaints"  icon="bi-chat-square-text-fill" label="Complaints"   :badge="openComplaints" />
        </div>

        <div class="sidebar-section">
          <span class="sidebar-label">Analytics</span>
          <NavItem to="/reports" icon="bi-bar-chart-fill" label="Reports" :locked="!subStore.can.reports" />
        </div>

        <div class="sidebar-section" v-if="auth.hasRole('super_admin','auditor')">
          <span class="sidebar-label">Admin</span>
          <NavItem to="/audit"    icon="bi-shield-check"      label="Audit Log" :locked="!subStore.can.audit" v-if="auth.hasRole('super_admin','auditor')" />
          <NavItem to="/users"    icon="bi-person-badge-fill" label="Users"     v-if="auth.isAdmin" />
          <NavItem to="/settings" icon="bi-gear-fill"         label="Settings"  v-if="auth.isAdmin" />
        </div>

        <!-- Subscription section -->
        <div class="sidebar-section" v-if="auth.isAdmin">
          <span class="sidebar-label">Account</span>
          <NavItem to="/subscription" icon="bi-credit-card-fill" label="Subscription" />
        </div>
      </div>

      <!-- Subscription mini-status -->
      <div class="sub-mini" v-if="subStore.isActive">
        <div class="sub-mini-info">
          <span class="sub-mini-plan">{{ subStore.planName }}</span>
          <span class="sub-mini-badge" :class="subStore.isTrial ? 'trial' : 'active'">
            {{ subStore.isTrial ? 'Trial' : 'Active' }}
          </span>
        </div>
        <div class="sub-mini-bar">
          <div class="sub-mini-fill" :style="{ width: trialPct + '%', background: trialPct < 30 ? '#ef4444' : '#10b981' }"></div>
        </div>
        <span class="sub-mini-days">{{ subStore.daysRemaining }} days remaining</span>
      </div>

      <!-- User footer -->
      <div class="sidebar-footer">
        <div class="user-card">
          <img v-if="auth.user?.profile_photo" :src="auth.user.profile_photo" class="user-avatar" alt="">
          <div v-else class="user-avatar-placeholder">{{ initials }}</div>
          <div class="user-info">
            <span class="user-name">{{ auth.user?.full_name }}</span>
            <span class="user-role">{{ auth.user?.role?.replace(/_/g,' ') }}</span>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Topbar -->
      <header class="topbar">
        <button class="btn-menu d-lg-none" @click="openSidebar" aria-label="Open menu">
          <i class="bi bi-list"></i>
        </button>
        <button class="btn-menu d-none d-lg-flex" @click="sidebarCollapsed = !sidebarCollapsed" aria-label="Toggle sidebar">
          <i class="bi bi-layout-sidebar-inset"></i>
        </button>

        <div class="topbar-search">
          <i class="bi bi-search"></i>
          <input v-model="globalSearch" type="text" placeholder="Search PWDs…"
            class="search-input" @keyup.enter="doSearch" aria-label="Search">
        </div>

        <div class="topbar-actions">
          <!-- Sync indicator -->
          <button v-if="offlineStore.pendingCount > 0" class="btn-icon" @click="offlineStore.sync()" title="Sync pending">
            <i class="bi bi-arrow-repeat" :class="{ spin: offlineStore.isSyncing }"></i>
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
              <img v-if="auth.user?.profile_photo" :src="auth.user.profile_photo" class="topbar-avatar" alt="">
              <div v-else class="topbar-avatar-placeholder">{{ initials }}</div>
              <i class="bi bi-chevron-down ms-1 d-none d-sm-inline"></i>
            </button>
            <Transition name="dropdown">
              <div v-if="userMenuOpen" class="user-dropdown">
                <div class="dropdown-header">
                  <strong>{{ auth.user?.full_name }}</strong>
                  <small>{{ auth.user?.email }}</small>
                </div>
                <button v-if="auth.isAdmin" class="dropdown-item" @click="navigate('/subscription')">
                  <i class="bi bi-credit-card me-2"></i>Subscription
                  <span class="ms-auto badge" :class="subStore.isTrial ? 'bg-warning-subtle text-warning' : 'bg-success-subtle text-success'">
                    {{ subStore.planName }}
                  </span>
                </button>
                <button v-if="auth.isAdmin" class="dropdown-item" @click="navigate('/settings')">
                  <i class="bi bi-gear me-2"></i>Settings
                </button>
                <hr class="dropdown-divider m-0">
                <button class="dropdown-item text-danger" @click="auth.logout()">
                  <i class="bi bi-box-arrow-right me-2"></i>Logout
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </header>

      <!-- Subscription alert bar -->
      <SubAlertBar />

      <!-- Page Content -->
      <main class="page-content">
        <router-view v-slot="{ Component }">
          <Transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore }         from '@/stores/auth'
import { useSettingsStore }     from '@/stores/settings'
import { useOfflineStore }      from '@/stores/offline'
import { useSubscriptionStore } from '@/stores/subscription'
import NavItem    from '@/components/NavItem.vue'
import SubAlertBar from '@/components/SubAlertBar.vue'
import api from '@/services/api'

const router        = useRouter()
const auth          = useAuthStore()
const settingsStore = useSettingsStore()
const offlineStore  = useOfflineStore()
const subStore      = useSubscriptionStore()

const sidebarCollapsed    = ref(false)
const mobileOpen          = ref(false)
const globalSearch        = ref('')
const userMenuOpen        = ref(false)
const userMenuRef         = ref(null)
const openComplaints      = ref(0)
const unreadNotifications = ref(0)

const initials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  return `${u.first_name?.[0] || ''}${u.last_name?.[0] || ''}`.toUpperCase()
})

// Trial progress bar inside sidebar
const trialPct = computed(() => {
  const total = 30
  return Math.max(0, Math.min(100, (subStore.daysRemaining / total) * 100))
})

// ── Sidebar ──────────────────────────────────────────────────────────────────
function openSidebar()  { mobileOpen.value = true;  document.body.style.overflow = 'hidden' }
function closeSidebar() { mobileOpen.value = false; document.body.style.overflow = '' }

router.afterEach(() => { if (window.innerWidth < 992) closeSidebar() })

// ── User-menu click-away ──────────────────────────────────────────────────────
function handleDocumentClick(e) {
  if (userMenuRef.value && !userMenuRef.value.contains(e.target)) {
    userMenuOpen.value = false
  }
}
function handleKeydown(e) {
  if (e.key === 'Escape') { closeSidebar(); userMenuOpen.value = false }
}

function navigate(path) { userMenuOpen.value = false; router.push(path) }

function doSearch() {
  if (globalSearch.value.trim()) {
    router.push({ path: '/pwds', query: { search: globalSearch.value } })
    globalSearch.value = ''
    closeSidebar()
  }
}

onMounted(async () => {
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('click',   handleDocumentClick, true)

  await settingsStore.fetchSettings()
  await subStore.fetchStatus()

  try {
    const [cmp, notif] = await Promise.all([
      api.get('/complaints/', { params: { status: 'open', page_size: 1 } }),
      api.get('/notifications/', { params: { is_read: false, page_size: 1 } }),
    ])
    openComplaints.value      = cmp.data.count   || 0
    unreadNotifications.value = notif.data.count || 0
  } catch {}
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('click',   handleDocumentClick, true)
  document.body.style.overflow = ''
})
</script>

<style lang="scss">
/* ── CSS Variables ──────────────────────────────────────────── */
:root {
  --sidebar-width: 260px;
  --sidebar-collapsed-width: 68px;
  --topbar-height: 60px;
  --system-primary:   #1a56db;
  --system-secondary: #7e3af2;
  --system-accent:    #ff5a1f;
  --sidebar-bg:    #0f172a;
  --sidebar-text:  #94a3b8;
  --surface:       #ffffff;
  --surface-secondary: #f8fafc;
  --border:        #e2e8f0;
  --text-primary:  #0f172a;
  --text-secondary:#64748b;
  --radius:    12px;
  --radius-sm:  8px;
  --shadow:    0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,.10);
  --shadow-lg: 0 10px 30px rgba(0,0,0,.14);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: var(--surface-secondary);
  color: var(--text-primary);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* ── App shell ───────────────────────────────────────────────── */
.app-wrapper { display: flex; min-height: 100vh; position: relative; }

.offline-banner {
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  background: #dc2626; color: white;
  padding: 7px 20px; text-align: center;
  font-size: .82rem; font-weight: 500;
}

/* ── Overlay ─────────────────────────────────────────────────── */
.sidebar-overlay {
  position: fixed; inset: 0; z-index: 299;
  background: rgba(0,0,0,.55); backdrop-filter: blur(2px);
  opacity: 0; pointer-events: none;
  transition: opacity .28s ease;
}
.sidebar-overlay.active { opacity: 1; pointer-events: auto; }

/* ── Sidebar ─────────────────────────────────────────────────── */
.sidebar {
  width: var(--sidebar-width); height: 100vh;
  background: var(--sidebar-bg);
  display: flex; flex-direction: column;
  position: fixed; left: 0; top: 0; z-index: 300;
  overflow: hidden;
  transition: width .25s cubic-bezier(.4,0,.2,1);
}

.sidebar-close-btn {
  display: none; align-items: center; justify-content: center;
  position: absolute; top: 14px; right: 14px;
  width: 32px; height: 32px;
  background: rgba(255,255,255,.10); border: none;
  border-radius: 8px; color: #e2e8f0; font-size: 1rem;
  cursor: pointer; z-index: 1;
  transition: background .15s;
}
.sidebar-close-btn:hover { background: rgba(255,255,255,.18); }

.sidebar-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 18px 16px;
  border-bottom: 1px solid rgba(255,255,255,.07);
  min-height: 68px; flex-shrink: 0;
}
.brand-logo  { width: 38px; height: 38px; object-fit: contain; border-radius: 8px; flex-shrink: 0; }
.brand-icon  { width: 38px; height: 38px; border-radius: 10px; background: var(--system-primary); display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1.15rem; color: white; }
.brand-text  { overflow: hidden; min-width: 0; }
.brand-name  { display: block; color: white; font-weight: 700; font-size: .92rem; white-space: nowrap; }
.brand-sub   { display: block; color: var(--sidebar-text); font-size: .70rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.sidebar-content { flex: 1; overflow-y: auto; overflow-x: hidden; padding: 10px 0; }
.sidebar-content::-webkit-scrollbar { width: 4px; }
.sidebar-content::-webkit-scrollbar-thumb { background: rgba(255,255,255,.1); border-radius: 2px; }
.sidebar-section { margin-bottom: 4px; }
.sidebar-label { display: block; padding: 8px 18px 4px; font-size: .62rem; font-weight: 700; letter-spacing: .10em; text-transform: uppercase; color: rgba(148,163,184,.50); white-space: nowrap; }

/* ── Subscription mini strip ─────────────────────────────────── */
.sub-mini {
  padding: 10px 16px;
  border-top: 1px solid rgba(255,255,255,.07);
  border-bottom: 1px solid rgba(255,255,255,.07);
  flex-shrink: 0;
}
.sub-mini-info { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.sub-mini-plan { font-size: .75rem; font-weight: 700; color: #e2e8f0; }
.sub-mini-badge { font-size: .62rem; font-weight: 700; padding: 2px 8px; border-radius: 10px; }
.sub-mini-badge.trial  { background: rgba(245,158,11,.2); color: #fbbf24; }
.sub-mini-badge.active { background: rgba(16,185,129,.2); color: #34d399; }
.sub-mini-bar  { height: 4px; background: rgba(255,255,255,.1); border-radius: 2px; overflow: hidden; }
.sub-mini-fill { height: 100%; border-radius: 2px; transition: width .4s ease; }
.sub-mini-days { display: block; font-size: .65rem; color: var(--sidebar-text); margin-top: 5px; }

/* ── Sidebar footer ──────────────────────────────────────────── */
.sidebar-footer { padding: 12px 14px; border-top: 1px solid rgba(255,255,255,.07); flex-shrink: 0; }
.user-card { display: flex; align-items: center; gap: 10px; min-width: 0; }
.user-avatar            { width: 34px; height: 34px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.user-avatar-placeholder { width: 34px; height: 34px; border-radius: 50%; background: var(--system-primary); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: .78rem; flex-shrink: 0; }
.user-info { overflow: hidden; min-width: 0; }
.user-name { display: block; color: white; font-size: .80rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { display: block; color: var(--sidebar-text); font-size: .68rem; text-transform: capitalize; white-space: nowrap; }

/* ── Desktop collapsed ───────────────────────────────────────── */
.app-wrapper.sidebar-collapsed .sidebar { width: var(--sidebar-collapsed-width); }
.app-wrapper.sidebar-collapsed .main-content { margin-left: var(--sidebar-collapsed-width) !important; }
.app-wrapper.sidebar-collapsed .brand-text,
.app-wrapper.sidebar-collapsed .sidebar-label,
.app-wrapper.sidebar-collapsed .user-info,
.app-wrapper.sidebar-collapsed .sub-mini { display: none; }
.app-wrapper.sidebar-collapsed .sidebar-brand { padding: 16px 14px; justify-content: center; }
.app-wrapper.sidebar-collapsed .sidebar-footer { padding: 12px 10px; }
.app-wrapper.sidebar-collapsed .user-card { justify-content: center; }

/* ── Main content ────────────────────────────────────────────── */
.main-content {
  margin-left: var(--sidebar-width);
  min-height: 100vh;
  display: flex; flex-direction: column;
  transition: margin-left .25s cubic-bezier(.4,0,.2,1);
  min-width: 0; width: 100%;
}

/* ── Topbar ──────────────────────────────────────────────────── */
.topbar {
  height: var(--topbar-height);
  background: white; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 10px;
  padding: 0 18px 0 16px;
  position: sticky; top: 0; z-index: 50;
  box-shadow: 0 1px 0 rgba(0,0,0,.05); flex-shrink: 0;
}
.btn-menu { background: none; border: none; font-size: 1.35rem; cursor: pointer; color: var(--text-secondary); width: 40px; height: 40px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: background .14s, color .14s; }
.btn-menu:hover { background: var(--surface-secondary); color: var(--text-primary); }
.topbar-search { flex: 1; max-width: 340px; position: relative; min-width: 0; }
.topbar-search i { position: absolute; left: 11px; top: 50%; transform: translateY(-50%); color: var(--text-secondary); font-size: .9rem; pointer-events: none; }
.search-input { width: 100%; padding: 7px 12px 7px 34px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--surface-secondary); font-size: .855rem; outline: none; color: var(--text-primary); transition: border-color .15s, background .15s, box-shadow .15s; }
.search-input:focus { border-color: var(--system-primary); background: white; box-shadow: 0 0 0 3px rgba(26,86,219,.10); }
.search-input::placeholder { color: var(--text-secondary); }
.topbar-actions { display: flex; align-items: center; gap: 6px; margin-left: auto; flex-shrink: 0; }
.btn-icon { background: none; border: none; width: 38px; height: 38px; border-radius: var(--radius-sm); cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.05rem; color: var(--text-secondary); position: relative; transition: background .14s, color .14s; }
.btn-icon:hover { background: var(--surface-secondary); color: var(--text-primary); }
.badge-dot { position: absolute; top: 3px; right: 3px; min-width: 16px; height: 16px; padding: 0 3px; border-radius: 8px; font-size: .58rem; font-weight: 700; color: white; display: flex; align-items: center; justify-content: center; border: 2px solid white; }
.badge-dot.warning { background: #f59e0b; }
.badge-dot.danger  { background: #ef4444; }
.topbar-avatar            { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; }
.topbar-avatar-placeholder { width: 30px; height: 30px; border-radius: 50%; background: var(--system-primary); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: .72rem; }
.user-btn { width: auto; padding: 4px 8px; gap: 6px; border-radius: 8px; }

.user-menu-wrapper { position: relative; }
.user-dropdown { position: absolute; right: 0; top: calc(100% + 8px); width: 220px; background: white; border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-lg); padding: 6px 0; z-index: 1000; }
.dropdown-enter-active, .dropdown-leave-active { transition: opacity .15s, transform .15s; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-6px); }
.dropdown-header { padding: 10px 14px 8px; border-bottom: 1px solid var(--border); margin-bottom: 4px; }
.dropdown-header strong { display: block; font-size: .85rem; }
.dropdown-header small  { color: var(--text-secondary); font-size: .73rem; }
.dropdown-item { display: flex; align-items: center; width: 100%; padding: 9px 14px; background: none; border: none; font-size: .85rem; cursor: pointer; color: var(--text-primary); text-align: left; transition: background .12s; gap: 4px; }
.dropdown-item:hover { background: var(--surface-secondary); }
.dropdown-divider { border-color: var(--border); }

/* ── Page content ────────────────────────────────────────────── */
.page-content { flex: 1; padding: 24px; overflow-x: hidden; }

.page-fade-enter-active, .page-fade-leave-active { transition: opacity .18s, transform .18s; }
.page-fade-enter-from { opacity: 0; transform: translateY(6px); }
.page-fade-leave-to   { opacity: 0; }

.spin { animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Responsive ──────────────────────────────────────────────── */
@media (max-width: 991.98px) {
  .main-content { margin-left: 0 !important; width: 100%; }
  .sidebar { transform: translateX(-100%); transition: transform .30s cubic-bezier(.4,0,.2,1), box-shadow .30s ease; width: var(--sidebar-width) !important; }
  .sidebar.sidebar-open { transform: translateX(0); box-shadow: 4px 0 32px rgba(0,0,0,.25); }
  .sidebar-close-btn { display: flex; }
  .topbar-search { max-width: 200px; }
  .page-content  { padding: 14px; }
}
@media (max-width: 575.98px) {
  .topbar { padding: 0 10px; gap: 6px; }
  .topbar-search { max-width: 150px; }
  .page-content  { padding: 10px; }
  .topbar-actions { gap: 2px; }
}
@media (max-width: 380px) { .topbar-search { display: none; } }
@media (min-width: 1400px) { :root { --sidebar-width: 272px; } .page-content { padding: 28px 32px; } }

/* ── Global reusables ────────────────────────────────────────── */
.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 24px; gap: 12px; flex-wrap: wrap; }
.page-title  { font-size: clamp(1.25rem, 3vw, 1.75rem); font-weight: 800; line-height: 1.2; }
.page-subtitle { color: var(--text-secondary); font-size: .875rem; margin-top: 3px; }
.table-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.table-card .table thead th { background: var(--surface-secondary); font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; color: var(--text-secondary); border-bottom: 1px solid var(--border); padding: 11px 14px; white-space: nowrap; }
.table-card .table tbody td { padding: 11px 14px; font-size: .855rem; vertical-align: middle; }
.table-card .table tbody tr:hover { background: #fafbff; }
.table-responsive { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.pagination-bar { display: flex; align-items: center; justify-content: center; gap: 14px; padding: 14px 16px; border-top: 1px solid var(--border); flex-wrap: wrap; }
.page-info { font-size: .835rem; color: var(--text-secondary); }
.empty-state { text-align: center; padding: 56px 20px; color: var(--text-secondary); background: white; border-radius: var(--radius); box-shadow: var(--shadow); }
.empty-state i { font-size: 2.8rem; display: block; margin-bottom: 12px; opacity: .5; }
.empty-state p { margin-bottom: 16px; }
</style>
