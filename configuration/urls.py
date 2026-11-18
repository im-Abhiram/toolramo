from django.urls import path
from . import views

app_name = 'configuration'

urlpatterns = [
    path('assistant/', views.assistant_view, name='assistant'),
    path('switches/', views.switches_view, name='switches'),
    path('routers/', views.routers_view, name='routers'),
    path('firewalls/', views.firewalls_view, name='firewalls'),
    path('wireless/', views.wireless_view, name='wireless'),
    path('servers/', views.servers_view, name='servers'),
    path('storage/', views.storage_view, name='storage'),
    path('cctv/', views.cctv_view, name='cctv'),
    path('ipam/', views.ipam_view, name='ipam'),
    
    # API endpoints
    path('api/cctv-calc/', views.cctv_calculate_api, name='api_cctv_calc'),
    path('api/ipam-validate/', views.ipam_validate_api, name='api_ipam_validate'),
    path('automation/', views.automation_studio_view, name='automation_studio'),
    path('api/automation/execute/', views.api_run_automation, name='api_run_automation'),
    path('compliance/', views.compliance_centre_view, name='compliance_centre'),
    path('api/compliance/audit/', views.api_run_compliance_audit, name='api_run_compliance_audit'),
]
