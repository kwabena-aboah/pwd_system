<template>
  <div class="info-card">
    <div class="info-card-header">
      <i :class="['bi', icon]"></i>
      <span>{{ title }}</span>
    </div>
    <div class="info-card-body"><slot /></div>
  </div>
</template>
<script setup>
defineProps({ title: String, icon: String })
</script>
<style scoped>
.info-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.info-card-header { background: var(--surface-secondary); padding: 12px 16px; font-weight: 700; font-size: 0.875rem; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid var(--border); }
.info-card-header i { color: var(--system-primary); }
</style>
