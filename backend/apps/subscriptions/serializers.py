"""apps/subscriptions/serializers.py"""
from rest_framework import serializers
from .models import Plan, Subscription, Invoice


class PlanSerializer(serializers.ModelSerializer):
    yearly_savings_pct = serializers.ReadOnlyField()

    class Meta:
        model  = Plan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_detail    = PlanSerializer(source='plan', read_only=True)
    is_active      = serializers.ReadOnlyField()
    is_trial       = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    current_price  = serializers.ReadOnlyField()

    class Meta:
        model  = Subscription
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at',
                            'paystack_customer_id', 'paystack_subscription_id']


class InvoiceSerializer(serializers.ModelSerializer):
    tenant_name   = serializers.CharField(source='subscription.tenant_name', read_only=True)
    plan_name     = serializers.CharField(source='subscription.plan.name',   read_only=True)

    class Meta:
        model  = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'invoice_number', 'created_at', 'updated_at']


class SubscriptionStatusSerializer(serializers.Serializer):
    """Lightweight payload consumed by the frontend on every app load."""
    has_subscription  = serializers.BooleanField()
    status            = serializers.CharField()
    plan_tier         = serializers.CharField()
    plan_name         = serializers.CharField()
    days_remaining    = serializers.IntegerField()
    is_trial          = serializers.BooleanField()
    billing_cycle     = serializers.CharField()
    current_price     = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency          = serializers.CharField()
    # Limits
    max_users         = serializers.IntegerField()
    max_pwds          = serializers.IntegerField()
    max_partners      = serializers.IntegerField()
    storage_gb        = serializers.IntegerField()
    # Features
    feature_ai          = serializers.BooleanField()
    feature_album_pdf   = serializers.BooleanField()
    feature_album_pptx  = serializers.BooleanField()
    feature_audit       = serializers.BooleanField()
    feature_reports     = serializers.BooleanField()
    feature_api_access  = serializers.BooleanField()
    feature_white_label = serializers.BooleanField()
    feature_bulk_import = serializers.BooleanField()
    feature_offline     = serializers.BooleanField()
    feature_support     = serializers.CharField()
    # Current usage
    current_pwds        = serializers.IntegerField()
    current_users       = serializers.IntegerField()
    current_partners    = serializers.IntegerField()
