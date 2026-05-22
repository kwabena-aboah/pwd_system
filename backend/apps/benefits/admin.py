"""
benefits/admin.py
"""
from django.contrib import admin
from .models import DevelopmentPartner, BenefitCategory, Benefit, BenefitAllocation


@admin.register(DevelopmentPartner)
class DevelopmentPartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner_type', 'district', 'is_active']
    list_filter = ['partner_type', 'is_active', 'region']
    search_fields = ['name', 'acronym', 'contact_person']


@admin.register(BenefitCategory)
class BenefitCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner', 'category', 'status', 'frequency', 'value']
    list_filter = ['status', 'frequency', 'partner']
    search_fields = ['name', 'description']


@admin.register(BenefitAllocation)
class BenefitAllocationAdmin(admin.ModelAdmin):
    list_display = ['pwd', 'benefit', 'status', 'allocation_date', 'amount_disbursed']
    list_filter = ['status', 'benefit__partner']
    search_fields = ['pwd__first_name', 'pwd__last_name', 'pwd__registration_number']
    date_hierarchy = 'allocation_date'
