from django.db import models

class MonitoringLog(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('danger', 'Critical / Error'),
        ('success', 'Resolved / Normal'),
    ]

    source_device = models.CharField(max_length=64)
    event_type = models.CharField(max_length=64, default='link_event')
    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES, default='info')
    message = models.CharField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.severity.upper()}] {self.source_device}: {self.message}"
