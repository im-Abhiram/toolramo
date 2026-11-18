from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.monitoring_view, name='dashboard'),
    path('api/stats/', views.monitoring_stats_api, name='stats_api'),
    path('security-audit/', views.security_audit_view, name='security_audit'),
    path('api/security-audit/', views.api_run_security_audit, name='api_run_security_audit'),
    path('capacity/', views.capacity_view, name='capacity'),
    path('api/capacity/', views.api_capacity_stats, name='api_capacity_stats'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('api/alerts/list/', views.api_get_alerts, name='api_get_alerts'),
    path('api/alerts/acknowledge/', views.api_acknowledge_alert, name='api_acknowledge_alert'),
    path('api/alerts/resolve/', views.api_resolve_alert, name='api_resolve_alert'),
    path('ha-lab/', views.ha_lab_view, name='ha_lab'),
    path('api/ha-lab/simulate/', views.api_ha_simulate, name='api_ha_simulate'),
    path('qos/', views.qos_view, name='qos'),
    path('api/qos/simulate/', views.api_qos_simulate, name='api_qos_simulate'),
]
