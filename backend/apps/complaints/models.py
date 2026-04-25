"""
complaints/models.py
"""
from django.db import models
from django.conf import settings


class ComplaintCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Complaint Categories'


class Complaint(models.Model):
    PRIORITY = [
        ('low', 'Low'), ('medium', 'Medium'),
        ('high', 'High'), ('urgent', 'Urgent'),
    ]
    STATUS = [
        ('open', 'Open'), ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'), ('closed', 'Closed'), ('escalated', 'Escalated'),
    ]
    SOURCE = [
        ('pwd', 'PWD Self'), ('caregiver', 'Caregiver'),
        ('community', 'Community'), ('partner', 'Partner'),
        ('anonymous', 'Anonymous'),
    ]

    pwd = models.ForeignKey(
        'pwds.PWD', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='complaints'
    )
    complaint_number = models.CharField(max_length=30, unique=True, editable=False)
    category = models.ForeignKey(ComplaintCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    source = models.CharField(max_length=20, choices=SOURCE)
    complainant_name = models.CharField(max_length=200, blank=True)
    complainant_phone = models.CharField(max_length=20, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY, default='medium')
    status = models.CharField(max_length=20, choices=STATUS, default='open')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_complaints'
    )
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='resolved_complaints'
    )
    date_lodged = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='logged_complaints'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.complaint_number} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.complaint_number:
            from datetime import date
            year = date.today().year
            count = Complaint.objects.filter(date_lodged__year=year).count() + 1
            self.complaint_number = f"CMP-{year}-{count:04d}"
        super().save(*args, **kwargs)


class ComplaintNote(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
