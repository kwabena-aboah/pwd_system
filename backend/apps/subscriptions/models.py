"""
apps/subscriptions/models.py
Subscription system for the PWD Management System.
Each District Assembly (tenant) has a subscription that gates feature access.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid


class Plan(models.Model):
    """Subscription plan definition."""

    BILLING_CYCLE = [
        ('monthly', 'Monthly'),
        ('yearly',  'Yearly'),
    ]

    TIER = [
        ('free',       'Free Trial'),
        ('starter',    'Starter'),
        ('standard',   'Standard'),
        ('professional','Professional'),
        ('enterprise', 'Enterprise'),
    ]

    # Identity
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name          = models.CharField(max_length=100)
    tier          = models.CharField(max_length=20, choices=TIER, unique=True)
    description   = models.TextField(blank=True)
    is_active     = models.BooleanField(default=True)
    is_popular     = models.BooleanField(default=False, help_text="Highlighted on pricing page")

    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency      = models.CharField(max_length=3, default='GHS')

    # Hard limits (0 = unlimited)
    max_users          = models.PositiveIntegerField(default=3,    help_text="0 = unlimited")
    max_pwds           = models.PositiveIntegerField(default=50,   help_text="0 = unlimited")
    max_partners       = models.PositiveIntegerField(default=2,    help_text="0 = unlimited")
    max_districts      = models.PositiveIntegerField(default=1,    help_text="0 = unlimited")
    storage_gb         = models.PositiveIntegerField(default=1,    help_text="File/media storage in GB")

    # Feature flags
    feature_ai          = models.BooleanField(default=False, help_text="AI risk scoring & summaries")
    feature_album_pdf   = models.BooleanField(default=True,  help_text="PDF album export")
    feature_album_pptx  = models.BooleanField(default=False, help_text="PowerPoint album export")
    feature_audit       = models.BooleanField(default=False, help_text="Full audit trail")
    feature_reports     = models.BooleanField(default=False, help_text="Advanced analytics & reports")
    feature_api_access  = models.BooleanField(default=False, help_text="REST API access")
    feature_white_label = models.BooleanField(default=False, help_text="Custom branding / white-label")
    feature_bulk_import = models.BooleanField(default=False, help_text="CSV bulk import")
    feature_offline     = models.BooleanField(default=True,  help_text="Offline / PWA support")
    feature_support     = models.CharField(max_length=30, default='community',
                                            choices=[('community','Community'),('email','Email'),
                                                     ('priority','Priority'),('dedicated','Dedicated')],
                                            help_text="Support tier")

    # Trial
    trial_days = models.PositiveIntegerField(default=14)

    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'price_monthly']

    def __str__(self):
        return f"{self.name} ({self.tier})"

    def price_for_cycle(self, cycle='monthly'):
        return self.price_yearly if cycle == 'yearly' else self.price_monthly

    @property
    def yearly_savings_pct(self):
        if self.price_monthly and self.price_yearly:
            annual_monthly = self.price_monthly * 12
            if annual_monthly > 0:
                return int(((annual_monthly - self.price_yearly) / annual_monthly) * 100)
        return 0


class Subscription(models.Model):
    """A District Assembly's active subscription."""

    STATUS = [
        ('trialing',   'Free Trial'),
        ('active',     'Active'),
        ('past_due',   'Past Due'),
        ('cancelled',  'Cancelled'),
        ('suspended',  'Suspended'),
        ('expired',    'Expired'),
    ]

    BILLING_CYCLE = [
        ('monthly', 'Monthly'),
        ('yearly',  'Yearly'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The system settings record acts as the tenant identifier
    tenant_name     = models.CharField(max_length=200, help_text="District Assembly name")
    tenant_email    = models.EmailField(help_text="Billing contact email")
    tenant_phone    = models.CharField(max_length=20, blank=True)

    plan            = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    billing_cycle   = models.CharField(max_length=10, choices=BILLING_CYCLE, default='monthly')
    status          = models.CharField(max_length=20, choices=STATUS, default='trialing')

    # Dates
    trial_start     = models.DateField(null=True, blank=True)
    trial_end       = models.DateField(null=True, blank=True)
    current_period_start = models.DateField(null=True, blank=True)
    current_period_end   = models.DateField(null=True, blank=True)
    cancelled_at    = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)

    # Payment reference (Paystack / manual)
    payment_method  = models.CharField(max_length=30, blank=True,
                                        choices=[('paystack','Paystack'),('bank_transfer','Bank Transfer'),('cash','Cash'),('manual','Manual')])
    paystack_customer_id     = models.CharField(max_length=100, blank=True)
    paystack_subscription_id = models.CharField(max_length=100, blank=True)
    last_payment_ref         = models.CharField(max_length=100, blank=True)

    # Who manages this subscription
    managed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='managed_subscriptions'
    )

    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tenant_name} — {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        return self.status in ('active', 'trialing')

    @property
    def is_trial(self):
        return self.status == 'trialing'

    @property
    def days_remaining(self):
        if self.current_period_end:
            delta = self.current_period_end - timezone.now().date()
            return max(delta.days, 0)
        if self.trial_end:
            delta = self.trial_end - timezone.now().date()
            return max(delta.days, 0)
        return 0

    @property
    def current_price(self):
        return self.plan.price_for_cycle(self.billing_cycle)

    def can_use_feature(self, feature_key):
        """Check if the current plan allows a given feature flag."""
        return getattr(self.plan, f'feature_{feature_key}', False)

    def check_limit(self, resource, current_count):
        """Returns (allowed: bool, limit: int, current: int)"""
        limit_attr = f'max_{resource}'
        limit = getattr(self.plan, limit_attr, 0)
        if limit == 0:
            return True, 0, current_count
        return current_count < limit, limit, current_count

    def activate(self, billing_cycle='monthly'):
        from datetime import date
        from dateutil.relativedelta import relativedelta
        today = date.today()
        self.status = 'active'
        self.billing_cycle = billing_cycle
        self.current_period_start = today
        self.current_period_end = (
            today + relativedelta(years=1) if billing_cycle == 'yearly'
            else today + relativedelta(months=1)
        )
        self.save()

    def cancel(self, at_period_end=True):
        self.cancel_at_period_end = at_period_end
        if not at_period_end:
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
        self.save()


class Invoice(models.Model):
    """Payment record for a subscription period."""

    STATUS = [
        ('draft',    'Draft'),
        ('open',     'Open'),
        ('paid',     'Paid'),
        ('void',     'Void'),
        ('uncollectible', 'Uncollectible'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number  = models.CharField(max_length=30, unique=True, editable=False)
    subscription    = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')

    amount          = models.DecimalField(max_digits=10, decimal_places=2)
    currency        = models.CharField(max_length=3, default='GHS')
    status          = models.CharField(max_length=20, choices=STATUS, default='open')

    period_start    = models.DateField()
    period_end      = models.DateField()

    due_date        = models.DateField()
    paid_at         = models.DateTimeField(null=True, blank=True)
    payment_ref     = models.CharField(max_length=100, blank=True)
    payment_method  = models.CharField(max_length=30, blank=True)
    paystack_ref    = models.CharField(max_length=100, blank=True)

    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.invoice_number} — {self.subscription.tenant_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = timezone.now().year
            count = Invoice.objects.filter(created_at__year=year).count() + 1
            self.invoice_number = f"INV-{year}-{count:05d}"
        super().save(*args, **kwargs)

    def mark_paid(self, payment_ref='', method='manual'):
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.payment_ref = payment_ref
        self.payment_method = method
        self.save()
        # Activate the subscription on payment
        sub = self.subscription
        sub.last_payment_ref = payment_ref
        sub.activate(sub.billing_cycle)


class SubscriptionFeatureUsage(models.Model):
    """Track feature usage for metered billing or analytics."""
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='usage')
    feature      = models.CharField(max_length=50)
    count        = models.PositiveIntegerField(default=0)
    period_start = models.DateField()
    period_end   = models.DateField()
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['subscription', 'feature', 'period_start']
