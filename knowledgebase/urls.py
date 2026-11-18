from django.urls import path
from . import views

app_name = 'knowledgebase'

urlpatterns = [
    path('guide/', views.device_guide_api, name='device_guide_api'),
    path('how-to-connect/', views.how_to_connect_api, name='how_to_connect_api'),
    path('search/', views.search_api, name='search_api'),
]
