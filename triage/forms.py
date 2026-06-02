from django import forms
from .models import TriageRecord, Consultation

class TriageForm(forms.ModelForm):
    class Meta:
        model = TriageRecord
        fields = [
            'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'heart_rate', 'respiratory_rate', 'oxygen_saturation',
            'weight', 'height',
            'chief_complaint', 'symptoms_description', 'priority', 'notes',
        ]
        widgets = {
            'temperature': forms.NumberInput(attrs={'class':'form-control','step':'0.01','placeholder':'e.g. 37.5'}),
            'blood_pressure_systolic': forms.NumberInput(attrs={'class':'form-control','placeholder':'e.g. 120'}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'class':'form-control','placeholder':'e.g. 80'}),
            'heart_rate': forms.NumberInput(attrs={'class':'form-control','placeholder':'e.g. 75'}),
            'respiratory_rate': forms.NumberInput(attrs={'class':'form-control','placeholder':'e.g. 16'}),
            'oxygen_saturation': forms.NumberInput(attrs={'class':'form-control','step':'0.1','placeholder':'e.g. 98.5'}),
            'weight': forms.NumberInput(attrs={'class':'form-control','step':'0.1'}),
            'height': forms.NumberInput(attrs={'class':'form-control','step':'0.1'}),
            'chief_complaint': forms.TextInput(attrs={'class':'form-control','placeholder':'Chief complaint...'}),
            'symptoms_description': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'priority': forms.Select(attrs={'class':'form-select'}),
            'notes': forms.Textarea(attrs={'class':'form-control','rows':2}),
        }

class ConsultationStatusForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['status', 'diagnosis', 'treatment_notes', 'prescription',
                  'admitted_ward', 'discharge_notes', 'follow_up_date']
        widgets = {
            'status': forms.Select(attrs={'class':'form-select'}),
            'diagnosis': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'treatment_notes': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'prescription': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'admitted_ward': forms.TextInput(attrs={'class':'form-control'}),
            'discharge_notes': forms.Textarea(attrs={'class':'form-control','rows':2}),
            'follow_up_date': forms.DateInput(attrs={'class':'form-control','type':'date'}),
        }
