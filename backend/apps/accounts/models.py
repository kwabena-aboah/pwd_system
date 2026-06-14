"""
accounts/models.py — Custom User with Roles
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    DISTRICT_OFFICER = 'district_officer', 'District Officer'
    DATA_ENTRY = 'data_entry', 'Data Entry Officer'
    SOCIAL_WORKER = 'social_worker', 'Social Worker'
    NGO_PARTNER = 'ngo_partner', 'NGO Partner'
    GOVT_OFFICER = 'govt_officer', 'Government Officer'
    AUDITOR = 'auditor', 'Auditor'
    VIEWER = 'viewer', 'Viewer (Read Only)'


class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.VIEWER)
    phone = models.CharField(max_length=20, blank=True)
    district = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=200, blank=True, help_text="NGO/Govt institution name")
    profile_photo = models.ImageField(upload_to='staff/photos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def full_name(self):
        return self.get_full_name() or self.username

    def has_role(self, *roles):
        return self.role in roles

    @property
    def can_edit(self):
        return self.role in [Role.SUPER_ADMIN, Role.DISTRICT_OFFICER, Role.DATA_ENTRY, Role.SOCIAL_WORKER]

    @property
    def can_approve_benefits(self):
        return self.role in [Role.SUPER_ADMIN, Role.DISTRICT_OFFICER]

    @property
    def is_partner(self):
        return self.role in [Role.NGO_PARTNER, Role.GOVT_OFFICER]
