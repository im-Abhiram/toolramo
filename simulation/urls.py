from django.urls import path
from . import views

app_name = 'simulation'

urlpatterns = [
    path('visualizer/', views.visualizer_view, name='visualizer'),
    path('trace/', views.trace_packet_api, name='trace_api'),
]
