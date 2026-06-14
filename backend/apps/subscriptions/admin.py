"""apps/subscriptions/admin.py"""
from django.contrib import admin
from .models import Plan, Subscription, Invoice


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display  = ['name', 'tier', 'price_monthly', 'price_yearly', 'max_users',
                     'max_pwds', 'is_popular', 'is_active']
    list_filter   = ['is_active', 'is_popular', 'tier']
    list_editable = ['is_active', 'is_popular']
    ordering      = ['sort_order']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display  = ['tenant_name', 'plan', 'status', 'billing_cycle',
                     'trial_end', 'current_period_end', 'days_remaining']
    list_filter   = ['status', 'billing_cycle', 'plan']
    search_fields = ['tenant_name', 'tenant_email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display  = ['invoice_number', 'subscription', 'amount', 'currency',
                     'status', 'due_date', 'paid_at']
    list_filter   = ['status', 'currency']
    search_fields = ['invoice_number', 'subscription__tenant_name']
    readonly_fields = ['id', 'invoice_number', 'created_at']
    date_hierarchy = 'created_at'
