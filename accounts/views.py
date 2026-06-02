from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import User
from .forms import LoginForm, UserCreationForm, UserEditForm
from .decorators import admin_required
from patients.models import AuditLog, Patient
from triage.models import Consultation

def home_view(request):
    """Public homepage shown when the site is first opened."""
    return render(request, 'home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        ip = request.META.get('REMOTE_ADDR')
        AuditLog.objects.create(
            user=user, action='login',
            description=f'Logged in from {ip}', ip_address=ip
        )
        messages.success(request, f'Welcome, {user.get_full_name_with_mi() or user.username}!')
        return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    AuditLog.objects.create(user=request.user, action='logout', description='Logged out')
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    user  = request.user
    today = timezone.now().date()

    # Scope to department unless admin
    if user.is_admin_user():
        p_qs = Patient.objects.all()
        c_qs = Consultation.objects.all()
    else:
        p_qs = Patient.objects.filter(department=user.department)
        c_qs = Consultation.objects.filter(patient__department=user.department)

    stats = {
        'total_patients':     p_qs.count(),
        'today_patients':     p_qs.filter(registered_at__date=today).count(),
        'waiting':            c_qs.filter(status='waiting').count(),
        'critical':           c_qs.filter(priority='critical', status__in=['waiting','consultation']).count(),
        'under_consultation': c_qs.filter(status='consultation').count(),
        'treated_today':      c_qs.filter(status='treated', updated_at__date=today).count(),
        'admitted':           c_qs.filter(status='admitted').count(),
        'discharged_today':   c_qs.filter(status='discharged', updated_at__date=today).count(),
    }

    recent_consultations = c_qs.filter(
        status__in=['waiting', 'consultation']
    ).select_related('patient', 'doctor').order_by('priority', 'arrival_time')[:10]

    recent_audit = AuditLog.objects.select_related('user', 'patient').order_by('-timestamp')[:10]

    dept_choices = dict(Patient.DEPARTMENT_CHOICES)
    dept_label   = dept_choices.get(user.department, 'All Departments') if not user.is_admin_user() else 'All Departments'

    return render(request, 'accounts/dashboard.html', {
        'stats': stats,
        'recent_consultations': recent_consultations,
        'recent_audit': recent_audit,
        'dept_label': dept_label,
    })

@admin_required
def user_list_view(request):
    users = User.objects.all().order_by('role', 'last_name', 'first_name')
    return render(request, 'accounts/user_list.html', {'users': users})

@admin_required
def user_create_view(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        AuditLog.objects.create(
            user=request.user, action='create',
            description=f'Created user: {user.username} ({user.role}) — {user.department}'
        )
        messages.success(request, f'User {user.username} created successfully.')
        # Redirect back to create page with empty form (cleared)
        return redirect('user_create')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create User'})

@admin_required
def user_edit_view(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=target_user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        AuditLog.objects.create(
            user=request.user, action='edit',
            description=f'Edited user: {target_user.username}'
        )
        messages.success(request, 'User updated.')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': f'Edit — {target_user.get_full_name_with_mi() or target_user.username}',
        'edit_mode': True,
        'target_user': target_user,
    })
