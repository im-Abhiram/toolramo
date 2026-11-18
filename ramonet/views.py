import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from devices.models import DeviceDefinition, DeviceCategory
from projects.models import NetworkProject
from commands.models import CommandEntry
from learning.models import LearningTopic
from troubleshooting.models import TroubleshootingScenario

@login_required(login_url='accounts:login')
def dashboard_view(request):
    """
    Ramonet Operations Dashboard View.
    Displays metrics, quick starter templates, recent activities, and shortcuts.
    Requires authentication; unauthenticated visitors are directed to login.
    """
    devices_count = DeviceDefinition.objects.count()
    categories_count = DeviceCategory.objects.count()
    commands_count = CommandEntry.objects.count()
    topics_count = LearningTopic.objects.count()
    scenarios_count = TroubleshootingScenario.objects.count()
    templates = NetworkProject.objects.filter(is_template=True)[:6]

    # Calculate SQLite file size on disk
    db_path = settings.DATABASES['default']['NAME']
    db_size_kb = round(os.path.getsize(db_path) / 1024, 1) if os.path.exists(db_path) else 0

    context = {
        'devices_count': devices_count,
        'categories_count': categories_count,
        'commands_count': commands_count,
        'topics_count': topics_count,
        'scenarios_count': scenarios_count,
        'templates': templates,
        'db_size_kb': db_size_kb,
        'storage_limit_mb': 512,
        'system_status': 'Operational',
        'health_score': 98,
    }
    return render(request, 'dashboard.html', context)
