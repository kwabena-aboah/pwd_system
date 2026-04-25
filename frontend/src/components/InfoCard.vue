<template>
  <div class="info-card">
    <div class="info-card-header">
      <i :class="['bi', icon]"></i>
      <span>{{ title }}</span>
    </div>
    <div class="info-card-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({ title: String, icon: String })
</script>

<style scoped>
.info-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; height: 100%; }
.info-card-header { background: var(--surface-secondary); padding: 14px 18px; font-weight: 700; font-size: 0.9rem; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid var(--border); color: var(--text-primary); }
.info-card-header i { color: var(--bs-primary, #1a56db); }
.info-card-body { padding: 4px 0; }
</style>
