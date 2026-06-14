<template>
  <!-- Trial warning bar — shown when ≤7 days remain on trial -->
  <Transition name="slide-down">
    <div v-if="show" class="sub-alert-bar" :class="alertClass">
      <div class="alert-inner">
        <i :class="['bi', alertIcon, 'me-2']"></i>
        <span>{{ alertMessage }}</span>
        <router-link to="/subscription" class="alert-link">
          {{ subStore.isTrial ? 'Upgrade Now' : 'Manage Subscription' }}
        </router-link>
        <button class="alert-dismiss" @click="dismissed = true" aria-label="Dismiss">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useSubscriptionStore } from '@/stores/subscription'

const subStore  = useSubscriptionStore()
const dismissed = ref(false)

const show = computed(() =>
  !dismissed.value &&
  subStore.isActive &&
  (subStore.daysRemaining <= 7 || subStore.status?.status === 'past_due')
)

const alertClass = computed(() => ({
  'alert-warning': subStore.daysRemaining > 3,
  'alert-danger':  subStore.daysRemaining <= 3 || subStore.status?.status === 'past_due',
}))

const alertIcon = computed(() =>
  subStore.status?.status === 'past_due' ? 'bi-exclamation-triangle-fill' : 'bi-hourglass-split'
)

const alertMessage = computed(() => {
  if (subStore.status?.status === 'past_due')
    return 'Your payment is overdue. Please settle to avoid service interruption.'
  if (subStore.isTrial)
    return `Your free trial expires in ${subStore.daysRemaining} day${subStore.daysRemaining === 1 ? '' : 's'}.`
  return `Your ${subStore.planName} subscription renews in ${subStore.daysRemaining} day${subStore.daysRemaining === 1 ? '' : 's'}.`
})
</script>

<style scoped>
.sub-alert-bar {
  width: 100%;
  padding: 8px 0;
  font-size: .845rem;
  font-weight: 500;
  z-index: 49;
  flex-shrink: 0;
}
.alert-warning { background: #fffbeb; border-bottom: 1px solid #fde68a; color: #92400e; }
.alert-danger  { background: #fef2f2; border-bottom: 1px solid #fecaca; color: #991b1b; }

.alert-inner {
  max-width: 1200px; margin: 0 auto;
  padding: 0 24px;
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.alert-link {
  background: currentColor;
  color: inherit;
  /* override as button-like */
  display: inline-flex; align-items: center;
  padding: 3px 12px;
  border-radius: 6px;
  font-weight: 700;
  font-size: .78rem;
  text-decoration: none;
  white-space: nowrap;
  opacity: .9;
  background: rgba(0,0,0,.1);
}
.alert-link:hover { opacity: 1; }
.alert-dismiss {
  margin-left: auto;
  background: none; border: none;
  cursor: pointer; font-size: 1rem;
  color: inherit; opacity: .6;
  padding: 2px 4px;
}
.alert-dismiss:hover { opacity: 1; }

.slide-down-enter-active, .slide-down-leave-active { transition: max-height .25s ease, opacity .25s ease; overflow: hidden; }
.slide-down-enter-from, .slide-down-leave-to { max-height: 0; opacity: 0; }
.slide-down-enter-to, .slide-down-leave-from { max-height: 80px; opacity: 1; }
</style>
