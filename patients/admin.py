from django.contrib import admin
from .models import Patient, AuditLog

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'full_name', 'age', 'gender', 'contact_number', 'registered_at']
    search_fields = ['full_name', 'patient_id', 'contact_number']
    list_filter = ['gender', 'registered_at']
    readonly_fields = ['patient_id', 'registered_at']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'patient', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'description']
    readonly_fields = ['timestamp']
