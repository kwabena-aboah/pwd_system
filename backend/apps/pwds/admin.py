"""
pwds/admin.py
"""
from django.contrib import admin
from .models import PWD, MedicalRecord, DisabilityType, PWDDocument


@admin.register(DisabilityType)
class DisabilityTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category']
    search_fields = ['name', 'code']


@admin.register(PWD)
class PWDAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'full_name', 'age', 'gender', 'district', 'status', 'ai_risk_label']
    list_filter = ['status', 'gender', 'district', 'region', 'ai_risk_label']
    search_fields = ['first_name', 'last_name', 'registration_number', 'national_id']
    readonly_fields = ['pwd_id', 'registration_number', 'registered_by', 'created_at', 'updated_at']
    date_hierarchy = 'registration_date'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['pwd', 'disability_severity', 'disability_onset', 'has_assistive_device']
    list_filter = ['disability_severity', 'disability_onset', 'has_assistive_device']


@admin.register(PWDDocument)
class PWDDocumentAdmin(admin.ModelAdmin):
    list_display = ['pwd', 'doc_type', 'title', 'uploaded_at']
