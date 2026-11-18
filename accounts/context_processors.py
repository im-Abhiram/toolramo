import os
from django.conf import settings

def ramonet_context(request):
    """
    Global context processor providing Ramonet metadata, storage status, and navigation states.
    """
    db_size_kb = 0
    db_path = settings.DATABASES['default']['NAME']
    if os.path.exists(db_path):
        db_size_kb = round(os.path.getsize(db_path) / 1024, 1)

    return {
        'APP_NAME': 'Ramonet',
        'APP_VERSION': '2.0.0',
        'APP_SUBTITLE': 'Enterprise Network Simulator & Learning Platform',
        'DB_SIZE_KB': db_size_kb,
        'PYTHONANYWHERE_STORAGE_LIMIT_MB': 512,
        'USER_PREFERENCES': {
            'theme': 'dark-navy',
            'sidebar_collapsed': False,
        }
    }
