"""apps/subscriptions/views.py"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import hashlib, hmac, json
from datetime import date
from dateutil.relativedelta import relativedelta

from .models import Plan, Subscription, Invoice
from .serializers import (
    PlanSerializer, SubscriptionSerializer,
    InvoiceSerializer, SubscriptionStatusSerializer
)


# ─── helpers ──────────────────────────────────────────────────────────────────
def _get_active_subscription():
    """Return the single active subscription, or None."""
    return (
        Subscription.objects
        .filter(status__in=['active', 'trialing', 'past_due'])
        .select_related('plan')
        .first()
    )


def _build_status_payload(sub):
    """Build the SubscriptionStatusSerializer payload dict."""
    from apps.pwds.models import PWD
    from apps.benefits.models import DevelopmentPartner
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if not sub:
        return {
            'has_subscription': False,
            'status': 'none', 'plan_tier': 'free', 'plan_name': 'No Plan',
            'days_remaining': 0, 'is_trial': False,
            'billing_cycle': 'monthly', 'current_price': 0, 'currency': 'GHS',
            'max_users': 3, 'max_pwds': 50, 'max_partners': 2, 'storage_gb': 1,
            'feature_ai': False, 'feature_album_pdf': True, 'feature_album_pptx': False,
            'feature_audit': False, 'feature_reports': False, 'feature_api_access': False,
            'feature_white_label': False, 'feature_bulk_import': False,
            'feature_offline': True, 'feature_support': 'community',
            'current_pwds': 0, 'current_users': 0, 'current_partners': 0,
        }

    plan = sub.plan
    return {
        'has_subscription': True,
        'status':        sub.status,
        'plan_tier':     plan.tier,
        'plan_name':     plan.name,
        'days_remaining': sub.days_remaining,
        'is_trial':      sub.is_trial,
        'billing_cycle': sub.billing_cycle,
        'current_price': sub.current_price,
        'currency':      plan.currency,
        # limits
        'max_users':    plan.max_users,
        'max_pwds':     plan.max_pwds,
        'max_partners': plan.max_partners,
        'storage_gb':   plan.storage_gb,
        # features
        'feature_ai':           plan.feature_ai,
        'feature_album_pdf':    plan.feature_album_pdf,
        'feature_album_pptx':   plan.feature_album_pptx,
        'feature_audit':        plan.feature_audit,
        'feature_reports':      plan.feature_reports,
        'feature_api_access':   plan.feature_api_access,
        'feature_white_label':  plan.feature_white_label,
        'feature_bulk_import':  plan.feature_bulk_import,
        'feature_offline':      plan.feature_offline,
        'feature_support':      plan.feature_support,
        # current usage
        'current_pwds':     PWD.objects.count(),
        'current_users':    User.objects.filter(is_active=True).count(),
        'current_partners': DevelopmentPartner.objects.count(),
    }


# ─── Plans (public) ───────────────────────────────────────────────────────────
class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset          = Plan.objects.filter(is_active=True).order_by('sort_order')
    serializer_class  = PlanSerializer
    permission_classes = [permissions.AllowAny]


# ─── Subscription ─────────────────────────────────────────────────────────────
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset          = Subscription.objects.select_related('plan', 'managed_by').all()
    serializer_class  = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ['super_admin']:
            return super().get_queryset()
        return super().get_queryset().filter(status__in=['active', 'trialing'])

    def perform_create(self, serializer):
        serializer.save(managed_by=self.request.user)

    # GET /api/subscriptions/current/
    @action(detail=False, methods=['get'], url_path='current',
            permission_classes=[permissions.AllowAny])
    def current(self, request):
        sub     = _get_active_subscription()
        payload = _build_status_payload(sub)
        return Response(SubscriptionStatusSerializer(payload).data)

    # POST /api/subscriptions/{id}/activate/
    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        sub   = self.get_object()
        cycle = request.data.get('billing_cycle', 'monthly')
        sub.activate(cycle)
        # Create invoice
        Invoice.objects.create(
            subscription=sub,
            amount=sub.current_price,
            currency=sub.plan.currency,
            status='paid',
            period_start=sub.current_period_start,
            period_end=sub.current_period_end,
            due_date=sub.current_period_start,
            paid_at=timezone.now(),
            payment_method=request.data.get('payment_method', 'manual'),
            payment_ref=request.data.get('payment_ref', ''),
            notes='Manual activation',
        )
        return Response(SubscriptionSerializer(sub).data)

    # POST /api/subscriptions/{id}/cancel/
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_sub(self, request, pk=None):
        sub            = self.get_object()
        at_period_end  = request.data.get('at_period_end', True)
        sub.cancel(at_period_end=at_period_end)
        return Response(SubscriptionSerializer(sub).data)

    # POST /api/subscriptions/{id}/change-plan/
    @action(detail=True, methods=['post'], url_path='change-plan')
    def change_plan(self, request, pk=None):
        sub     = self.get_object()
        plan_id = request.data.get('plan_id')
        try:
            new_plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response({'error': 'Plan not found'}, status=400)
        sub.plan = new_plan
        sub.save()
        return Response(SubscriptionSerializer(sub).data)

    # POST /api/subscriptions/start-trial/
    @action(detail=False, methods=['post'], url_path='start-trial',
            permission_classes=[permissions.IsAuthenticated])
    def start_trial(self, request):
        if _get_active_subscription():
            return Response({'error': 'A subscription already exists.'}, status=400)
        try:
            plan = Plan.objects.get(tier='free')
        except Plan.DoesNotExist:
            plan = Plan.objects.order_by('sort_order').first()

        today = date.today()
        sub = Subscription.objects.create(
            tenant_name   = request.data.get('tenant_name', 'My District Assembly'),
            tenant_email  = request.data.get('tenant_email', request.user.email),
            tenant_phone  = request.data.get('tenant_phone', ''),
            plan          = plan,
            billing_cycle = 'monthly',
            status        = 'trialing',
            trial_start   = today,
            trial_end     = today + relativedelta(days=plan.trial_days),
            managed_by    = request.user,
        )
        return Response(SubscriptionSerializer(sub).data, status=201)


# ─── Invoices ─────────────────────────────────────────────────────────────────
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset          = Invoice.objects.select_related('subscription', 'subscription__plan').all()
    serializer_class  = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields  = ['status', 'subscription']

    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.mark_paid(
            payment_ref=request.data.get('payment_ref', ''),
            method=request.data.get('payment_method', 'manual'),
        )
        return Response(InvoiceSerializer(invoice).data)


# ─── Paystack Webhook ─────────────────────────────────────────────────────────
@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        secret    = getattr(settings, 'PAYSTACK_SECRET_KEY', '')
        signature = request.headers.get('x-paystack-signature', '')
        payload   = request.body

        # Verify HMAC
        computed = hmac.new(secret.encode(), payload, hashlib.sha512).hexdigest()
        if not hmac.compare_digest(computed, signature):
            return Response({'error': 'Invalid signature'}, status=400)

        event = json.loads(payload)
        etype = event.get('event')
        data  = event.get('data', {})

        if etype == 'charge.success':
            ref = data.get('reference', '')
            try:
                inv = Invoice.objects.get(paystack_ref=ref)
                inv.mark_paid(payment_ref=ref, method='paystack')
            except Invoice.DoesNotExist:
                pass

        elif etype == 'subscription.disable':
            sub_code = data.get('subscription_code', '')
            Subscription.objects.filter(
                paystack_subscription_id=sub_code
            ).update(status='cancelled', cancelled_at=timezone.now())

        return Response({'status': 'ok'})
