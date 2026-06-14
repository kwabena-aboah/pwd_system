<template>
  <div class="sub-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Subscription</h1>
        <p class="page-subtitle">Manage your plan, billing and invoices</p>
      </div>
      <router-link to="/pricing" target="_blank" class="btn btn-outline-primary btn-sm">
        <i class="bi bi-arrow-up-circle me-1"></i>View Plans
      </router-link>
    </div>

    <div v-if="subStore.loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>

    <div v-else-if="!subStore.isActive" class="no-sub-card">
      <div class="no-sub-icon"><i class="bi bi-lock-fill"></i></div>
      <h3>No Active Subscription</h3>
      <p>Subscribe to unlock all features for your District Assembly.</p>
      <router-link to="/pricing" class="btn btn-primary px-4 py-2">
        <i class="bi bi-rocket-takeoff me-2"></i>Choose a Plan
      </router-link>
    </div>

    <template v-else>
      <!-- Status banner -->
      <div class="status-banner" :class="bannerClass">
        <div class="banner-left">
          <div class="banner-icon"><i :class="['bi', bannerIcon]"></i></div>
          <div>
            <strong>{{ subStore.planName }}</strong>
            <span class="badge ms-2" :class="statusBadge">{{ subStore.status?.status }}</span>
            <p class="mb-0 small mt-1">{{ bannerMessage }}</p>
          </div>
        </div>
        <div class="banner-right">
          <div class="days-ring">
            <svg viewBox="0 0 36 36" class="ring-svg">
              <circle cx="18" cy="18" r="15" fill="none" stroke="#e2e8f0" stroke-width="3"/>
              <circle cx="18" cy="18" r="15" fill="none" :stroke="ringColor"
                stroke-width="3" stroke-linecap="round"
                :stroke-dasharray="`${daysPct * 94.2 / 100} 94.2`"
                stroke-dashoffset="23.55" transform="rotate(-90 18 18)"/>
            </svg>
            <div class="ring-label">
              <span class="ring-num">{{ subStore.daysRemaining }}</span>
              <span class="ring-sub">days</span>
            </div>
          </div>
          <div class="banner-actions">
            <button v-if="subStore.isTrial" class="btn btn-sm btn-primary" @click="showUpgrade = true">
              <i class="bi bi-arrow-up-circle me-1"></i>Upgrade Now
            </button>
            <button v-else class="btn btn-sm btn-outline-secondary" @click="showUpgrade = true">
              <i class="bi bi-arrow-up-circle me-1"></i>Change Plan
            </button>
          </div>
        </div>
      </div>

      <!-- Usage meters -->
      <div class="usage-section">
        <h5 class="usage-title">Current Usage</h5>
        <div class="usage-grid">
          <div class="usage-meter" v-for="m in meters" :key="m.label">
            <div class="meter-header">
              <span class="meter-label"><i :class="['bi', m.icon, 'me-2']"></i>{{ m.label }}</span>
              <span class="meter-count">
                {{ m.current }}
                <span class="text-muted">/ {{ m.max === 0 ? '∞' : m.max }}</span>
              </span>
            </div>
            <div class="meter-bar">
              <div class="meter-fill"
                :style="{ width: m.pct + '%', background: m.pct >= 90 ? '#ef4444' : m.pct >= 70 ? '#f59e0b' : '#10b981' }">
              </div>
            </div>
            <div class="meter-footer" v-if="m.max > 0">
              <span :class="m.pct >= 90 ? 'text-danger fw-bold' : 'text-muted'">{{ m.pct }}% used</span>
              <span class="text-muted">{{ m.max - m.current }} remaining</span>
            </div>
            <div class="meter-footer" v-else>
              <span class="text-success fw-semibold">Unlimited</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Feature flags -->
      <div class="features-section">
        <h5 class="usage-title">Plan Features</h5>
        <div class="features-grid">
          <div class="feature-flag" v-for="f in featureList" :key="f.key" :class="{ enabled: f.enabled }">
            <div class="flag-icon" :class="f.enabled ? 'flag-enabled' : 'flag-disabled'">
              <i :class="['bi', f.icon]"></i>
            </div>
            <div>
              <div class="flag-name">{{ f.name }}</div>
              <div class="flag-status">{{ f.enabled ? 'Included' : 'Not on this plan' }}</div>
            </div>
            <span class="ms-auto">
              <i :class="['bi', f.enabled ? 'bi-check-circle-fill text-success' : 'bi-x-circle text-muted']"></i>
            </span>
          </div>
        </div>
      </div>

      <!-- Invoices -->
      <div class="invoices-section">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="usage-title mb-0">Billing History</h5>
        </div>
        <div class="table-card">
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead>
                <tr>
                  <th>Invoice #</th><th>Period</th><th>Amount</th>
                  <th>Status</th><th>Paid</th><th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="inv in invoices" :key="inv.id">
                  <td><code>{{ inv.invoice_number }}</code></td>
                  <td class="text-muted small">{{ inv.period_start }} → {{ inv.period_end }}</td>
                  <td><strong>GHS {{ Number(inv.amount).toLocaleString() }}</strong></td>
                  <td>
                    <span class="badge" :class="invBadge(inv.status)">{{ inv.status }}</span>
                  </td>
                  <td class="text-muted small">{{ inv.paid_at ? inv.paid_at.slice(0,10) : '—' }}</td>
                  <td>
                    <button class="btn btn-xs btn-outline-secondary"
                      v-if="inv.status === 'open'" @click="markPaid(inv.id)">
                      Mark Paid
                    </button>
                  </td>
                </tr>
                <tr v-if="!invoices.length">
                  <td colspan="6" class="text-center text-muted py-4">No invoices yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>

    <!-- Upgrade modal -->
    <Transition name="modal">
      <div class="modal-overlay" v-if="showUpgrade" @click.self="showUpgrade = false">
        <div class="modal-box upgrade-modal">
          <button class="modal-close" @click="showUpgrade = false"><i class="bi bi-x-lg"></i></button>
          <h4 class="mb-1">Upgrade Your Plan</h4>
          <p class="text-muted mb-4">Switch to a higher plan to unlock more features.</p>

          <div class="upgrade-plans">
            <div class="upgrade-plan-row" v-for="plan in availablePlans" :key="plan.id"
              :class="{ current: plan.tier === subStore.planTier, recommended: plan.is_popular }"
              @click="selectUpgradePlan(plan)">
              <div>
                <strong>{{ plan.name }}</strong>
                <span class="badge bg-primary-subtle text-primary ms-2" v-if="plan.is_popular">Popular</span>
                <span class="badge bg-secondary-subtle text-secondary ms-2" v-if="plan.tier === subStore.planTier">Current</span>
                <p class="mb-0 text-muted small mt-1">{{ plan.description }}</p>
              </div>
              <div class="text-end flex-shrink-0">
                <span class="upgrade-price">GHS {{ Number(plan.price_monthly).toLocaleString() }}<small>/mo</small></span>
              </div>
            </div>
          </div>

          <div class="mt-4 p-3 bg-light rounded" v-if="selectedUpgradePlan">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="fw-semibold">Upgrading to {{ selectedUpgradePlan.name }}</span>
              <span class="fw-bold text-primary">GHS {{ Number(selectedUpgradePlan.price_monthly).toLocaleString() }}/mo</span>
            </div>
            <select v-model="upgradePaymentMethod" class="form-select form-select-sm mb-2">
              <option value="bank_transfer">Bank Transfer</option>
              <option value="paystack">Paystack (Card/MoMo)</option>
              <option value="cash">Cash</option>
              <option value="manual">Manual</option>
            </select>
            <input v-if="upgradePaymentMethod !== 'paystack'" v-model="upgradeRef"
              class="form-control form-control-sm" placeholder="Payment reference (optional)">
          </div>

          <button class="btn btn-primary w-100 mt-3 py-2" @click="confirmUpgrade"
            :disabled="!selectedUpgradePlan || upgradeLoading">
            <span v-if="upgradeLoading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-check-lg me-2"></i>
            Confirm Upgrade
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSubscriptionStore } from '@/stores/subscription'
import api from '@/services/api'

