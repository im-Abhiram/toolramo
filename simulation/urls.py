from django.urls import path
from . import views

app_name = 'simulation'

urlpatterns = [
    path('visualizer/', views.visualizer_view, name='visualizer'),
    path('trace/', views.trace_packet_api, name='trace_api'),
    path('analyzer/', views.packet_analyzer_view, name='packet_analyzer'),
    path('api/analyzer/capture/', views.api_generate_packet_capture, name='api_packet_capture'),
    path('what-if/', views.what_if_view, name='what_if'),
    path('api/what-if/simulate/', views.api_run_what_if, name='api_run_what_if'),
]
