from django.urls import path
from . import views

app_name = 'academy'

urlpatterns = [
    # Dashboard & Catalogues
    path('', views.academy_dashboard_view, name='dashboard'),
    path('devices/', views.device_guides_catalogue_view, name='device_guides'),
    path('devices/<slug:slug>/', views.device_guide_detail_view, name='device_guide_detail'),

    # Course & Lesson Learning Paths
    path('course/<slug:slug>/', views.course_detail_view, name='course_detail'),
    path('course/<slug:course_slug>/lesson/<slug:lesson_slug>/', views.lesson_reader_view, name='lesson_reader'),
    path('course/<slug:course_slug>/lesson/<slug:lesson_slug>/lab/', views.practical_lab_view, name='practical_lab'),
    path('course/<slug:course_slug>/certificate/', views.certificate_view, name='certificate'),

    # Lab and Progress APIs
    path('api/verify-step/', views.lab_verify_step_api, name='api_verify_step'),
    path('api/exam-evaluate/', views.exam_evaluate_api, name='api_exam_evaluate'),
    path('api/sync-progress/', views.sync_progress_api, name='api_sync_progress'),
    path('api/hint/', views.progressive_hint_api, name='api_hint'),
]
