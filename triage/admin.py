from django.contrib import admin
from .models import TriageRecord, Consultation

@admin.register(TriageRecord)
class TriageRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'priority', 'chief_complaint', 'nurse', 'recorded_at']
    list_filter = ['priority', 'recorded_at']

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'status', 'priority', 'arrival_time']
    list_filter = ['status', 'priority', 'arrival_time']
