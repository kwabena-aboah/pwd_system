<template>
  <div class="pricing-page">
    <!-- ── Nav ── -->
    <nav class="pricing-nav">
      <div class="nav-inner">
        <div class="nav-brand">
          <div class="nav-logo"><i class="bi bi-heart-pulse-fill"></i></div>
          <span>PWDMS</span>
        </div>
        <div class="nav-links">
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
          <a href="#faq">FAQ</a>
        </div>
        <router-link to="/login" class="nav-cta">Sign In</router-link>
      </div>
    </nav>

    <!-- ── Hero ── -->
    <section class="hero">
      <div class="hero-badge"><i class="bi bi-stars me-2"></i>Ghana's #1 PWD Management Platform</div>
      <h1 class="hero-title">
        Manage Every Person<br>
        <span class="hero-accent">With Disability</span><br>
        Across Your District
      </h1>
      <p class="hero-subtitle">
        From registration to benefits tracking, complaints management and AI-powered risk analysis —
        all in one secure, offline-capable platform built for District Assemblies.
      </p>
      <div class="hero-actions">
        <button class="btn-hero-primary" @click="scrollTo('pricing')">
          <i class="bi bi-rocket-takeoff-fill me-2"></i>Start Free Trial
        </button>
        <router-link to="/login" class="btn-hero-secondary">
          <i class="bi bi-play-circle me-2"></i>View Demo
        </router-link>
      </div>
      <div class="hero-stats">
        <div class="hero-stat"><span>500+</span><small>Districts Served</small></div>
        <div class="hero-stat-divider"></div>
        <div class="hero-stat"><span>50K+</span><small>PWDs Registered</small></div>
        <div class="hero-stat-divider"></div>
        <div class="hero-stat"><span>99.9%</span><small>Uptime SLA</small></div>
        <div class="hero-stat-divider"></div>
        <div class="hero-stat"><span>GHS</span><small>Local Currency</small></div>
      </div>
    </section>

    <!-- ── Features grid ── -->
    <section class="features-section" id="features">
      <div class="section-label">Everything you need</div>
      <h2 class="section-title">Purpose-built for Ghana's <br>Social Protection System</h2>
      <div class="features-grid">
        <div class="feature-card" v-for="f in features" :key="f.title">
          <div class="feature-icon" :style="{ background: f.bg, color: f.color }">
            <i :class="['bi', f.icon]"></i>
          </div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ── Pricing ── -->
    <section class="pricing-section" id="pricing">
      <div class="section-label">Simple, transparent pricing</div>
      <h2 class="section-title">Choose the right plan<br>for your Assembly</h2>
      <p class="section-subtitle">All plans include a 14-day free trial. No credit card required.</p>

      <!-- Billing toggle -->
      <div class="billing-toggle">
        <span :class="{ active: billingCycle === 'monthly' }" @click="billingCycle = 'monthly'">Monthly</span>
        <div class="toggle-switch" @click="billingCycle = billingCycle === 'monthly' ? 'yearly' : 'monthly'">
          <div class="toggle-knob" :class="{ right: billingCycle === 'yearly' }"></div>
        </div>
        <span :class="{ active: billingCycle === 'yearly' }" @click="billingCycle = 'yearly'">
          Yearly <span class="save-badge">Save 17%</span>
        </span>
      </div>

      <!-- Plan cards -->
      <div v-if="plansLoading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>
      <div class="plans-grid" v-else>
        <div
          v-for="plan in plans"
          :key="plan.id"
          class="plan-card"
          :class="{ popular: plan.is_popular, enterprise: plan.tier === 'enterprise' }"
        >
          <div class="popular-badge" v-if="plan.is_popular">Most Popular</div>

          <div class="plan-header">
            <div class="plan-icon"><i :class="['bi', planIcon(plan.tier)]"></i></div>
            <h3 class="plan-name">{{ plan.name }}</h3>
            <p class="plan-desc">{{ plan.description }}</p>
          </div>

          <div class="plan-price" v-if="plan.tier !== 'enterprise'">
            <span class="currency">GHS</span>
            <span class="amount">{{ displayPrice(plan) }}</span>
            <span class="period">/ {{ billingCycle === 'monthly' ? 'month' : 'year' }}</span>
          </div>
          <div class="plan-price enterprise-price" v-else>
            <span class="custom-price">Custom Pricing</span>
          </div>

          <div class="plan-limits">
            <div class="limit-item"><i class="bi bi-people-fill"></i>
              {{ plan.max_users === 0 ? 'Unlimited' : (plan.max_users || 0) }} Users
            </div>
            <div class="limit-item"><i class="bi bi-person-wheelchair"></i>
              {{ plan.max_pwds === 0 ? 'Unlimited' : Number(plan.max_pwds || 0).toLocaleString() }} PWDs
            </div>
            <div class="limit-item"><i class="bi bi-building"></i>
              {{ plan.max_partners === 0 ? 'Unlimited' : (plan.max_partners || 0) }} Partners
            </div>
            <div class="limit-item"><i class="bi bi-hdd-fill"></i>
              {{ plan.storage_gb }} GB Storage
            </div>
          </div>

          <ul class="plan-features">
            <li
                v-for="(feat, index) in planFeatures(plan)"
                :key="`${feat.label}-${index}`" :class="{ disabled: !feat.enabled }"
              >
              <i :class="['bi', feat.enabled ? 'bi-check-circle-fill' : 'bi-x-circle']"></i>
              {{ feat.label }}
            </li>
          </ul>

          <button
            class="plan-cta"
            :class="{ 'plan-cta-primary': plan.is_popular }"
            @click="selectPlan(plan)"
          >
            {{ plan.tier === 'enterprise' ? 'Contact Sales' : plan.tier === 'free' ? 'Start Free Trial' : 'Get Started' }}
            <i class="bi bi-arrow-right ms-2"></i>
          </button>
        </div>
      </div>
    </section>

    <!-- ── Comparison table ── -->
    <section class="compare-section">
      <h2 class="section-title">Full Feature Comparison</h2>
      <div class="compare-wrap">
        <table class="compare-table">
          <thead>
            <tr>
              <th>Feature</th>
              <th v-for="plan in plans" :key="plan.id" :class="{ highlight: plan.is_popular }">
                {{ plan.name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in compareRows" :key="row.label">
              <td class="feature-name">{{ row.label }}</td>
              <td v-for="plan in plans" :key="plan.id" :class="{ highlight: plan.is_popular }">
                <template v-if="typeof row.getValue(plan) === 'boolean'">
                  <i :class="row.getValue(plan) ? 'bi bi-check-lg text-success' : 'bi bi-dash text-muted'"></i>
                </template>
                <template v-else>
                  <span class="compare-val">{{ row.getValue(plan) }}</span>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- ── FAQ ── -->
    <section class="faq-section" id="faq">
      <h2 class="section-title">Frequently Asked Questions</h2>
      <div class="faq-grid">
        <div class="faq-item" v-for="(item, i) in faqs" :key="i">
          <button class="faq-q" @click="openFaq = openFaq === i ? null : i">
            <span>{{ item.q }}</span>
            <i class="bi" :class="openFaq === i ? 'bi-dash' : 'bi-plus'"></i>
          </button>
          <div class="faq-a" :class="{ open: openFaq === i }">
            <p>{{ item.a }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── CTA Banner ── -->
    <section class="cta-banner">
      <div class="cta-inner">
        <h2>Ready to modernise your district's PWD management?</h2>
        <p>Join District Assemblies across Ghana using PWDMS to serve persons with disability better.</p>
        <button class="btn-hero-primary" @click="scrollTo('pricing')">
          <i class="bi bi-rocket-takeoff-fill me-2"></i>Get Started Free
        </button>
      </div>
    </section>

    <!-- ── Footer ── -->
    <footer class="pricing-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <div class="nav-logo"><i class="bi bi-heart-pulse-fill"></i></div>
          <span>PWDMS — Persons With Disability Management System</span>
        </div>
        <div class="footer-links">
          <router-link to="/login">Sign In</router-link>
          <a href="mailto:info@pwdms.gh">Contact</a>
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
        </div>
        <p class="footer-copy">© {{ new Date().getFullYear() }} Sikaba Systems. Built for Ghana.</p>
      </div>
    </footer>

    <!-- ── Trial Modal ── -->
    <Transition name="modal">
      <div class="modal-overlay" v-if="showTrialModal" @click.self="showTrialModal = false">
        <div class="modal-box">
          <button class="modal-close" @click="showTrialModal = false"><i class="bi bi-x-lg"></i></button>
          <div class="modal-header-icon"><i class="bi bi-rocket-takeoff-fill"></i></div>
          <h3>Start Your Free Trial</h3>
          <p class="text-muted mb-4">
            {{ selectedPlan?.trial_days }}-day free trial on the
            <strong>{{ selectedPlan?.name }}</strong> plan. No credit card required.
          </p>
          <div class="mb-3">
            <label class="form-label fw-semibold">District Assembly Name *</label>
            <input v-model="trialForm.tenant_name" type="text" class="form-control" placeholder="e.g. Accra Metropolitan Assembly">
          </div>
          <div class="mb-3">
            <label class="form-label fw-semibold">Contact Email *</label>
            <input v-model="trialForm.tenant_email" type="email" class="form-control" placeholder="admin@yourda.gov.gh">
          </div>
          <div class="mb-4">
            <label class="form-label fw-semibold">Contact Phone</label>
            <input v-model="trialForm.tenant_phone" type="tel" class="form-control" placeholder="0XX XXX XXXX">
          </div>
          <div class="alert alert-info py-2 mb-4 small">
            <i class="bi bi-info-circle me-2"></i>
            After starting your trial, you'll be redirected to set up your admin account.
          </div>
          <button class="btn btn-primary w-100 py-2" @click="submitTrial" :disabled="trialLoading">
            <span v-if="trialLoading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-rocket-takeoff me-2"></i>
            Start {{ selectedPlan?.trial_days }}-Day Free Trial
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router       = useRouter()
const plans        = ref([])
const plansLoading = ref(true)
const billingCycle = ref('monthly')
const openFaq      = ref(null)
const showTrialModal = ref(false)
const selectedPlan   = ref(null)
const trialLoading   = ref(false)
const trialForm = ref({ tenant_name: '', tenant_email: '', tenant_phone: '' })

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

function displayPrice(plan) {
  const price = billingCycle.value === 'yearly'
    ? plan?.price_yearly
    : plan?.price_monthly

  return Number(price || 0).toLocaleString()
}

function planIcon(tier) {
  return { free:'bi-gift', starter:'bi-lightning', standard:'bi-star-fill',
           professional:'bi-gem', enterprise:'bi-building-fill' }[tier] || 'bi-circle'
}

function planFeatures(plan) {
  const supportLevel = plan?.feature_support
    ? plan.feature_support.charAt(0).toUpperCase() +
      plan.feature_support.slice(1)
    : 'Standard'

  return [
    { label: 'PWD Registration & Medical Records', enabled: true },
    { label: 'Benefits & Allocations Tracking', enabled: true },
    { label: 'Complaints Management', enabled: true },
    { label: 'Offline / PWA Support', enabled: !!plan?.feature_offline },
    { label: 'PDF Album Export', enabled: !!plan?.feature_album_pdf },
    { label: 'PowerPoint Album Export', enabled: !!plan?.feature_album_pptx },
    { label: 'Advanced Reports & Analytics', enabled: !!plan?.feature_reports },
    { label: 'AI Risk Scoring & Summaries', enabled: !!plan?.feature_ai },
    { label: 'Full Audit Trail', enabled: !!plan?.feature_audit },
    { label: 'Custom Branding / White-label', enabled: !!plan?.feature_white_label },
    { label: 'CSV Bulk Import', enabled: !!plan?.feature_bulk_import },
    { label: 'REST API Access', enabled: !!plan?.feature_api_access },
    { label: `${supportLevel} Support`, enabled: true },
  ]
}

const compareRows = computed(() => [
  {
    label: 'Users',
    getValue: p => p?.max_users === 0 ? 'Unlimited' : (p?.max_users ?? 0)
  },
  {
    label: 'PWDs',
    getValue: p =>
      p?.max_pwds === 0
        ? 'Unlimited'
        : Number(p?.max_pwds || 0).toLocaleString()
  },
  {
    label: 'Partners',
    getValue: p =>
      p?.max_partners === 0
        ? 'Unlimited'
        : (p?.max_partners ?? 0)
  },
  {
    label: 'Storage',
    getValue: p => `${p?.storage_gb || 0} GB`
  },
  {
    label: 'Offline / PWA',
    getValue: p => !!p?.feature_offline
  },
  {
    label: 'PDF Export',
    getValue: p => !!p?.feature_album_pdf
  },
  {
    label: 'PPTX Export',
    getValue: p => !!p?.feature_album_pptx
  },
  {
    label: 'Reports',
    getValue: p => !!p?.feature_reports
  },
  {
    label: 'AI Analysis',
    getValue: p => !!p?.feature_ai
  },
  {
    label: 'Audit Log',
    getValue: p => !!p?.feature_audit
  },
  {
    label: 'White-label',
    getValue: p => !!p?.feature_white_label
  },
  {
    label: 'Bulk Import',
    getValue: p => !!p?.feature_bulk_import
  },
  {
    label: 'API Access',
    getValue: p => !!p?.feature_api_access
  },
  {
    label: 'Support',
    getValue: p =>
      p?.feature_support
        ? p.feature_support.charAt(0).toUpperCase() +
          p.feature_support.slice(1)
        : 'Standard'
  }
])

const features = [
  { icon:'bi-person-vcard-fill',      title:'PWD Registration',      bg:'#eff6ff', color:'#1d4ed8', desc:'Full personal, medical and disability records with photo upload and unique ID generation.' },
  { icon:'bi-gift-fill',              title:'Benefits Tracking',      bg:'#fdf4ff', color:'#9333ea', desc:'Track benefits from NGOs, government and development partners with approval workflows.' },
  { icon:'bi-chat-left-text-fill',    title:'Complaints Management',  bg:'#fff7ed', color:'#ea580c', desc:'Lodge, assign and resolve complaints with priority levels and resolution notes.' },
  { icon:'bi-robot',                  title:'AI Risk Analysis',       bg:'#f0fdf4', color:'#15803d', desc:'GPT-powered vulnerability scoring and intervention recommendations per PWD.' },
  { icon:'bi-journal-richtext',       title:'PWD Album & Export',     bg:'#fefce8', color:'#ca8a04', desc:'Visual PWD directory exportable as branded PDF or PowerPoint for presentations.' },
  { icon:'bi-wifi-off',               title:'Works Offline',          bg:'#f8fafc', color:'#475569', desc:'Progressive Web App with offline support — critical for areas with poor connectivity.' },
  { icon:'bi-bar-chart-fill',         title:'Analytics Dashboard',    bg:'#fff1f2', color:'#e11d48', desc:'Charts and KPIs for gender, disability type, district distribution and risk levels.' },
  { icon:'bi-shield-check',           title:'Full Audit Trail',       bg:'#ecfdf5', color:'#047857', desc:'Every action logged with timestamp, user and before/after values for compliance.' },
  { icon:'bi-palette-fill',           title:'Custom Branding',        bg:'#fdf2f8', color:'#db2777', desc:'Upload your DA logo, set brand colours — the system reflects your Assembly identity.' },
  { icon:'bi-geo-alt-fill',           title:'Ghana-specific',         bg:'#eff6ff', color:'#2563eb', desc:'Ghana Post GPS, GRA compliance, NHIS integration and Africa/Accra timezone built in.' },
]

const faqs = [
  { q:'Is there a free trial?', a:'Yes — all paid plans include a 14-day free trial with no credit card required. Enterprise plans get 30 days.' },
  { q:'Can I change my plan later?', a:'Absolutely. You can upgrade or downgrade at any time from the subscription settings in your account. Changes take effect immediately.' },
  { q:'What payment methods are accepted?', a:'We accept mobile money (MTN, Vodafone, AirtelTigo), bank transfer, and Paystack card payments in GHS.' },
  { q:'Does it work without internet?', a:'Yes. The system is a Progressive Web App (PWA) that caches data locally. Data entry works offline and syncs when connectivity is restored.' },
  { q:'Is data secure and private?', a:'Yes. Data is encrypted at rest and in transit. Each District Assembly\'s data is isolated. We comply with Ghana\'s Data Protection Act.' },
  { q:'Can we self-host the system?', a:'Enterprise plans include source code access and on-premise deployment support for assemblies that require it.' },
  { q:'What happens when my trial ends?', a:'You\'ll be prompted to choose a paid plan. Your data is preserved for 30 days after trial expiry so you can upgrade without losing anything.' },
  { q:'Do you offer discounts for government?', a:'Yes — we offer special pricing for District Assemblies and Regional Coordinating Councils. Contact our sales team for details.' },
]

function selectPlan(plan) {
  if (plan.tier === 'enterprise') {
    window.location.href = 'mailto:sales@pwdms.gh?subject=Enterprise Enquiry'
    return
  }
  selectedPlan.value = plan
  showTrialModal.value = true
}

async function submitTrial() {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  if (!trialForm.value.tenant_name?.trim()) {
    alert('Assembly name is required')
    return
  }

  if (!emailRegex.test(trialForm.value.tenant_email)) {
    alert('Please enter a valid email address')
    return
  }

  trialLoading.value = true

  try {
    await api.post('/subscriptions/start-trial/', {
      ...trialForm.value,
      plan_id: selectedPlan.value?.id,
    })

    showTrialModal.value = false

    router.push({
      path: '/login',
      query: { trial: 'started' }
    })

  } catch (error) {
    console.error(error)

    const message =
      error?.response?.data?.message ||
      error?.response?.data?.detail ||
      'Unable to start trial.'

    alert(message)

  } finally {
    trialLoading.value = false
  }
}

onMounted(async () => {
  plansLoading.value = true

  try {
    const { data } = await api.get('/plans/')

    const planData = Array.isArray(data)
      ? data
      : Array.isArray(data?.results)
        ? data.results
        : []

    plans.value = planData.filter(
      p => p?.tier && p.tier !== 'free'
    )

  } catch (error) {
    console.error('Failed to load plans:', error)
    plans.value = []
  } finally {
    plansLoading.value = false
  }
})
</script>

<style scoped>
/* ── Base ── */
.pricing-page { font-family: 'Segoe UI', system-ui, sans-serif; color: #0f172a; overflow-x: hidden; }

/* ── Nav ── */
.pricing-nav {
  position: sticky; top: 0; z-index: 100;
  background: rgba(255,255,255,.92); backdrop-filter: blur(12px);
  border-bottom: 1px solid #e2e8f0;
}
.nav-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; height: 64px; display: flex; align-items: center; gap: 32px; }
.nav-brand { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.1rem; text-decoration: none; color: #0f172a; }
.nav-logo { width: 36px; height: 36px; border-radius: 10px; background: #1a56db; display: flex; align-items: center; justify-content: center; color: white; font-size: 1rem; }
.nav-links { display: flex; gap: 24px; margin-left: auto; }
.nav-links a { text-decoration: none; color: #64748b; font-size: .9rem; font-weight: 500; transition: color .15s; }
.nav-links a:hover { color: #1a56db; }
.nav-cta { background: #1a56db; color: white; padding: 8px 20px; border-radius: 8px; text-decoration: none; font-size: .9rem; font-weight: 600; transition: opacity .15s; white-space: nowrap; }
.nav-cta:hover { opacity: .88; }

/* ── Hero ── */
.hero {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #1a56db 100%);
  color: white; text-align: center;
  padding: clamp(80px, 10vw, 140px) 24px 80px;
  position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(96,165,250,.2) 0%, transparent 70%);
}
.hero-badge {
  display: inline-flex; align-items: center;
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.2);
  backdrop-filter: blur(8px); border-radius: 20px; padding: 6px 16px;
  font-size: .8rem; font-weight: 600; margin-bottom: 28px;
  color: #bfdbfe;
}
.hero-title {
  font-size: clamp(2rem, 5vw, 3.8rem); font-weight: 900;
  line-height: 1.1; margin-bottom: 20px; position: relative;
}
.hero-accent { color: #60a5fa; }
.hero-subtitle { font-size: clamp(.9rem, 2vw, 1.15rem); color: #94a3b8; max-width: 600px; margin: 0 auto 36px; line-height: 1.7; }
.hero-actions { display: flex; justify-content: center; gap: 14px; flex-wrap: wrap; margin-bottom: 56px; }
.btn-hero-primary {
  background: #1a56db; color: white; border: none;
  padding: 14px 28px; border-radius: 10px; font-size: 1rem; font-weight: 700;
  cursor: pointer; display: flex; align-items: center; transition: transform .18s, box-shadow .18s;
  box-shadow: 0 4px 20px rgba(26,86,219,.4);
}
.btn-hero-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(26,86,219,.5); }
.btn-hero-secondary {
  background: rgba(255,255,255,.10); color: white;
  border: 1.5px solid rgba(255,255,255,.25);
  padding: 14px 28px; border-radius: 10px; font-size: 1rem; font-weight: 600;
  cursor: pointer; display: flex; align-items: center; text-decoration: none;
  transition: background .18s;
}
.btn-hero-secondary:hover { background: rgba(255,255,255,.18); }
.hero-stats { display: flex; justify-content: center; align-items: center; gap: 0; flex-wrap: wrap; position: relative; z-index: 1; }
.hero-stat { text-align: center; padding: 0 32px; }
.hero-stat span { display: block; font-size: 1.8rem; font-weight: 900; color: white; }
.hero-stat small { display: block; font-size: .75rem; color: #94a3b8; margin-top: 2px; }
.hero-stat-divider { width: 1px; height: 36px; background: rgba(255,255,255,.15); }

/* ── Section commons ── */
.section-label {
  text-align: center; font-size: .78rem; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; color: #1a56db; margin-bottom: 14px;
}
.section-title { text-align: center; font-size: clamp(1.6rem,3.5vw,2.4rem); font-weight: 800; margin-bottom: 16px; line-height: 1.2; }
.section-subtitle { text-align: center; color: #64748b; font-size: 1rem; margin-bottom: 48px; }

/* ── Features ── */
.features-section { padding: 100px 24px; max-width: 1200px; margin: 0 auto; }
.features-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 24px; margin-top: 56px; }
.feature-card { background: white; border-radius: 16px; padding: 28px 24px; border: 1px solid #e2e8f0; transition: transform .2s, box-shadow .2s; }
.feature-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,.08); }
.feature-icon { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.4rem; margin-bottom: 16px; }
.feature-card h3 { font-size: 1rem; font-weight: 700; margin-bottom: 8px; }
.feature-card p { font-size: .875rem; color: #64748b; line-height: 1.6; }

/* ── Pricing ── */
.pricing-section { background: #f8fafc; padding: 100px 24px; }
.billing-toggle {
  display: flex; align-items: center; justify-content: center;
  gap: 14px; margin-bottom: 56px; font-size: .9rem; font-weight: 600; color: #94a3b8;
}
.billing-toggle span { cursor: pointer; transition: color .15s; }
.billing-toggle span.active { color: #0f172a; }
.toggle-switch {
  width: 52px; height: 28px; background: #1a56db; border-radius: 14px;
  cursor: pointer; position: relative; transition: background .2s;
}
.toggle-knob {
  position: absolute; width: 22px; height: 22px; background: white; border-radius: 50%;
  top: 3px; left: 3px; transition: transform .25s cubic-bezier(.4,0,.2,1);
  box-shadow: 0 2px 6px rgba(0,0,0,.2);
}
.toggle-knob.right { transform: translateX(24px); }
.save-badge { background: #dcfce7; color: #16a34a; font-size: .7rem; padding: 2px 8px; border-radius: 10px; margin-left: 6px; }

.plans-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; align-items: start; }

.plan-card {
  background: white; border-radius: 20px; padding: 32px 24px;
  border: 2px solid #e2e8f0; position: relative;
  transition: transform .2s, box-shadow .2s, border-color .2s;
}
.plan-card:hover { transform: translateY(-4px); box-shadow: 0 16px 48px rgba(0,0,0,.10); }
.plan-card.popular {
  border-color: #1a56db;
  box-shadow: 0 8px 32px rgba(26,86,219,.15);
  transform: scale(1.02);
}
.plan-card.enterprise { border-color: #7e3af2; background: linear-gradient(135deg, #faf5ff 0%, #f0f4ff 100%); }
.popular-badge {
  position: absolute; top: -14px; left: 50%; transform: translateX(-50%);
  background: #1a56db; color: white; padding: 4px 16px; border-radius: 20px;
  font-size: .75rem; font-weight: 700; white-space: nowrap;
}

.plan-icon {
  width: 48px; height: 48px; border-radius: 12px; background: #eff6ff;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; color: #1a56db; margin-bottom: 14px;
}
.plan-card.popular .plan-icon { background: #1a56db; color: white; }
.plan-card.enterprise .plan-icon { background: #7e3af2; color: white; }
.plan-name { font-size: 1.15rem; font-weight: 800; margin-bottom: 6px; }
.plan-desc { font-size: .8rem; color: #64748b; margin-bottom: 20px; line-height: 1.5; }

.plan-price { display: flex; align-items: baseline; gap: 4px; margin-bottom: 20px; }
.currency { font-size: .95rem; font-weight: 700; color: #64748b; align-self: flex-start; margin-top: 8px; }
.amount { font-size: 2.4rem; font-weight: 900; color: #0f172a; line-height: 1; }
.period { font-size: .8rem; color: #94a3b8; }
.enterprise-price { margin-bottom: 20px; }
.custom-price { font-size: 1.4rem; font-weight: 800; color: #7e3af2; }

.plan-limits { display: flex; flex-direction: column; gap: 6px; padding: 16px; background: #f8fafc; border-radius: 10px; margin-bottom: 20px; }
.limit-item { font-size: .8rem; color: #475569; display: flex; align-items: center; gap: 8px; font-weight: 600; }
.limit-item i { color: #1a56db; width: 16px; }

.plan-features { list-style: none; padding: 0; margin: 0 0 24px; display: flex; flex-direction: column; gap: 8px; max-height: 260px; overflow: hidden; }
.plan-features li { display: flex; align-items: center; gap: 8px; font-size: .82rem; color: #374151; }
.plan-features li.disabled { color: #cbd5e1; }
.plan-features li i { font-size: .9rem; flex-shrink: 0; }
.plan-features li:not(.disabled) i { color: #16a34a; }
.plan-features li.disabled i { color: #cbd5e1; }

.plan-cta {
  width: 100%; padding: 12px; border-radius: 10px; font-size: .9rem; font-weight: 700;
  cursor: pointer; border: 2px solid #e2e8f0; background: white; color: #0f172a;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s, border-color .15s, color .15s;
}
.plan-cta:hover { border-color: #1a56db; color: #1a56db; }
.plan-cta-primary { background: #1a56db; color: white; border-color: #1a56db; }
.plan-cta-primary:hover { background: #1d4ed8; border-color: #1d4ed8; color: white; }

/* ── Compare table ── */
.compare-section { padding: 80px 24px; max-width: 1200px; margin: 0 auto; }
.compare-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 16px; border: 1px solid #e2e8f0; }
.compare-table { width: 100%; border-collapse: collapse; font-size: .875rem; }
.compare-table thead { background: #f8fafc; }
.compare-table th { padding: 14px 20px; text-align: center; font-weight: 700; border-bottom: 1px solid #e2e8f0; white-space: nowrap; }
.compare-table th:first-child { text-align: left; }
.compare-table th.highlight { background: #eff6ff; color: #1a56db; }
.compare-table td { padding: 12px 20px; text-align: center; border-bottom: 1px solid #f1f5f9; }
.compare-table td:first-child { text-align: left; }
.compare-table td.highlight { background: #f8fbff; }
.compare-table tr:last-child td { border-bottom: none; }
.feature-name { font-weight: 600; color: #374151; }
.compare-val { font-size: .82rem; color: #64748b; }
.bi-check-lg { font-size: 1.1rem; }

/* ── FAQ ── */
.faq-section { background: #f8fafc; padding: 80px 24px; }
.faq-grid { max-width: 800px; margin: 48px auto 0; display: flex; flex-direction: column; gap: 12px; }
.faq-item { background: white; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }
.faq-q {
  width: 100%; display: flex; justify-content: space-between; align-items: center;
  padding: 18px 20px; background: none; border: none; cursor: pointer;
  font-size: .95rem; font-weight: 600; color: #0f172a; text-align: left; gap: 12px;
}
.faq-q:hover { background: #f8fafc; }
.faq-q i { font-size: 1.1rem; color: #1a56db; flex-shrink: 0; }
.faq-a { max-height: 0; overflow: hidden; transition: max-height .3s ease, padding .3s ease; }
.faq-a.open { max-height: 200px; padding-bottom: 18px; }
.faq-a p { padding: 0 20px; color: #64748b; font-size: .9rem; line-height: 1.7; }

/* ── CTA Banner ── */
.cta-banner { background: linear-gradient(135deg, #1e3a8a, #1a56db); color: white; padding: 80px 24px; text-align: center; }
.cta-inner { max-width: 640px; margin: 0 auto; }
.cta-inner h2 { font-size: clamp(1.5rem, 3vw, 2.2rem); font-weight: 900; margin-bottom: 16px; }
.cta-inner p { color: #bfdbfe; margin-bottom: 32px; font-size: 1rem; }

/* ── Footer ── */
.pricing-footer { background: #0f172a; color: #94a3b8; padding: 48px 24px; }
.footer-inner { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 20px; }
.footer-brand { display: flex; align-items: center; gap: 10px; font-size: .9rem; font-weight: 600; color: #e2e8f0; }
.footer-links { display: flex; gap: 24px; flex-wrap: wrap; justify-content: center; }
.footer-links a { color: #64748b; text-decoration: none; font-size: .85rem; transition: color .15s; }
.footer-links a:hover { color: #e2e8f0; }
.footer-copy { font-size: .8rem; color: #475569; }

/* ── Modal ── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.6); backdrop-filter: blur(4px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-box { background: white; border-radius: 20px; padding: 36px 32px; width: 100%; max-width: 460px; position: relative; box-shadow: 0 24px 60px rgba(0,0,0,.2); }
.modal-close { position: absolute; top: 16px; right: 16px; background: #f1f5f9; border: none; width: 32px; height: 32px; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: .9rem; }
.modal-header-icon { width: 56px; height: 56px; border-radius: 16px; background: #eff6ff; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; color: #1a56db; margin-bottom: 16px; }
.modal-box h3 { font-size: 1.3rem; font-weight: 800; margin-bottom: 8px; }
.modal-enter-active, .modal-leave-active { transition: opacity .2s; }
.modal-enter-active .modal-box, .modal-leave-active .modal-box { transition: transform .2s; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-box { transform: scale(.95) translateY(10px); }

/* ── Responsive ── */
@media (max-width: 768px) {
  .nav-links { display: none; }
  .hero-stat-divider { display: none; }
  .hero-stat { padding: 12px 16px; }
  .plans-grid { grid-template-columns: 1fr; }
  .plan-card.popular { transform: none; }
  .features-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
  .features-grid { grid-template-columns: 1fr; }
  .hero-actions { flex-direction: column; align-items: center; }
  .btn-hero-primary, .btn-hero-secondary { width: 100%; justify-content: center; }
}
</style>
