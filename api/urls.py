from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.PublicStatsView.as_view(), name='api_stats'),
    path('queue/', views.QueueStatsView.as_view(), name='api_queue'),
    path('patients/', views.PatientListView.as_view(), name='api_patients'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='api_patient_detail'),
]
