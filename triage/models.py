from django.db import models
from django.conf import settings
from django.utils import timezone
from patients.models import Patient

class TriageRecord(models.Model):
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='triage_records')
    nurse = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='triage_records'
    )
    temperature = models.DecimalField(max_digits=5, decimal_places=2, help_text="°C")
    blood_pressure_systolic = models.PositiveIntegerField(help_text="mmHg")
    blood_pressure_diastolic = models.PositiveIntegerField(help_text="mmHg")
    heart_rate = models.PositiveIntegerField(help_text="bpm")
    respiratory_rate = models.PositiveIntegerField(help_text="breaths/min")
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, help_text="%")
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="cm")
    chief_complaint = models.CharField(max_length=500)
    symptoms_description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-recorded_at']

    def get_blood_pressure(self):
        return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"

    def __str__(self):
        return f"Triage: {self.patient.full_name} | {self.priority} | {self.recorded_at:%Y-%m-%d %H:%M}"


class Consultation(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('consultation', 'Under Consultation'),
        ('treated', 'Treated'),
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged'),
        ('transferred', 'Transferred'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='consultations'
    )
    triage_record = models.ForeignKey(
        TriageRecord, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='consultations'
    )
    diagnosis = models.TextField(blank=True)
    treatment_notes = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    priority = models.CharField(max_length=10, choices=TriageRecord.PRIORITY_CHOICES, default='medium')
    arrival_time = models.DateTimeField(default=timezone.now)
    consultation_start = models.DateTimeField(null=True, blank=True)
    consultation_end = models.DateTimeField(null=True, blank=True)
    admitted_ward = models.CharField(max_length=100, blank=True)
    discharge_notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            models.Case(
                models.When(priority='critical', then=0),
                models.When(priority='high', then=1),
                models.When(priority='medium', then=2),
                models.When(priority='low', then=3),
                default=4,
            ),
            'arrival_time'
        ]

    def __str__(self):
        return f"{self.patient.full_name} | {self.status} | {self.priority}"
