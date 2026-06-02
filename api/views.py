from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.db.models import Count
from patients.models import Patient
from triage.models import TriageRecord, Consultation
from .serializers import (
    PublicStatsSerializer, HIPAAMaskedPatientSerializer,
    AuthenticatedPatientSerializer
)

class PublicStatsView(APIView):
    """
    Public endpoint — returns aggregated regional statistics.
    No authentication required. No patient identifiable data returned.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        stats = {
            'region': 'Leyte',
            'total_patients': Patient.objects.count(),
            'critical_cases': TriageRecord.objects.filter(priority='critical').count(),
            'high_cases': TriageRecord.objects.filter(priority='high').count(),
            'medium_cases': TriageRecord.objects.filter(priority='medium').count(),
            'low_cases': TriageRecord.objects.filter(priority='low').count(),
            'waiting': Consultation.objects.filter(status='waiting').count(),
            'under_consultation': Consultation.objects.filter(status='consultation').count(),
            'treated_cases': Consultation.objects.filter(status='treated').count(),
            'admitted_cases': Consultation.objects.filter(status='admitted').count(),
            'discharged_cases': Consultation.objects.filter(status='discharged').count(),
        }
        serializer = PublicStatsSerializer(stats)
        return Response(serializer.data)


class PatientListView(APIView):
    """
    Patient list endpoint.
    - Unauthenticated: HIPAA-masked data only
    - Authenticated: Full data (role-dependent)
    """
    def get(self, request):
        patients = Patient.objects.all().order_by('-registered_at')[:50]
        if request.user.is_authenticated:
            serializer = AuthenticatedPatientSerializer(patients, many=True)
        else:
            serializer = HIPAAMaskedPatientSerializer(patients, many=True)
        return Response(serializer.data)


class PatientDetailView(APIView):
    """
    Single patient detail.
    - Unauthenticated: HIPAA-masked
    - Authenticated: full record (Anti-IDOR enforced)
    """
    def get(self, request, pk):
        try:
            patient = Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_authenticated:
            if request.user.role not in ('admin', 'doctor') and not request.user.is_staff:
                # Nurses only see their own registered/triaged patients
                if not (patient.registered_by == request.user or
                        TriageRecord.objects.filter(patient=patient, nurse=request.user).exists()):
                    return Response({
                        'patient_name': 'HIPAA Restricted',
                        'diagnosis': 'HIPAA Restricted',
                        'address': 'HIPAA Restricted',
                        'detail': 'Access restricted to authorized personnel only.'
                    }, status=status.HTTP_403_FORBIDDEN)
            serializer = AuthenticatedPatientSerializer(patient)
        else:
            serializer = HIPAAMaskedPatientSerializer(patient)

        return Response(serializer.data)


class QueueStatsView(APIView):
    """Live queue stats — public aggregated only."""
    permission_classes = [AllowAny]

    def get(self, request):
        data = {
            'queue_length': Consultation.objects.filter(status__in=['waiting','consultation']).count(),
            'by_priority': list(
                Consultation.objects.filter(status__in=['waiting','consultation'])
                .values('priority').annotate(count=Count('id'))
            ),
            'avg_wait_note': 'Estimated wait times are not disclosed publicly.'
        }
        return Response(data)
