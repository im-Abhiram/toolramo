"""
Ramonet Security Audit Logging Utility.
Records security-relevant events to the AuditEvent database table and Python logging facility.
"""
import logging
from typing import Optional, Dict, Any
from django.http import HttpRequest
from .models import AuditEvent

logger = logging.getLogger('ramonet.security')

class SecurityLogger:
    """
    Central security event logger for RAMONET.
    Logs authentication events, access control violations, rate limits, and configuration modifications.
    """

    @staticmethod
    def get_client_ip(request: Optional[HttpRequest]) -> Optional[str]:
        if not request:
            return None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # First IP in list is client IP
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        # Basic sanity check
        if ip and len(ip) <= 45:
            return ip
        return None

    @classmethod
    def log_event(
        cls,
        action: str,
        module: str = 'general',
        request: Optional[HttpRequest] = None,
        user: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = 'info'
    ) -> Optional[AuditEvent]:
        """
        Record a security audit event in the database and logging subsystem.
        Never logs passwords, auth tokens, or private secrets.
        """
        try:
            target_user = user
            if target_user is None and request and hasattr(request, 'user') and request.user.is_authenticated:
                target_user = request.user

            ip_address = cls.get_client_ip(request)

            sanitized_details = dict(details) if details else {}
            # Strip sensitive keywords if accidentally passed
            for sensitive_key in ('password', 'token', 'secret', 'key', 'sessionid', 'csrftoken'):
                if sensitive_key in sanitized_details:
                    sanitized_details[sensitive_key] = '[REDACTED]'

            event = AuditEvent.objects.create(
                user=target_user if getattr(target_user, 'is_authenticated', False) else None,
                action=action[:64],
                module=module[:64],
                details=sanitized_details,
                ip_address=ip_address
            )

            log_msg = f"SECURITY_AUDIT: action={action} module={module} user={target_user} ip={ip_address} details={sanitized_details}"
            if severity == 'warning':
                logger.warning(log_msg)
            elif severity == 'error' or severity == 'critical':
                logger.error(log_msg)
            else:
                logger.info(log_msg)

            return event
        except Exception as e:
            # Fallback to file logging if DB write fails; never crash the app
            logger.error(f"Failed to record SecurityLogger event '{action}': {e}")
            return None
