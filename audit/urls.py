from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.storage_view, name='storage'),
    path('security/', views.security_dashboard_view, name='security_dashboard'),
    path('api/storage-stats/', views.storage_stats_api, name='storage_stats_api'),
]
