// composables/useFeatureGate.js
// Usage:  const { can, atLimit, requireFeature } = useFeatureGate()
//         can('ai')           → true/false
//         atLimit('pwds')     → true/false
//         requireFeature('ai')→ redirects to /subscription if not allowed

import { useSubscriptionStore } from '@/stores/subscription'
import { useRouter } from 'vue-router'

export function useFeatureGate() {
  const sub    = useSubscriptionStore()
  const router = useRouter()

  function can(featureKey) {
    // Map camelCase keys to store keys
    const map = {
      ai:         'ai',
      albumPdf:   'albumPdf',
      albumPptx:  'albumPptx',
      audit:      'audit',
      reports:    'reports',
      apiAccess:  'apiAccess',
      whiteLabel: 'whiteLabel',
      bulkImport: 'bulkImport',
      offline:    'offline',
    }
    return sub.can[map[featureKey] ?? featureKey] ?? true
  }

  function atLimit(resource) {
    return sub.atLimit(resource)
  }

  function usagePct(resource) {
    return sub.usagePct(resource)
  }

  function requireFeature(featureKey, redirectPath = '/subscription') {
    if (!can(featureKey)) {
      router.push(redirectPath)
      return false
    }
    return true
  }

  function requireUnderLimit(resource, redirectPath = '/subscription') {
    if (atLimit(resource)) {
      router.push(redirectPath)
      return false
    }
    return true
  }

  return { can, atLimit, usagePct, requireFeature, requireUnderLimit, sub }
}
