"""
benefits/models.py
"""
from django.db import models
from django.conf import settings
from auditlog.registry import auditlog


class DevelopmentPartner(models.Model):
    PARTNER_TYPE = [
        ('ngo', 'NGO'),
        ('government', 'Government Institution'),
        ('international', 'International Organization'),
        ('faith_based', 'Faith-Based Organization'),
        ('private', 'Private Sector'),
    ]
    name = models.CharField(max_length=200, unique=True)
    partner_type = models.CharField(max_length=30, choices=PARTNER_TYPE)
    acronym = models.CharField(max_length=20, blank=True)
    logo = models.ImageField(upload_to='partners/logos/', null=True, blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    district = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    registration_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BenefitCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Benefit Categories'


class Benefit(models.Model):
    STATUS = [
        ('active', 'Active'), ('suspended', 'Suspended'),
        ('completed', 'Completed'), ('pending', 'Pending'),
    ]
    FREQUENCY = [
        ('once', 'One-Time'), ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'), ('annually', 'Annual'),
        ('as_needed', 'As Needed'),
    ]
    partner = models.ForeignKey(DevelopmentPartner, on_delete=models.CASCADE, related_name='benefits')
    category = models.ForeignKey(BenefitCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    value_in_kind = models.CharField(max_length=200, blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY)
    eligibility_criteria = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='active')
    target_disability_types = models.ManyToManyField('pwds.DisabilityType', blank=True)
    max_beneficiaries = models.PositiveIntegerField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.partner.name}"


class BenefitAllocation(models.Model):
    STATUS = [
        ('pending', 'Pending'), ('approved', 'Approved'),
        ('disbursed', 'Disbursed'), ('rejected', 'Rejected'),
    ]
    pwd = models.ForeignKey('pwds.PWD', on_delete=models.CASCADE, related_name='benefit_allocations')
    benefit = models.ForeignKey(Benefit, on_delete=models.CASCADE, related_name='allocations')
    allocation_date = models.DateField()
    disbursement_date = models.DateField(null=True, blank=True)
    amount_disbursed = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    in_kind_description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_allocations'
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='recorded_allocations'
    )
    notes = models.TextField(blank=True)
    receipt_document = models.FileField(upload_to='benefits/receipts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-allocation_date']

    def __str__(self):
        return f"{self.pwd.full_name} — {self.benefit.name}"


auditlog.register(Benefit)
auditlog.register(BenefitAllocation)
auditlog.register(DevelopmentPartner)
