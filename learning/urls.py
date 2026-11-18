from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.learning_center_view, name='center'),
    path('topic/<slug:slug>/', views.topic_detail_view, name='topic_detail'),
]
