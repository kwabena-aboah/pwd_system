// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // ── Public pages ────────────────────────────────────────────────────────────
  { path: '/login',   name: 'Login',   component: () => import('@/views/LoginView.vue'),              meta: { public: true } },
  { path: '/pricing', name: 'Pricing', component: () => import('@/views/subscription/PricingPage.vue'), meta: { public: true } },

  // ── Authenticated app shell ──────────────────────────────────────────────────
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },

      // Core
      { path: 'dashboard',  name: 'Dashboard', component: () => import('@/views/DashboardView.vue') },

      // PWDs
      { path: 'pwds',         name: 'PWDList',   component: () => import('@/views/pwds/PWDListView.vue') },
      { path: 'pwds/new',     name: 'PWDNew',    component: () => import('@/views/pwds/PWDFormView.vue') },
      { path: 'pwds/:id',     name: 'PWDDetail', component: () => import('@/views/pwds/PWDDetailView.vue') },
      { path: 'pwds/:id/edit',name: 'PWDEdit',   component: () => import('@/views/pwds/PWDFormView.vue') },

      // Album
      { path: 'album', name: 'Album', component: () => import('@/views/AlbumView.vue') },

      // Benefits
      { path: 'partners',    name: 'Partners',    component: () => import('@/views/benefits/PartnersView.vue') },
      { path: 'benefits',    name: 'Benefits',    component: () => import('@/views/benefits/BenefitsView.vue') },
      { path: 'allocations', name: 'Allocations', component: () => import('@/views/benefits/AllocationsView.vue') },

      // Complaints
      { path: 'complaints',     name: 'Complaints',      component: () => import('@/views/complaints/ComplaintsView.vue') },
      { path: 'complaints/:id', name: 'ComplaintDetail', component: () => import('@/views/complaints/ComplaintDetailView.vue') },

      // Analytics & Reporting
      { path: 'reports', name: 'Reports', component: () => import('@/views/ReportsView.vue'), meta: { feature: 'reports' } },

      // Admin
      { path: 'audit',    name: 'Audit',    component: () => import('@/views/AuditView.vue'),    meta: { roles: ['super_admin','auditor'], feature: 'audit' } },
      { path: 'users',    name: 'Users',    component: () => import('@/views/UsersView.vue'),    meta: { roles: ['super_admin'] } },
      { path: 'settings', name: 'Settings', component: () => import('@/views/SettingsView.vue'), meta: { roles: ['super_admin'] } },

      // Notifications
      { path: 'notifications', name: 'Notifications', component: () => import('@/views/NotificationsView.vue') },

      // Subscription management
      { path: 'subscription', name: 'Subscription', component: () => import('@/views/subscription/SubscriptionView.vue'), meta: { roles: ['super_admin'] } },
    ],
  },

  // Catch-all
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // Always allow public pages
  if (to.meta.public) return next()

  // Require authentication
  if (!auth.isAuthenticated) return next('/login')

  // Role guard
  if (to.meta.roles && !to.meta.roles.includes(auth.user?.role)) {
    return next('/dashboard')
  }

  // Feature gate — lazy-load subscription store to avoid circular imports
  if (to.meta.feature) {
    const { useSubscriptionStore } = await import('@/stores/subscription')
    const sub = useSubscriptionStore()
    if (!sub.status) await sub.fetchStatus()
    const featureKey = to.meta.feature.replace(/-/g, '_')
    const allowed = sub.can[featureKey] ?? sub.can[to.meta.feature] ?? true
    if (!allowed) return next('/subscription')
  }

  next()
})

export default router
