import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from devices.models import DeviceDefinition, DeviceCategory
from projects.models import NetworkProject
from commands.models import CommandEntry
from learning.models import LearningTopic
from troubleshooting.models import TroubleshootingScenario
from academy.models import UserLearningProfile, UserCourseProgress, Course

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
    courses_count = Course.objects.count()

    # User profile & gamification
    streak_days = 1
    user_xp = 0
    level = 1
    next_level_xp = 200
    level_progress_pct = 0
    completed_courses = 0

    if request.user.is_authenticated:
        profile, _ = UserLearningProfile.objects.get_or_create(user=request.user)
        user_xp = profile.total_points
        streak_days = max(1, profile.streak_days)
        level = max(1, user_xp // 200 + 1)
        next_level_xp = level * 200
        level_progress_pct = min(100, int((user_xp % 200) / 200 * 100)) if next_level_xp > 0 else 0
        completed_courses = UserCourseProgress.objects.filter(user=request.user, is_completed=True).count()

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
        'health_score': 100 if devices_count > 0 else 95,
        'user_xp': user_xp,
        'next_level_xp': next_level_xp,
        'level_progress_pct': level_progress_pct,
        'level': level,
        'streak_days': streak_days,
        'active_nodes': devices_count,
        'courses_count': courses_count,
        'completed_courses': completed_courses,
    }
    return render(request, 'dashboard.html', context)
