import os
from django.shortcuts import render
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import AuditEvent
from .logger import SecurityLogger

def storage_view(request):
    """
    Ramonet Hybrid Storage Architecture & PythonAnywhere Quota Manager.
    """
    db_path = settings.DATABASES['default']['NAME']
    db_size_kb = round(os.path.getsize(db_path) / 1024, 1) if os.path.exists(db_path) else 0

    # Calculate static assets size
    static_size_bytes = 0
    for s_dir in settings.STATICFILES_DIRS:
        if os.path.exists(s_dir):
            for root, dirs, files in os.walk(s_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        static_size_bytes += os.path.getsize(fp)
                    except Exception:
                        pass
    static_size_mb = round(static_size_bytes / (1024 * 1024), 2)

    context = {
        'db_size_kb': db_size_kb,
        'static_size_mb': static_size_mb,
        'quota_mb': 512,
        'db_percent': round((db_size_kb / (512 * 1024)) * 100, 2),
        'page_title': 'Storage Management',
    }
    return render(request, 'audit/storage.html', context)

@api_view(['GET'])
@permission_classes([AllowAny])
def storage_stats_api(request):
    """
    Returns server-side SQLite and static asset sizes.
    """
    db_path = settings.DATABASES['default']['NAME']
    db_size_kb = round(os.path.getsize(db_path) / 1024, 1) if os.path.exists(db_path) else 0

    static_size_bytes = 0
    for s_dir in settings.STATICFILES_DIRS:
        if os.path.exists(s_dir):
            for root, dirs, files in os.walk(s_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        static_size_bytes += os.path.getsize(fp)
                    except Exception:
                        pass
    static_size_mb = round(static_size_bytes / (1024 * 1024), 2)

    return Response({
        'db_size_kb': db_size_kb,
        'static_size_mb': static_size_mb,
        'quota_mb': 512,
        'db_percent': round((db_size_kb / (512 * 1024)) * 100, 2)
    })

@login_required
def security_dashboard_view(request):
    """
    Administrator & Instructor Security Overview Dashboard.
    Displays real-time security events, brute-force logs, audit status, and OWASP Top 10 hardening scorecard.
    Restricted to staff, superusers, or instructor/architect roles.
    """
    role = getattr(getattr(request.user, 'profile', None), 'role', '')
    if not (request.user.is_staff or request.user.is_superuser or role in ('architect', 'instructor')):
        SecurityLogger.log_event(
            action='UNAUTHORIZED_SECURITY_DASHBOARD_ACCESS',
            module='audit',
            request=request,
            user=request.user,
            details={'attempted_role': role},
            severity='warning'
        )
        raise PermissionDenied("Access to the Administrator Security Dashboard is restricted.")

    recent_events = AuditEvent.objects.all().order_by('-created_at')[:50]
    total_events = AuditEvent.objects.count()
    failed_logins = AuditEvent.objects.filter(action='LOGIN_FAILED').count()
    blocked_attempts = AuditEvent.objects.filter(action='LOGIN_BLOCKED_RATE_LIMIT').count()
    exports_count = AuditEvent.objects.filter(action='EXPORT_DOCUMENTATION').count()

    context = {
        'page_title': 'Security Operations & Audit Center — Ramonet',
        'recent_events': recent_events,
        'total_events': total_events,
        'failed_logins': failed_logins,
        'blocked_attempts': blocked_attempts,
        'exports_count': exports_count,
        'debug_status': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'hsts_enabled': getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0,
        'session_cookie_secure': getattr(settings, 'SESSION_COOKIE_SECURE', False),
        'csrf_cookie_secure': getattr(settings, 'CSRF_COOKIE_SECURE', False),
    }
    return render(request, 'audit/security_dashboard.html', context)
