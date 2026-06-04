from django.db import models
from django.conf import settings
from django.utils import timezone

class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    BLOOD_TYPE_CHOICES = [
        ('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
        ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-'),('unknown','Unknown'),
    ]
    DEPARTMENT_CHOICES = [
        ('triage_emergency', 'Triage / Emergency'),
        ('opd', 'Outpatient Department (OPD)'),
        ('internal_medicine', 'Internal Medicine'),
        ('pediatrics', 'Pediatrics'),
        ('ob_gyn', 'OB-GYN / Maternal Health'),
        ('laboratory', 'Laboratory'),
        ('pharmacy', 'Pharmacy'),
        ('admitting_records', 'Admitting / Medical Records'),
    ]

    patient_id = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPE_CHOICES, default='unknown')
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    emergency_contact_name = models.CharField(max_length=200)
    emergency_contact_number = models.CharField(max_length=20)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    known_allergies = models.TextField(blank=True)
    existing_conditions = models.TextField(blank=True)
    department = models.CharField(
        max_length=50, choices=DEPARTMENT_CHOICES,
        default='triage_emergency',
        help_text='Department this patient is assigned to'
    )
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='registered_patients'
    )
    registered_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-registered_at']

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last = Patient.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.patient_id = f"PT-{next_id:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_id} — {self.full_name}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('edit', 'Edited'),
        ('status_change', 'Status Changed'),
        ('discharge', 'Discharged'),
        ('view', 'Viewed'),
        ('login', 'Login'),
        ('login_failed', 'Failed Login'),
        ('logout', 'Logout'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} | {self.user} | {self.action}"
