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
.info-row { display: flex; justify-content: space-between; padding: 10px 18px; border-bottom: 1px solid var(--border); font-size: 0.875rem; }
.info-row:last-child { border-bottom: none; }
.info-label { color: var(--text-secondary); font-weight: 500; }
.info-value { color: var(--text-primary); font-weight: 600; text-align: right; max-width: 60%; word-break: break-word; }
</style>
