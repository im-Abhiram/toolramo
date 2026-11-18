from django.urls import path
from . import views

app_name = 'networktools'

urlpatterns = [
    path('', views.toolbox_view, name='toolbox'),
    path('discovery/', views.discovery_view, name='discovery'),
    path('api/discovery/', views.api_run_discovery, name='api_run_discovery'),
]
