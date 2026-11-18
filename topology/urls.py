from django.urls import path
from . import views

app_name = 'topology'

urlpatterns = [
    path('designer/', views.designer_view, name='designer'),
    path('rack/', views.rack_designer_view, name='rack'),
    path('rack-designer/', views.rack_designer_view, name='rack_designer'),
    path('api/validate-rack/', views.api_validate_rack_layout, name='api_validate_rack'),
]
