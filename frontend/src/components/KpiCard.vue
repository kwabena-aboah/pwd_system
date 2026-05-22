<template>
  <div class="kpi-card">
    <div class="kpi-icon" :class="`bg-${color}-subtle text-${color}`">
      <i :class="['bi', icon]"></i>
    </div>
    <div class="kpi-body">
      <div class="kpi-value">{{ formattedValue }}</div>
      <div class="kpi-label">{{ label }}</div>
    </div>
    <div v-if="trend !== undefined" class="kpi-trend" :class="trend >= 0 ? 'text-success' : 'text-danger'">
      <i :class="trend >= 0 ? 'bi-arrow-up-right' : 'bi-arrow-down-right'"></i>
      {{ Math.abs(trend) }}%
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
  trend: { type: Number, default: undefined },
})

const formattedValue = computed(() =>
  typeof props.value === 'number'
    ? props.value.toLocaleString()
    : props.value
)
</script>

<style scoped>
.kpi-card {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.kpi-icon {
  width: 52px; height: 52px; border-radius: 14px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem;
}
.kpi-body { flex: 1; }
.kpi-value { font-size: 1.8rem; font-weight: 800; line-height: 1; color: var(--text-primary); }
.kpi-label { font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px; font-weight: 500; }
.kpi-trend { font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; gap: 2px; }
</style>
