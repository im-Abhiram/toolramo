# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PythonAnywhere WSGI Configuration File for Ramonet 2.0
# Copy and paste this file into your PythonAnywhere Web Tab:
# /var/www/ramonet_pythonanywhere_com_wsgi.py
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import sys

# 1. Add your project directory to the sys.path
path = '/home/ramonet/ramonet'
if path not in sys.path:
    sys.path.insert(0, path)

# 2. Configure Environment Variables for Production
os.environ['DJANGO_SETTINGS_MODULE'] = 'ramonet.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'ramonet.pythonanywhere.com,localhost,127.0.0.1'
os.environ['DJANGO_SECRET_KEY'] = 'ramonet-prod-sec-key-x9q8v7w6p5m4k3j2h1-9876543210-abcdef'
os.environ['SECURE_SSL_REDIRECT'] = 'True'
os.environ['ENABLE_HSTS'] = 'True'

# Gemini AI Chatbot API Key (set your key here or in .env)
# os.environ['GEMINI_API_KEY'] = 'your-gemini-api-key-here'

# 3. Initialize Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
