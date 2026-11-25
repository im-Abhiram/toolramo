"""
Django settings for ramonet enterprise network simulation platform.
Hardened according to OWASP Top 10 guidelines and PythonAnywhere deployment best practices.
"""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env file cleanly (zero third-party dependency required)
_ENV_FILE = BASE_DIR / '.env'
if _ENV_FILE.is_file():
    with open(_ENV_FILE, 'r', encoding='utf-8') as _f:
        for _raw_line in _f:
            _line = _raw_line.strip()
            if not _line or _line.startswith('#') or '=' not in _line:
                continue
            _k, _v = _line.split('=', 1)
            _k = _k.strip()
            _v = _v.strip().strip('"').strip("'")
            if _k:
                os.environ.setdefault(_k, _v)

# Security: Debug Flag
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

# Security: Secret Key Validation
DEFAULT_INSECURE_KEY = 'ramonet-enterprise-network-sim-secret-key-prod-2026'
RAW_SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')

if not RAW_SECRET_KEY:
    if DEBUG:
        SECRET_KEY = DEFAULT_INSECURE_KEY
    else:
        raise ImproperlyConfigured(
            "CRITICAL SECURITY FAILURE: DJANGO_SECRET_KEY environment variable must be set in production when DEBUG=False."
        )
else:
    if not DEBUG and RAW_SECRET_KEY == DEFAULT_INSECURE_KEY:
        raise ImproperlyConfigured(
            "CRITICAL SECURITY FAILURE: Default development SECRET_KEY detected in production environment."
        )
    SECRET_KEY = RAW_SECRET_KEY

# Security: Host Header Poisoning Protection (ALLOWED_HOSTS)
RAW_ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
if RAW_ALLOWED_HOSTS:
    ALLOWED_HOSTS = [h.strip() for h in RAW_ALLOWED_HOSTS.split(',') if h.strip()]
else:
    # PythonAnywhere production and local development defaults
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        'testserver',
        '[::1]',
        '.pythonanywhere.com',
        'ramonet.pythonanywhere.com',
    ]

# Security: CSRF Trusted Origins (Mandatory for Django 4.0+ over HTTPS / PythonAnywhere)
RAW_CSRF_TRUSTED_ORIGINS = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')
if RAW_CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in RAW_CSRF_TRUSTED_ORIGINS.split(',') if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'https://ramonet.pythonanywhere.com',
        'https://*.pythonanywhere.com',
        'http://ramonet.pythonanywhere.com',
        'http://*.pythonanywhere.com',
        'http://localhost',
        'http://127.0.0.1',
        'https://localhost',
        'https://127.0.0.1',
    ]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Third-party
    'rest_framework',
    
    # Ramonet Modular Apps
    'accounts',
    'devices',
    'projects',
    'topology',
    'configuration',
    'knowledgebase',
    'commands',
    'simulation',
    'networktools',
    'monitoring',
    'troubleshooting',
    'learning',
    'audit',
    'academy',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'ramonet.middleware.RamonetSecurityHeadersMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ramonet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.ramonet_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'ramonet.wsgi.application'

# Database
# Using SQLite with optimized PRAGMAs for PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Security: Password Policy Hardening (OWASP A07)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Security: Session & Cookie Hardening
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 10800  # 3 hours session timeout
SESSION_SAVE_EVERY_REQUEST = True

# Security: HTTP Defensive Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Production-Only HTTPS and Transport Protections
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    if os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() in ('true', '1'):
        SECURE_SSL_REDIRECT = True
    if os.environ.get('ENABLE_HSTS', 'False').lower() in ('true', '1'):
        SECURE_HSTS_SECONDS = 31536000
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (minimal for PythonAnywhere storage safety)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

# Auth redirects
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Gemini AI Chatbot Configuration (kept strictly server-side)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
GEMINI_MODELS = [
    m.strip()
    for m in os.environ.get(
        'GEMINI_MODELS',
        'gemini-flash-lite-latest,gemini-3-flash-preview,gemini-3.5-flash-lite,gemini-flash-latest,gemini-3.8-flash'
    ).split(',')
    if m.strip()
]

# Security Audit Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'ramonet.security': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
