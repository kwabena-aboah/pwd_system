<template>
  <router-link
    v-if="!locked"
    :to="to"
    class="nav-item"
    :class="{ active: isActive }"
    :title="label"
  >
    <i :class="['bi', icon, 'nav-icon']"></i>
    <span class="nav-label">{{ label }}</span>
    <span v-if="badge" class="nav-badge">{{ badge > 99 ? '99+' : badge }}</span>
  </router-link>

  <!-- Locked item — click goes to /subscription -->
  <router-link
    v-else
    to="/subscription"
    class="nav-item nav-item-locked"
    :title="`${label} — Upgrade to unlock`"
  >
    <i :class="['bi', icon, 'nav-icon']"></i>
    <span class="nav-label">{{ label }}</span>
    <i class="bi bi-lock-fill nav-lock"></i>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  to:     { type: String,  required: true },
  icon:   { type: String,  required: true },
  label:  { type: String,  required: true },
  badge:  { type: [Number, String], default: null },
  locked: { type: Boolean, default: false },
})

const route    = useRoute()
const isActive = computed(() =>
  props.to === '/dashboard'
    ? route.path === '/dashboard' || route.path === '/'
    : route.path.startsWith(props.to)
)
</script>

<style scoped>
.nav-item {
  display: flex; align-items: center; gap: 11px;
  padding: 9px 16px; margin: 1px 8px;
  border-radius: 9px; text-decoration: none;
  color: var(--sidebar-text, #94a3b8);
  font-size: .855rem; font-weight: 500;
  transition: background .14s, color .14s;
  white-space: nowrap; position: relative; overflow: hidden;
  -webkit-tap-highlight-color: transparent;
}
.nav-item:hover { background: rgba(255,255,255,.07); color: #e2e8f0; }
.nav-item.active { background: rgba(255,255,255,.13); color: #ffffff; }
.nav-item.active::before {
  content: ''; position: absolute; left: 0; top: 20%; bottom: 20%;
  width: 3px; border-radius: 0 3px 3px 0;
  background: var(--system-primary, #1a56db);
}
.nav-item-locked { opacity: .5; cursor: pointer; }
.nav-item-locked:hover { opacity: .75; background: rgba(255,255,255,.05); }

.nav-icon { font-size: 1rem; width: 20px; text-align: center; flex-shrink: 0; }
.nav-item.active .nav-icon { color: #60a5fa; }
.nav-label { flex: 1; }
.nav-lock  { font-size: .65rem; color: #f59e0b; margin-left: auto; }

.nav-badge {
  background: #ef4444; color: white;
  font-size: .60rem; font-weight: 700;
  min-width: 17px; height: 17px; border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 4px; flex-shrink: 0;
}

:global(.sidebar-collapsed) .nav-label  { display: none; }
:global(.sidebar-collapsed) .nav-badge  { display: none; }
:global(.sidebar-collapsed) .nav-lock   { display: none; }
:global(.sidebar-collapsed) .nav-item   { justify-content: center; padding: 9px 0; margin: 1px 10px; }
:global(.sidebar-collapsed) .nav-icon   { width: auto; }

@media (max-width: 991.98px) { .nav-item { padding: 11px 16px; } }
</style>
