"""
settings_app/models.py — System branding & config
"""
from django.db import models


class SystemSettings(models.Model):
    """Singleton — District Assembly branding"""
    system_name = models.CharField(max_length=200, default='PWD Management System')
    short_name = models.CharField(max_length=50, default='PWDMS')
    district_name = models.CharField(max_length=200, default='')
    region = models.CharField(max_length=100, default='')
    logo = models.ImageField(upload_to='settings/logos/', null=True, blank=True)
    logo_secondary = models.ImageField(upload_to='settings/logos/', null=True, blank=True)
    favicon = models.ImageField(upload_to='settings/icons/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#1a56db', help_text="Hex color")
    secondary_color = models.CharField(max_length=7, default='#7e3af2')
    accent_color = models.CharField(max_length=7, default='#ff5a1f')
    text_on_primary = models.CharField(max_length=7, default='#ffffff')
    footer_text = models.TextField(default='Ghana PWD Management System')
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)

    # Album settings
    album_title = models.CharField(max_length=200, default='PWD Directory')
    album_subtitle = models.CharField(max_length=300, default='Registered Persons with Disability')
    album_show_reg_number = models.BooleanField(default=True)
    album_show_disability = models.BooleanField(default=True)
    album_show_community = models.BooleanField(default=True)
    album_show_phone = models.BooleanField(default=False)
    album_photos_per_page = models.PositiveIntegerField(default=12)
    album_header_color = models.CharField(max_length=7, default='#1a56db')
    album_bg_color = models.CharField(max_length=7, default='#f9fafb')

    # Notification settings
    notify_new_pwd = models.BooleanField(default=True)
    notify_benefit_approval = models.BooleanField(default=True)
    notify_complaint_assigned = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'System Settings'

    def save(self, *args, **kwargs):
        self.pk = 1  # Enforce singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.system_name


# ─────────────────────────────────────────────────────────────────────────────
# notifications/models.py
# ─────────────────────────────────────────────────────────────────────────────
from django.conf import settings as django_settings


class Notification(models.Model):
    TYPE = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
        ('new_pwd', 'New PWD Registered'),
        ('benefit', 'Benefit Update'),
        ('complaint', 'Complaint Update'),
        ('audit', 'Audit Alert'),
        ('system', 'System'),
    ]
    recipient = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=TYPE, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, help_text="Frontend route")
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def mark_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])

    def __str__(self):
        return f"[{self.notification_type}] {self.title} → {self.recipient.full_name}"
