// stores/subscription.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useSubscriptionStore = defineStore('subscription', () => {
  const status = ref(null)
  const loading = ref(false)

  // ── Computed shortcuts ────────────────────────────────────────────
  const isActive      = computed(() => status.value?.status === 'active' || status.value?.status === 'trialing')
  const isTrial       = computed(() => status.value?.status === 'trialing')
  const isExpired     = computed(() => status.value?.status === 'expired')
  const daysRemaining = computed(() => status.value?.days_remaining ?? 0)
  const planTier      = computed(() => status.value?.plan_tier ?? 'free')
  const planName      = computed(() => status.value?.plan_name ?? 'No Plan')

  // Feature checks
  const can = computed(() => ({
    ai:          status.value?.feature_ai          ?? false,
    albumPdf:    status.value?.feature_album_pdf   ?? true,
    albumPptx:   status.value?.feature_album_pptx  ?? false,
    audit:       status.value?.feature_audit       ?? false,
    reports:     status.value?.feature_reports     ?? false,
    apiAccess:   status.value?.feature_api_access  ?? false,
    whiteLabel:  status.value?.feature_white_label ?? false,
    bulkImport:  status.value?.feature_bulk_import ?? false,
    offline:     status.value?.feature_offline     ?? true,
  }))

  // Limit checks
  const limits = computed(() => ({
    users:    status.value?.max_users    ?? 3,
    pwds:     status.value?.max_pwds     ?? 50,
    partners: status.value?.max_partners ?? 2,
    storageGb: status.value?.storage_gb ?? 1,
  }))

  const usage = computed(() => ({
    users:    status.value?.current_users    ?? 0,
    pwds:     status.value?.current_pwds     ?? 0,
    partners: status.value?.current_partners ?? 0,
  }))

  function atLimit(resource) {
    const limit   = limits.value[resource]
    const current = usage.value[resource]
    if (limit === 0) return false          // 0 = unlimited
    return current >= limit
  }

  function usagePct(resource) {
    const limit   = limits.value[resource]
    const current = usage.value[resource]
    if (!limit) return 0
    return Math.min(Math.round((current / limit) * 100), 100)
  }

  // ── Actions ───────────────────────────────────────────────────────
  async function fetchStatus() {
    loading.value = true
    try {
      const { data } = await api.get('/subscriptions/current/')
      status.value = data
    } catch (e) {
      console.warn('Could not fetch subscription status', e)
    } finally {
      loading.value = false
    }
  }

  async function startTrial(payload) {
    const { data } = await api.post('/subscriptions/start-trial/', payload)
    await fetchStatus()
    return data
  }

  return {
    status, loading,
    isActive, isTrial, isExpired, daysRemaining, planTier, planName,
    can, limits, usage, atLimit, usagePct,
    fetchStatus, startTrial,
  }
})
