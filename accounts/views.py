from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from axes.decorators import axes_dispatch
from axes.signals import user_locked_out
from django.dispatch import receiver
from .models import User
from .forms import LoginForm, UserCreationForm, UserEditForm
from .decorators import admin_required
from patients.models import AuditLog, Patient
from triage.models import Consultation, TriageRecord


def home_view(request):
    """Public homepage shown when the site is first opened."""
    return render(request, 'home.html')


# ── Signal receiver — fires when axes locks an account ────────────────
# This runs automatically when axes decides to lock out a username.
# It writes a clear LOCKOUT entry to the audit log so admins can see it.
@receiver(user_locked_out)
def on_user_locked_out(sender, request, username, ip_address, **kwargs):
    AuditLog.objects.create(
        user=None,
        action='login_failed',
        description=f'🔒 ACCOUNT LOCKED OUT: username "{username}" — too many failed attempts from IP: {ip_address}',
        ip_address=ip_address,
    )


@axes_dispatch
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Login view protected by django-axes.
    @axes_dispatch checks if the username is locked out BEFORE processing
    the form. If locked, it shows the 403_axes.html page immediately.
    Only the specific username is locked — other accounts are not affected.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        ip = request.META.get('REMOTE_ADDR', 'unknown')

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # NIST audit log — successful login
            AuditLog.objects.create(
                user=user,
                action='login',
                description=f'Successful login from IP: {ip}',
                ip_address=ip,
            )
            messages.success(request, f'Welcome, {user.get_full_name_with_mi() or user.username}!')
            return redirect('dashboard')

        else:
            # NIST audit log — record every failed attempt with the attempted username
            attempted_username = request.POST.get('username', 'unknown')
            AuditLog.objects.create(
                user=None,
                action='login_failed',
                description=f'Failed login attempt — username: "{attempted_username}" from IP: {ip}',
                ip_address=ip,
            )

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    AuditLog.objects.create(
        user=request.user,
        action='logout',
        description=f'Logged out from IP: {request.META.get("REMOTE_ADDR", "unknown")}',
    )
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    user  = request.user
    today = timezone.now().date()

    # ── Date range filter (interactive dashboard filtering) ───────────
    date_from_str = request.GET.get('date_from', '')
    date_to_str   = request.GET.get('date_to', '')
    status_filter = request.GET.get('status', '')

    try:
        date_from = timezone.datetime.strptime(date_from_str, '%Y-%m-%d').date() if date_from_str else today
    except ValueError:
        date_from = today
    try:
        date_to = timezone.datetime.strptime(date_to_str, '%Y-%m-%d').date() if date_to_str else today
    except ValueError:
        date_to = today

    # Ensure date_from is not after date_to
    if date_from > date_to:
        date_from = date_to

    if user.is_admin_user():
        p_qs = Patient.objects.all()
        c_qs = Consultation.objects.all()
    else:
        p_qs = Patient.objects.filter(department=user.department)
        c_qs = Consultation.objects.filter(patient__department=user.department)

    # Apply status filter to consultations if provided
    c_qs_filtered = c_qs.filter(status=status_filter) if status_filter else c_qs

    # Date-range aware stats
    stats = {
        'total_patients':     p_qs.count(),
        'today_patients':     p_qs.filter(registered_at__date__gte=date_from, registered_at__date__lte=date_to).count(),
        'waiting':            c_qs_filtered.filter(status='waiting').count() if not status_filter else c_qs_filtered.count(),
        'critical':           c_qs.filter(priority='critical', status__in=['waiting','consultation']).count(),
        'under_consultation': c_qs_filtered.filter(status='consultation').count() if not status_filter else c_qs_filtered.filter(status='consultation').count(),
        'treated_today':      c_qs.filter(status='treated', updated_at__date__gte=date_from, updated_at__date__lte=date_to).count(),
        'admitted':           c_qs.filter(status='admitted').count(),
        'discharged_today':   c_qs.filter(status='discharged', updated_at__date__gte=date_from, updated_at__date__lte=date_to).count(),
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
        # pass filter state back to template
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to':   date_to.strftime('%Y-%m-%d'),
        'status_filter': status_filter,
        'status_choices': Consultation.STATUS_CHOICES,
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
