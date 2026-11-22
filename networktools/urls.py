from django.urls import path
from . import views

app_name = 'networktools'

urlpatterns = [
    path('', views.toolbox_view, name='toolbox'),
    path('subnet-calculator/', views.subnet_calculator_view, name='subnet_calculator'),
    path('ports-cheat-sheet/', views.ports_cheatsheet_view, name='ports_cheatsheet'),
    path('osi-model/', views.osi_model_view, name='osi_model'),
    path('discovery/', views.discovery_view, name='discovery'),
    path('api/discovery/', views.api_run_discovery, name='api_run_discovery'),
    path('capacity-cost/', views.capacity_cost_view, name='capacity_cost'),
    path('api/capacity-cost/calculate/', views.api_calculate_capacity_cost, name='api_calculate_capacity_cost'),
]
