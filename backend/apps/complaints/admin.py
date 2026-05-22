"""
complaints/admin.py
"""
from django.contrib import admin
from .models import Complaint, ComplaintCategory, ComplaintNote


@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['complaint_number', 'title', 'priority', 'status', 'pwd', 'assigned_to', 'date_lodged']
    list_filter = ['status', 'priority', 'source', 'category']
    search_fields = ['complaint_number', 'title', 'pwd__first_name', 'pwd__last_name']
    date_hierarchy = 'date_lodged'


@admin.register(ComplaintNote)
class ComplaintNoteAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'added_by', 'created_at']
