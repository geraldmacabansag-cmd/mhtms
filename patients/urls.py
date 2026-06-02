from django.urls import path
from . import views

urlpatterns = [
    path('', views.patient_list_view, name='patient_list'),
    path('register/', views.patient_create_view, name='patient_create'),
    path('<int:pk>/', views.patient_detail_view, name='patient_detail'),
    path('<int:pk>/edit/', views.patient_edit_view, name='patient_edit'),
]
