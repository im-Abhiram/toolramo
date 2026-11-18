"""
URL configuration for Ramonet enterprise network simulation platform.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_view, name='dashboard'),
    
    # Core Modular Web Views
    path('accounts/', include('accounts.urls')),
    path('topology/', include('topology.urls')),
    path('devices/', include('devices.urls')),
    path('configuration/', include('configuration.urls')),
    path('commands/', include('commands.urls')),
    path('simulation/', include('simulation.urls')),
    path('networktools/', include('networktools.urls')),
    path('monitoring/', include('monitoring.urls')),
    path('troubleshooting/', include('troubleshooting.urls')),
    path('learning/', include('learning.urls')),
    path('academy/', include('academy.urls')),
    path('projects/', include('projects.urls')),
    path('storage/', include('audit.urls')),
    
    # REST API Endpoints
    path('api/', include('ramonet.api_urls')),
]
