from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_manager_view, name='manager'),
    path('template/', views.project_template_api, name='template_api'),
    path('documentation/', views.documentation_view, name='documentation'),
    path('api/documentation/export/', views.api_export_documentation, name='api_export_documentation'),
    path('scenarios/', views.scenarios_view, name='scenarios'),
    path('changes/', views.changes_view, name='changes'),
    path('api/changes/diff/', views.api_snapshot_diff, name='api_snapshot_diff'),
    path('backups/', views.backups_view, name='backups'),
    path('api/backups/restore/', views.api_backup_restore, name='api_backup_restore'),
    path('digital-twin/', views.digital_twin_view, name='digital_twin'),
    path('api/digital-twin/create/', views.api_create_twin, name='api_create_twin'),
    path('api/digital-twin/compare/', views.api_compare_twin, name='api_compare_twin'),
    path('api/digital-twin/commit/', views.api_commit_twin, name='api_commit_twin'),
    path('api/digital-twin/discard/', views.api_discard_twin, name='api_discard_twin'),
]
