from django.db import models

class DeviceConfigTemplate(models.Model):
    title = models.CharField(max_length=128)
    device_type = models.CharField(max_length=64)
    platform = models.CharField(max_length=32, default='cisco_ios')
    description = models.TextField(blank=True, default='')
    config_json = models.JSONField(default=dict)
    cli_commands = models.TextField(blank=True, default='')
    tags = models.JSONField(default=list, blank=True)
    is_starter = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['device_type', 'title']

    def __str__(self):
        return f"{self.title} ({self.device_type})"
