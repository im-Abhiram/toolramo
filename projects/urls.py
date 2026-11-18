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
]
