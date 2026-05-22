// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/DashboardView.vue') },

      // PWDs
      { path: 'pwds', name: 'PWDList', component: () => import('@/views/pwds/PWDListView.vue') },
      { path: 'pwds/new', name: 'PWDNew', component: () => import('@/views/pwds/PWDFormView.vue') },
      { path: 'pwds/:id', name: 'PWDDetail', component: () => import('@/views/pwds/PWDDetailView.vue') },
      { path: 'pwds/:id/edit', name: 'PWDEdit', component: () => import('@/views/pwds/PWDFormView.vue') },

      // Album
      { path: 'album', name: 'Album', component: () => import('@/views/AlbumView.vue') },

      // Benefits
      { path: 'partners', name: 'Partners', component: () => import('@/views/benefits/PartnersView.vue') },
      { path: 'benefits', name: 'Benefits', component: () => import('@/views/benefits/BenefitsView.vue') },
      { path: 'allocations', name: 'Allocations', component: () => import('@/views/benefits/AllocationsView.vue') },

      // Complaints
      { path: 'complaints', name: 'Complaints', component: () => import('@/views/complaints/ComplaintsView.vue') },
      { path: 'complaints/:id', name: 'ComplaintDetail', component: () => import('@/views/complaints/ComplaintDetailView.vue') },

      // Reports
      { path: 'reports', name: 'Reports', component: () => import('@/views/ReportsView.vue') },

      // Audit
      { path: 'audit', name: 'Audit', component: () => import('@/views/AuditView.vue'), meta: { roles: ['super_admin', 'auditor'] } },

      // Users
      { path: 'users', name: 'Users', component: () => import('@/views/UsersView.vue'), meta: { roles: ['super_admin'] } },

      // Settings
      { path: 'settings', name: 'Settings', component: () => import('@/views/SettingsView.vue'), meta: { roles: ['super_admin'] } },

      { path: 'notifications', name: 'Notifications', component: () => import('@/views/NotificationsView.vue') },
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.public) return next()
  if (!auth.isAuthenticated) return next('/login')

  if (to.meta.roles && !to.meta.roles.includes(auth.user?.role)) {
    return next('/dashboard')
  }

  next()
})

export default router
