"""
pwds/models.py — Core PWD Personal & Medical Records
"""
from django.db import models
from django.conf import settings
from auditlog.registry import auditlog
import uuid


class DisabilityType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=[
        ('physical', 'Physical'),
        ('sensory', 'Sensory'),
        ('intellectual', 'Intellectual'),
        ('psychosocial', 'Psychosocial'),
        ('multiple', 'Multiple'),
    ])

    def __str__(self):
        return self.name


class PWD(models.Model):
    """Primary PWD record — personal details"""
    GENDER = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    MARITAL = [
        ('single', 'Single'), ('married', 'Married'),
        ('divorced', 'Divorced'), ('widowed', 'Widowed'),
    ]
    EDUCATION = [
        ('none', 'None'), ('primary', 'Primary'), ('jhs', 'JHS'),
        ('shs', 'SHS'), ('tertiary', 'Tertiary'), ('vocational', 'Vocational'),
    ]
    EMPLOYMENT = [
        ('unemployed', 'Unemployed'), ('employed', 'Employed'),
        ('self_employed', 'Self Employed'), ('student', 'Student'),
        ('retired', 'Retired'),
    ]
    STATUS = [
        ('active', 'Active'), ('deceased', 'Deceased'),
        ('relocated', 'Relocated'), ('inactive', 'Inactive'),
    ]

    # Identity
    pwd_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    registration_number = models.CharField(max_length=30, unique=True, editable=False)
    photo = models.ImageField(upload_to='pwds/photos/', null=True, blank=True)

    # Personal
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER)
    marital_status = models.CharField(max_length=20, choices=MARITAL)
    nationality = models.CharField(max_length=50, default='Ghanaian')
    national_id = models.CharField(max_length=50, blank=True, help_text="Ghana Card / Passport / NHIS")
    national_id_type = models.CharField(max_length=30, blank=True)

    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    digital_address = models.CharField(max_length=30, blank=True, help_text="Ghana Post GPS")
    house_number = models.CharField(max_length=30, blank=True)
    street = models.CharField(max_length=100, blank=True)
    community = models.CharField(max_length=100)
    sub_district = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

    # Socioeconomic
    education_level = models.CharField(max_length=20, choices=EDUCATION)
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT)
    occupation = models.CharField(max_length=100, blank=True)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    household_size = models.PositiveIntegerField(default=1)
    caregiver_name = models.CharField(max_length=200, blank=True)
    caregiver_phone = models.CharField(max_length=20, blank=True)
    caregiver_relationship = models.CharField(max_length=50, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS, default='active')
    registration_date = models.DateField(auto_now_add=True)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='registered_pwds'
    )

    # AI fields
    ai_risk_score = models.FloatField(null=True, blank=True, help_text="AI-generated vulnerability score 0-100")
    ai_risk_label = models.CharField(max_length=20, blank=True, choices=[
        ('low', 'Low Risk'), ('medium', 'Medium Risk'), ('high', 'High Risk'), ('critical', 'Critical'),
    ])
    ai_summary = models.TextField(blank=True, help_text="AI-generated profile summary")
    ai_recommendations = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-registration_date']
        verbose_name = 'PWD'

    def __str__(self):
        return f"{self.full_name} ({self.registration_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        b = self.date_of_birth
        return today.year - b.year - ((today.month, today.day) < (b.month, b.day))

    def save(self, *args, **kwargs):
        if not self.registration_number:
            from datetime import date
            year = date.today().year
            count = PWD.objects.filter(registration_date__year=year).count() + 1
            self.registration_number = f"PWD-{year}-{count:05d}"
        super().save(*args, **kwargs)


class MedicalRecord(models.Model):
    """Medical/disability details for a PWD"""
    SEVERITY = [
        ('mild', 'Mild'), ('moderate', 'Moderate'),
        ('severe', 'Severe'), ('profound', 'Profound'),
    ]

    pwd = models.ForeignKey(PWD, on_delete=models.CASCADE, related_name='medical_records')
    disability_types = models.ManyToManyField(DisabilityType, related_name='pwds')
    disability_severity = models.CharField(max_length=20, choices=SEVERITY)
    disability_onset = models.CharField(max_length=20, choices=[
        ('congenital', 'Congenital (From Birth)'),
        ('acquired', 'Acquired'),
        ('progressive', 'Progressive'),
    ])
    onset_age = models.PositiveIntegerField(null=True, blank=True, help_text="Age when disability started")
    cause_of_disability = models.TextField(blank=True)

    # Medical support
    has_assistive_device = models.BooleanField(default=False)
    assistive_device_type = models.CharField(max_length=200, blank=True)
    device_condition = models.CharField(max_length=20, choices=[
        ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('needed', 'Needed'),
    ], blank=True)
    current_medications = models.TextField(blank=True)
    hospital_facility = models.CharField(max_length=200, blank=True)
    last_medical_checkup = models.DateField(null=True, blank=True)
    health_insurance = models.BooleanField(default=False)
    nhis_number = models.CharField(max_length=30, blank=True)
    additional_health_notes = models.TextField(blank=True)

    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='medical_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medical Record — {self.pwd.full_name}"


class PWDDocument(models.Model):
    """Attached documents for a PWD"""
    DOCTYPE = [
        ('birth_cert', 'Birth Certificate'),
        ('national_id', 'National ID'),
        ('medical_report', 'Medical Report'),
        ('disability_cert', 'Disability Certificate'),
        ('photo', 'Photo'),
        ('other', 'Other'),
    ]
    pwd = models.ForeignKey(PWD, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=30, choices=DOCTYPE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='pwds/documents/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.doc_type} — {self.pwd.full_name}"


# Register models for audit trail
auditlog.register(PWD)
auditlog.register(MedicalRecord)