const subStore = useSubscriptionStore()
const invoices = ref([])
const availablePlans = ref([])
const showUpgrade = ref(false)
const selectedUpgradePlan = ref(null)
const upgradePaymentMethod = ref('bank_transfer')
const upgradeRef = ref('')
const upgradeLoading = ref(false)

const bannerClass = computed(() => ({
  'banner-trial': subStore.isTrial,
  'banner-active': !subStore.isTrial && subStore.isActive,
  'banner-danger': subStore.daysRemaining < 7,
}))
const bannerIcon = computed(() => ({
  trialing: 'bi-hourglass-split', active: 'bi-check-circle-fill',
  past_due: 'bi-exclamation-triangle-fill', expired: 'bi-x-circle-fill',
}[subStore.status?.status] || 'bi-circle'))
const bannerMessage = computed(() => {
  if (subStore.isTrial) return `Trial ends in ${subStore.daysRemaining} days. Upgrade to avoid interruption.`
  return `Your ${subStore.planName} subscription renews in ${subStore.daysRemaining} days.`
})
const statusBadge = computed(() => ({
  trialing: 'bg-warning-subtle text-warning', active: 'bg-success-subtle text-success',
  past_due: 'bg-danger-subtle text-danger', expired: 'bg-dark text-white',
}[subStore.status?.status] || 'bg-secondary-subtle text-secondary'))
const ringColor = computed(() => subStore.daysRemaining < 7 ? '#ef4444' : '#1a56db')
const daysPct = computed(() => {
  const total = subStore.isTrial ? (subStore.status?.plan_detail?.trial_days ?? 14) : 30
  return Math.max(0, Math.min(100, (subStore.daysRemaining / total) * 100))
})

