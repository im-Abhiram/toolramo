from django.urls import path
from simulation.views import trace_packet_api
from commands.views import execute_command_api
from knowledgebase.views import device_guide_api, how_to_connect_api, search_api
from projects.views import project_template_api
from audit.views import storage_stats_api
from troubleshooting.views import verify_solution_api
from monitoring.views import monitoring_stats_api
from academy.views import lab_verify_step_api, exam_evaluate_api, sync_progress_api, progressive_hint_api

urlpatterns = [
    # Simulation & Tracing
    path('simulation/trace/', trace_packet_api, name='api_trace_packet'),
    
    # CLI Command Execution
    path('commands/execute/', execute_command_api, name='api_execute_command'),
    
    # Knowledgebase & Assistant
    path('knowledgebase/guide/', device_guide_api, name='api_device_guide'),
    path('knowledgebase/how-to-connect/', how_to_connect_api, name='api_how_to_connect'),
    path('knowledgebase/search/', search_api, name='api_search'),
    
    # Projects
    path('projects/template/', project_template_api, name='api_project_template'),
    
    # Audit & Storage
    path('audit/storage-stats/', storage_stats_api, name='api_storage_stats'),
    
    # Troubleshooting
    path('troubleshooting/verify/', verify_solution_api, name='api_verify_solution'),
    
    # Monitoring
    path('monitoring/stats/', monitoring_stats_api, name='api_monitoring_stats'),
    
    # Ramonet Academy
    path('academy/verify-step/', lab_verify_step_api, name='api_academy_verify_step'),
    path('academy/exam-evaluate/', exam_evaluate_api, name='api_academy_exam_evaluate'),
    path('academy/sync-progress/', sync_progress_api, name='api_academy_sync_progress'),
    path('academy/hint/', progressive_hint_api, name='api_academy_hint'),
]
