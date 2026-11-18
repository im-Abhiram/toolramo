from django.db import models
from django.contrib.auth.models import User

class AuditEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=64)
    module = models.CharField(max_length=64, default='general')
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.username if self.user else 'Guest'
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {user_name} - {self.action} ({self.module})"
