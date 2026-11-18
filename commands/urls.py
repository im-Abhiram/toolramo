from django.urls import path
from . import views

app_name = 'commands'

urlpatterns = [
    path('', views.command_library_view, name='library'),
    path('execute/', views.execute_command_api, name='execute_command_api'),
]
