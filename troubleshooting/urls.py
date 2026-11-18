from django.urls import path
from . import views

app_name = 'troubleshooting'

urlpatterns = [
    path('', views.lab_view, name='lab'),
    path('api/verify/', views.verify_solution_api, name='verify_api'),
    path('incident-response/', views.incident_simulator_view, name='incident_simulator'),
    path('api/incident-response/action/', views.api_incident_action, name='api_incident_action'),
]
