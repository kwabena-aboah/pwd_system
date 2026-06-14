<template>
  <div class="info-row">
    <span class="info-label">{{ label }}</span>
    <span class="info-value">{{ value ?? '—' }}</span>
  </div>
</template>
<script setup>
defineProps({ label: String, value: [String, Number] })
</script>
<style scoped>
.info-row { display: flex; justify-content: space-between; align-items: flex-start; padding: 9px 16px; border-bottom: 1px solid var(--border); gap: 8px; font-size: 0.855rem; }
.info-row:last-child { border-bottom: none; }
.info-label { color: var(--text-secondary); font-weight: 500; flex-shrink: 0; }
.info-value { color: var(--text-primary); font-weight: 600; text-align: right; word-break: break-word; min-width: 0; }
@media (max-width: 380px) { .info-row { flex-direction: column; gap: 2px; } .info-value { text-align: left; } }
</style>
