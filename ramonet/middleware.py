"""
Ramonet Security Headers and CSP Middleware.
Enforces Content-Security-Policy, Permissions-Policy, and defensive HTTP headers.
"""
from typing import Callable
from django.http import HttpRequest, HttpResponse

class RamonetSecurityHeadersMiddleware:
    """
    Appends hardened HTTP security headers to all responses.
    """
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Content-Security-Policy
        # Self-contained offline assets with Bootstrap, FontAwesome icons, and Google Fonts (Manrope)
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data:; "
                "font-src 'self' https://fonts.gstatic.com data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )

        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # Modern referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Feature / Permissions Policy
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'

        # Cache control for sensitive administrative pages
        if request.path.startswith('/admin/') or request.path.startswith('/audit/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'

        return response
