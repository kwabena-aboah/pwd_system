"""
accounts/admin.py
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'role', 'district', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'district']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('PWD System', {'fields': ('role', 'phone', 'district', 'organization', 'profile_photo')}),
    )