const meters = computed(() => [
  { label: 'PWD Records',  icon: 'bi-people-fill',   current: subStore.usage.pwds,     max: subStore.limits.pwds,     pct: subStore.usagePct('pwds') },
  { label: 'Users',        icon: 'bi-person-fill',   current: subStore.usage.users,    max: subStore.limits.users,    pct: subStore.usagePct('users') },
  { label: 'Dev. Partners',icon: 'bi-building-fill', current: subStore.usage.partners, max: subStore.limits.partners, pct: subStore.usagePct('partners') },
])

const featureList = computed(() => [
  { key:'ai',          name:'AI Risk Analysis',    icon:'bi-robot',          enabled: subStore.can.ai },
  { key:'albumPdf',    name:'PDF Album Export',    icon:'bi-file-earmark-pdf', enabled: subStore.can.albumPdf },
  { key:'albumPptx',   name:'PPTX Album Export',   icon:'bi-file-earmark-slides', enabled: subStore.can.albumPptx },
  { key:'audit',       name:'Audit Trail',          icon:'bi-shield-check',   enabled: subStore.can.audit },
  { key:'reports',     name:'Advanced Reports',     icon:'bi-bar-chart-fill', enabled: subStore.can.reports },
  { key:'whiteLabel',  name:'Custom Branding',      icon:'bi-palette-fill',   enabled: subStore.can.whiteLabel },
  { key:'bulkImport',  name:'Bulk Import',          icon:'bi-upload',         enabled: subStore.can.bulkImport },
  { key:'apiAccess',   name:'API Access',           icon:'bi-code-slash',     enabled: subStore.can.apiAccess },
  { key:'offline',     name:'Offline / PWA',        icon:'bi-wifi-off',       enabled: subStore.can.offline },
])

const invBadge = s => ({
  paid:'bg-success-subtle text-success', open:'bg-warning-subtle text-warning',
  void:'bg-secondary-subtle text-secondary', draft:'bg-light text-muted',
}[s] || 'bg-secondary-subtle text-secondary')

function selectUpgradePlan(plan) {
  if (plan.tier === subStore.planTier) return
  selectedUpgradePlan.value = plan
}

async function confirmUpgrade() {
  if (!selectedUpgradePlan.value) return
  upgradeLoading.value = true
  try {
    const subs = await api.get('/subscriptions/')
    const subId = (subs.data.results ?? subs.data)[0]?.id
    if (subId) {
      await api.post(`/subscriptions/${subId}/change-plan/`, { plan_id: selectedUpgradePlan.value.id })
      await api.post(`/subscriptions/${subId}/activate/`, {
        billing_cycle: 'monthly',
        payment_method: upgradePaymentMethod.value,
        payment_ref: upgradeRef.value,
      })
    }
    showUpgrade.value = false
    await subStore.fetchStatus()
    await loadInvoices()
  } finally { upgradeLoading.value = false }
}

async function markPaid(invoiceId) {
  await api.post(`/invoices/${invoiceId}/mark-paid/`, { payment_method: 'manual' })
  await loadInvoices()
}

