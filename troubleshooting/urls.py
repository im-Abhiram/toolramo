from django.urls import path
from . import views

app_name = 'troubleshooting'

urlpatterns = [
    path('', views.lab_view, name='lab'),
    path('api/verify/', views.verify_solution_api, name='verify_api'),
]
