from django.urls import path
from . import views

urlpatterns = [
    path('patient/<int:pk>/triage/', views.triage_create_view, name='triage_create'),
    path('queue/', views.patient_queue_view, name='patient_queue'),
    path('consultation/<int:pk>/', views.consultation_detail_view, name='consultation_detail'),
    path('bulk-action/', views.bulk_action_view, name='bulk_action'),
    path('reports/', views.reports_view, name='reports'),
]
