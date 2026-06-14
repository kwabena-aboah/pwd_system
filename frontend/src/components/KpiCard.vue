<template>
  <div class="kpi-card">
    <div class="kpi-icon" :class="`kpi-${color}`">
      <i :class="['bi', icon]"></i>
    </div>
    <div class="kpi-body">
      <div class="kpi-value">{{ formattedValue }}</div>
      <div class="kpi-label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  icon: { type: String, required: true },
  color: { type: String, default: 'primary' },
  value: { type: [Number, String], default: 0 },
  label: { type: String, required: true },
})
const formattedValue = computed(() =>
  typeof props.value === 'number' ? props.value.toLocaleString() : props.value
)
</script>

<style scoped>
.kpi-card {
  background: white; border-radius: var(--radius);
  padding: 16px; box-shadow: var(--shadow);
  display: flex; align-items: center; gap: 14px;
  transition: transform 0.18s, box-shadow 0.18s;
  overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.kpi-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; flex-shrink: 0;
}
.kpi-primary { background: #eff6ff; color: #1d4ed8; }
.kpi-success { background: #f0fdf4; color: #15803d; }
.kpi-danger  { background: #fef2f2; color: #dc2626; }
.kpi-warning { background: #fffbeb; color: #d97706; }
.kpi-info    { background: #f0f9ff; color: #0369a1; }
.kpi-secondary { background: #f8fafc; color: #475569; }
.kpi-body { min-width: 0; }
.kpi-value { font-size: 1.6rem; font-weight: 800; line-height: 1; color: var(--text-primary); }
.kpi-label { font-size: 0.775rem; color: var(--text-secondary); margin-top: 4px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

@media (max-width: 480px) {
  .kpi-card { padding: 13px 12px; gap: 10px; }
  .kpi-icon { width: 40px; height: 40px; border-radius: 10px; font-size: 1.1rem; }
  .kpi-value { font-size: 1.35rem; }
}
</style>
