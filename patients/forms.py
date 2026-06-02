from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'full_name', 'age', 'gender', 'date_of_birth', 'blood_type',
            'address', 'contact_number', 'email',
            'emergency_contact_name', 'emergency_contact_number',
            'emergency_contact_relationship', 'known_allergies',
            'existing_conditions', 'department',
        ]
        widgets = {
            'full_name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'age':          forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 150}),
            'gender':       forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth':forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_type':   forms.Select(attrs={'class': 'form-select'}),
            'address':      forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email':        forms.EmailInput(attrs={'class': 'form-control'}),
            'emergency_contact_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'known_allergies':    forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'existing_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'department':   forms.Select(attrs={'class': 'form-select'}),
        }
