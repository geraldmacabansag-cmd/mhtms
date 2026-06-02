from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from .models import Patient, AuditLog
from .forms import PatientForm
from triage.models import TriageRecord, Consultation

def get_client_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0] if x else request.META.get('REMOTE_ADDR')

def patient_queryset_for_user(user):
    """
    Returns filtered Patient queryset based on user role and department.
    - Admin / superuser : all patients
    - Doctor / Nurse    : only patients in their department
    """
    if user.is_admin_user():
        return Patient.objects.all()
    # Doctors and nurses only see their department's patients
    return Patient.objects.filter(department=user.department)

@login_required
def patient_list_view(request):
    qs = patient_queryset_for_user(request.user)
    q        = request.GET.get('q', '')
    priority = request.GET.get('priority', '')
    status   = request.GET.get('status', '')

    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(patient_id__icontains=q) |
            Q(contact_number__icontains=q)
        )
    if priority:
        qs = qs.filter(triage_records__priority=priority).distinct()
    if status:
        qs = qs.filter(consultations__status=status).distinct()

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'patients/patient_list.html', {
        'patients': page,
        'q': q, 'priority': priority, 'status': status,
    })

@login_required
def patient_detail_view(request, pk):
    base_qs = patient_queryset_for_user(request.user)
    patient = get_object_or_404(base_qs, pk=pk)   # 404 (not 403) to avoid info leak

    AuditLog.objects.create(
        user=request.user, action='view', patient=patient,
        description=f'Viewed patient profile: {patient.patient_id}',
        ip_address=get_client_ip(request)
    )
    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'triage_records': patient.triage_records.all(),
        'consultations': patient.consultations.all(),
    })

@login_required
def patient_create_view(request):
    if request.user.role not in ('nurse', 'admin') and not request.user.is_admin_user():
        raise PermissionDenied
    form = PatientForm(request.POST or None)

    # Pre-fill department from nurse's own department
    if request.method == 'GET' and request.user.department:
        form.initial['department'] = request.user.department

    if request.method == 'POST' and form.is_valid():
        patient = form.save(commit=False)
        patient.registered_by = request.user
        patient.save()
        AuditLog.objects.create(
            user=request.user, action='create', patient=patient,
            description=f'Registered new patient: {patient.full_name} → dept: {patient.department}',
            ip_address=get_client_ip(request)
        )
        messages.success(request, f'Patient {patient.full_name} registered. ID: {patient.patient_id}')
        return redirect('triage_create', pk=patient.pk)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Register New Patient'})

@login_required
def patient_edit_view(request, pk):
    base_qs = patient_queryset_for_user(request.user)
    patient = get_object_or_404(base_qs, pk=pk)

    form = PatientForm(request.POST or None, instance=patient)
    if request.method == 'POST' and form.is_valid():
        form.save()
        AuditLog.objects.create(
            user=request.user, action='edit', patient=patient,
            description=f'Edited patient record: {patient.patient_id}',
            ip_address=get_client_ip(request)
        )
        messages.success(request, 'Patient record updated.')
        return redirect('patient_detail', pk=pk)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Edit Patient'})
