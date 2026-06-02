from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, DEPARTMENT_CHOICES

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'loginPassword',
            'autocomplete': 'current-password'
        })
    )

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_password1'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_password2'})
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'middle_initial', 'last_name',
            'email', 'role', 'phone', 'department', 'license_number'
        ]
        widgets = {
            'username':       forms.TextInput(attrs={'class': 'form-control'}),
            'first_name':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'middle_initial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M. (optional)', 'maxlength': '5'}),
            'last_name':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email':          forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':          forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role':           forms.Select(attrs={'class': 'form-select'}),
            'department':     forms.Select(attrs={'class': 'form-select'}, choices=DEPARTMENT_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['middle_initial'].required = False
        self.fields['email'].required = False
        self.fields['phone'].required = False
        self.fields['license_number'].required = False

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match.")
        return p2

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        dept = cleaned.get('department')
        if role in ('doctor', 'nurse') and not dept:
            self.add_error('department', 'Department is required for doctors and nurses.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        # Ensure admin role gets is_staff
        if user.role == 'admin':
            user.is_staff = True
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'middle_initial', 'last_name',
            'email', 'role', 'phone', 'department', 'license_number', 'is_active'
        ]
        widgets = {
            'first_name':     forms.TextInput(attrs={'class': 'form-control'}),
            'middle_initial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M. (optional)', 'maxlength': '5'}),
            'last_name':      forms.TextInput(attrs={'class': 'form-control'}),
            'email':          forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':          forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'role':           forms.Select(attrs={'class': 'form-select'}),
            'department':     forms.Select(attrs={'class': 'form-select'}, choices=DEPARTMENT_CHOICES),
            'is_active':      forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['middle_initial'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == 'admin':
            user.is_staff = True
        if commit:
            user.save()
        return user
