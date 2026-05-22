<template>
  <router-link :to="to" class="nav-item" :class="{ active: isActive }">
    <i :class="['bi', icon, 'nav-icon']"></i>
    <span class="nav-label">{{ label }}</span>
    <span v-if="badge" class="nav-badge">{{ badge }}</span>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  to: String,
  icon: String,
  label: String,
  badge: [Number, String],
})

const route = useRoute()
const isActive = computed(() =>
  props.to === '/' ? route.path === '/' : route.path.startsWith(props.to)
)
</script>

<style scoped>
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 20px; margin: 2px 8px;
  border-radius: 10px; text-decoration: none;
  color: var(--sidebar-text); font-size: 0.875rem; font-weight: 500;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap; position: relative;
}
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; }
.nav-item.active { background: var(--sidebar-active-bg); color: var(--sidebar-active); }
.nav-item.active .nav-icon { color: var(--system-primary, #1a56db); }
.nav-icon { font-size: 1.05rem; width: 20px; text-align: center; flex-shrink: 0; }
.nav-label { flex: 1; }
.nav-badge {
  background: #ef4444; color: white;
  font-size: 0.65rem; font-weight: 700;
  min-width: 18px; height: 18px; border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 5px;
}
</style>