async function loadInvoices() {
  const { data } = await api.get('/invoices/')
  invoices.value = data.results ?? data
}

onMounted(async () => {
  await subStore.fetchStatus()
  await loadInvoices()
  const { data } = await api.get('/plans/')
  availablePlans.value = (data.results ?? data).filter(p => p.tier !== 'free')
})
</script>

<style scoped>
.sub-page { max-width: 900px; }

.no-sub-card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); padding: 60px 20px; text-align: center; }
.no-sub-icon { width: 72px; height: 72px; border-radius: 50%; background: #fef2f2; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; color: #ef4444; margin: 0 auto 20px; }
.no-sub-card h3 { font-weight: 800; margin-bottom: 10px; }
.no-sub-card p { color: #64748b; margin-bottom: 24px; }

.status-banner {
  border-radius: var(--radius); padding: 24px 28px; margin-bottom: 20px;
  display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap;
  background: #eff6ff; border: 1.5px solid #bfdbfe;
}
.banner-trial  { background: #fffbeb; border-color: #fde68a; }
.banner-danger { background: #fef2f2; border-color: #fecaca; }
.banner-left  { display: flex; align-items: center; gap: 16px; flex: 1; }
.banner-right { display: flex; align-items: center; gap: 16px; }
.banner-icon { width: 44px; height: 44px; border-radius: 12px; background: #1a56db; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; color: white; flex-shrink: 0; }
.banner-trial .banner-icon { background: #f59e0b; }
.banner-danger .banner-icon { background: #ef4444; }

.days-ring { position: relative; width: 64px; height: 64px; flex-shrink: 0; }
.ring-svg { width: 100%; height: 100%; }
.ring-label { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ring-num { font-size: .95rem; font-weight: 800; line-height: 1; }
.ring-sub { font-size: .55rem; color: #64748b; }

.usage-section, .features-section, .invoices-section { background: white; border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow); margin-bottom: 20px; }
.usage-title { font-size: .95rem; font-weight: 700; margin-bottom: 20px; }
.usage-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px; }
@media (max-width: 640px) { .usage-grid { grid-template-columns: 1fr; } }
.usage-meter { }
.meter-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: .85rem; }
.meter-label { font-weight: 600; }
.meter-count { font-weight: 700; }
.meter-bar { height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden; }
.meter-fill { height: 100%; border-radius: 4px; transition: width .4s ease; }
.meter-footer { display: flex; justify-content: space-between; font-size: .75rem; margin-top: 5px; }

.features-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; }
.feature-flag { background: #f8fafc; border-radius: 10px; padding: 12px 14px; display: flex; align-items: center; gap: 12px; border: 1px solid var(--border); }
.feature-flag.enabled { background: #f0fdf4; border-color: #bbf7d0; }
.flag-icon { width: 36px; height: 36px; border-radius: 9px; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.flag-enabled  { background: #dcfce7; color: #16a34a; }
.flag-disabled { background: #f1f5f9; color: #94a3b8; }
.flag-name { font-size: .855rem; font-weight: 600; }
.flag-status { font-size: .73rem; color: #64748b; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.55); backdrop-filter: blur(4px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-box { background: white; border-radius: 20px; padding: 32px 28px; width: 100%; max-width: 500px; max-height: 90vh; overflow-y: auto; position: relative; }
.upgrade-modal { max-width: 540px; }
.modal-close { position: absolute; top: 16px; right: 16px; background: #f1f5f9; border: none; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; }

.upgrade-plans { display: flex; flex-direction: column; gap: 10px; }
.upgrade-plan-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 16px; border: 1.5px solid var(--border); border-radius: 10px;
  cursor: pointer; transition: border-color .15s, background .15s; gap: 16px;
}
.upgrade-plan-row:hover:not(.current) { border-color: #1a56db; background: #f0f6ff; }
.upgrade-plan-row.current { border-color: #94a3b8; opacity: .5; cursor: default; }
.upgrade-plan-row.recommended { border-color: #1a56db; }
.upgrade-price { font-size: 1.05rem; font-weight: 800; color: #1a56db; }
.upgrade-price small { font-size: .7rem; font-weight: 500; color: #94a3b8; }

.modal-enter-active, .modal-leave-active { transition: opacity .2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

.btn-xs { padding: 3px 10px; font-size: .75rem; }
</style>
