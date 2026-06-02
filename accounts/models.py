from django.contrib.auth.models import AbstractUser
from django.db import models

DEPARTMENT_CHOICES = [
    ('', 'Select Department'),
    ('triage_emergency', 'Triage / Emergency'),
    ('opd', 'Outpatient Department (OPD)'),
    ('internal_medicine', 'Internal Medicine'),
    ('pediatrics', 'Pediatrics'),
    ('ob_gyn', 'OB-GYN / Maternal Health'),
    ('laboratory', 'Laboratory'),
    ('pharmacy', 'Pharmacy'),
    ('admitting_records', 'Admitting / Medical Records'),
]

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='nurse')
    middle_initial = models.CharField(max_length=5, blank=True, help_text='Optional (e.g. M.)')
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True)
    license_number = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        # Superusers and staff always get admin role
        if self.is_superuser or self.is_staff:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def get_full_name_with_mi(self):
        parts = [self.first_name]
        if self.middle_initial:
            mi = self.middle_initial.strip('.')
            parts.append(f"{mi}.")
        parts.append(self.last_name)
        return ' '.join(p for p in parts if p).strip() or self.username

    def is_doctor(self):
        return self.role == 'doctor'

    def is_nurse(self):
        return self.role == 'nurse'

    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser

    def __str__(self):
        name = self.get_full_name_with_mi() or self.username
        return f"{name} ({self.get_role_display()})"
