from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from datetime import timedelta
from patients.models import Patient, AuditLog
from patients.views import patient_queryset_for_user
from .models import TriageRecord, Consultation
from .forms import TriageForm, ConsultationStatusForm
from accounts.decorators import doctor_required, nurse_required

def get_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0] if x else request.META.get('REMOTE_ADDR')

def consultation_queryset_for_user(user, status_filter=None):
    """Department-scoped consultation queryset."""
    if user.is_admin_user():
        qs = Consultation.objects.all()
    else:
        qs = Consultation.objects.filter(patient__department=user.department)
    if status_filter:
        qs = qs.filter(status__in=status_filter)
    return qs.select_related('patient', 'doctor', 'triage_record')

@login_required
@nurse_required
def triage_create_view(request, pk):
    base_qs = patient_queryset_for_user(request.user)
    patient = get_object_or_404(base_qs, pk=pk)
    form = TriageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        triage = form.save(commit=False)
        triage.patient = patient
        triage.nurse = request.user
        triage.save()
        consultation, created = Consultation.objects.get_or_create(
            patient=patient,
            status='waiting',
            defaults={
                'triage_record': triage,
                'priority': triage.priority,
                'arrival_time': timezone.now(),
            }
        )
        if not created:
            consultation.triage_record = triage
            consultation.priority = triage.priority
            consultation.save()
        AuditLog.objects.create(
            user=request.user, action='create', patient=patient,
            description=f'Triage recorded for {patient.patient_id}, priority: {triage.priority}',
            ip_address=get_ip(request)
        )
        messages.success(request, f'Triage recorded. Priority: {triage.get_priority_display()}')
        return redirect('patient_queue')
    return render(request, 'triage/triage_form.html', {'form': form, 'patient': patient})

@login_required
@doctor_required
def patient_queue_view(request):
    qs = consultation_queryset_for_user(
        request.user,
        status_filter=['waiting', 'consultation']
    )
    priority_filter = request.GET.get('priority', '')
    search = request.GET.get('q', '')
    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    if search:
        qs = qs.filter(
            Q(patient__full_name__icontains=search) |
            Q(patient__patient_id__icontains=search)
        )

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))

    # Scoped counts
    base = consultation_queryset_for_user(request.user)
    return render(request, 'triage/patient_queue.html', {
        'consultations': page,
        'priority_filter': priority_filter,
        'search': search,
        'waiting_count': base.filter(status='waiting').count(),
        'critical_count': base.filter(priority='critical', status__in=['waiting','consultation']).count(),
        'dept_label': dict(Patient.DEPARTMENT_CHOICES).get(request.user.department, 'All Departments'),
    })

@login_required
@doctor_required
def consultation_detail_view(request, pk):
    base = consultation_queryset_for_user(request.user)
    consultation = get_object_or_404(base, pk=pk)

    form = ConsultationStatusForm(request.POST or None, instance=consultation)
    if request.method == 'POST' and form.is_valid():
        old_status = consultation.status
        c = form.save(commit=False)
        c.doctor = request.user
        if c.status == 'consultation' and not consultation.consultation_start:
            c.consultation_start = timezone.now()
        if c.status in ('treated', 'discharged', 'admitted') and not consultation.consultation_end:
            c.consultation_end = timezone.now()
        c.save()
        AuditLog.objects.create(
            user=request.user, action='status_change', patient=consultation.patient,
            description=f'Status: {old_status} → {c.status} | {consultation.patient.patient_id}',
            ip_address=get_ip(request)
        )
        messages.success(request, f'Updated. Status: {c.get_status_display()}')
        return redirect('patient_queue')
    return render(request, 'triage/consultation_detail.html', {
        'consultation': consultation,
        'form': form,
    })

@login_required
@doctor_required
@require_POST
def bulk_action_view(request):
    action = request.POST.get('bulk_action')
    ids = request.POST.getlist('consultation_ids')
    if not ids:
        messages.warning(request, 'No patients selected.')
        return redirect('patient_queue')

    # Only act on consultations the user is allowed to see
    base = consultation_queryset_for_user(request.user)
    consultations = base.filter(pk__in=ids)
    count = consultations.count()

    status_map = {
        'discharge': 'discharged',
        'treat':     'treated',
        'admit':     'admitted',
        'consult':   'consultation',
    }
    new_status = status_map.get(action)
    if new_status:
        now = timezone.now()
        for c in consultations:
            old = c.status
            c.status = new_status
            c.doctor = request.user
            if new_status in ('treated', 'discharged', 'admitted') and not c.consultation_end:
                c.consultation_end = now
            c.save()
            AuditLog.objects.create(
                user=request.user,
                action='discharge' if new_status == 'discharged' else 'status_change',
                patient=c.patient,
                description=f'Bulk: {old} → {new_status}',
                ip_address=get_ip(request)
            )
        messages.success(request, f'{count} patient(s) updated to {new_status}.')
    else:
        messages.error(request, 'Invalid action.')
    return redirect('patient_queue')

@login_required
def reports_view(request):
    today     = timezone.now().date()
    week_ago  = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Admin sees all; others scoped to department
    if request.user.is_admin_user():
        p_qs = Patient.objects.all()
        c_qs = Consultation.objects.all()
        t_qs = TriageRecord.objects.all()
    else:
        p_qs = Patient.objects.filter(department=request.user.department)
        c_qs = Consultation.objects.filter(patient__department=request.user.department)
        t_qs = TriageRecord.objects.filter(patient__department=request.user.department)

    context = {
        'daily_count':    p_qs.filter(registered_at__date=today).count(),
        'weekly_count':   p_qs.filter(registered_at__date__gte=week_ago).count(),
        'monthly_count':  p_qs.filter(registered_at__date__gte=month_ago).count(),
        'critical_active': c_qs.filter(priority='critical', status__in=['waiting','consultation']).count(),
        'critical_total': t_qs.filter(priority='critical').count(),
        'admitted_total': c_qs.filter(status='admitted').count(),
        'discharged_total': c_qs.filter(status='discharged').count(),
        'treated_total':  c_qs.filter(status='treated').count(),
        'priority_breakdown': t_qs.values('priority').annotate(count=Count('id')),
        'status_breakdown':   c_qs.values('status').annotate(count=Count('id')),
        'dept_label': dict(Patient.DEPARTMENT_CHOICES).get(request.user.department, 'All Departments'),
    }
    return render(request, 'triage/reports.html', context)
