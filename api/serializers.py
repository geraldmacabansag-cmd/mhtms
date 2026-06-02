from rest_framework import serializers
from patients.models import Patient
from triage.models import TriageRecord, Consultation

class PublicStatsSerializer(serializers.Serializer):
    region = serializers.CharField()
    total_patients = serializers.IntegerField()
    critical_cases = serializers.IntegerField()
    high_cases = serializers.IntegerField()
    medium_cases = serializers.IntegerField()
    low_cases = serializers.IntegerField()
    waiting = serializers.IntegerField()
    under_consultation = serializers.IntegerField()
    treated_cases = serializers.IntegerField()
    admitted_cases = serializers.IntegerField()
    discharged_cases = serializers.IntegerField()

class HIPAAMaskedPatientSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    contact_number = serializers.SerializerMethodField()
    emergency_contact = serializers.SerializerMethodField()
    diagnosis = serializers.SerializerMethodField()
    patient_id = serializers.CharField()
    age_group = serializers.SerializerMethodField()
    gender = serializers.CharField()

    class Meta:
        model = Patient
        fields = ['patient_id', 'patient_name', 'age_group', 'gender',
                  'address', 'contact_number', 'emergency_contact', 'diagnosis']

    def get_patient_name(self, obj): return "HIPAA Restricted"
    def get_address(self, obj): return "HIPAA Restricted"
    def get_contact_number(self, obj): return "HIPAA Restricted"
    def get_emergency_contact(self, obj): return "HIPAA Restricted"
    def get_diagnosis(self, obj): return "HIPAA Restricted"
    def get_age_group(self, obj):
        age = obj.age
        if age < 13: return "Child (0-12)"
        elif age < 18: return "Adolescent (13-17)"
        elif age < 60: return "Adult (18-59)"
        else: return "Senior (60+)"

class AuthenticatedPatientSerializer(serializers.ModelSerializer):
    registered_by = serializers.StringRelatedField()
    latest_priority = serializers.SerializerMethodField()
    latest_status = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'

    def get_latest_priority(self, obj):
        tr = obj.triage_records.first()
        return tr.priority if tr else None

    def get_latest_status(self, obj):
        c = obj.consultations.first()
        return c.status if c else None
