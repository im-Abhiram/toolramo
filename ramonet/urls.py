"""
URL configuration for Ramonet enterprise network simulation platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemaps import (
    StaticViewSitemap,
    TopicSitemap,
    CourseSitemap,
    LessonSitemap,
    DeviceGuideSitemap
)
from networktools import views as networktools_views

sitemaps = {
    'static': StaticViewSitemap,
    'topics': TopicSitemap,
    'courses': CourseSitemap,
    'lessons': LessonSitemap,
    'devices': DeviceGuideSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_view, name='dashboard'),
    
    # Technical SEO Endpoints
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', views.robots_txt_view, name='robots_txt'),

    # High-Traffic Dedicated SEO Landing Routes
    path('tools/subnet-calculator/', networktools_views.subnet_calculator_view, name='seo_subnet_calculator'),
    path('tools/ports-cheat-sheet/', networktools_views.ports_cheatsheet_view, name='seo_ports_cheatsheet'),
    path('tools/osi-model/', networktools_views.osi_model_view, name='seo_osi_model'),
    
    # Core Modular Web Views
    path('accounts/', include('accounts.urls')),
    path('topology/', include('topology.urls')),
    path('devices/', include('devices.urls')),
    path('configuration/', include('configuration.urls')),
    path('commands/', include('commands.urls')),
    path('simulation/', include('simulation.urls')),
    path('networktools/', include('networktools.urls')),
    path('monitoring/', include('monitoring.urls')),
    path('troubleshooting/', include('troubleshooting.urls')),
    path('learning/', include('learning.urls')),
    path('academy/', include('academy.urls')),
    path('projects/', include('projects.urls')),
    path('storage/', include('audit.urls')),
    
    # REST API Endpoints
    path('api/', include('ramonet.api_urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

