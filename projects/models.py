from django.db import models
from django.contrib.auth.models import User

class NetworkProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='network_projects')
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, blank=True)
    description = models.TextField(blank=True, default='')
    version = models.CharField(max_length=16, default='1.0.0')
    tags = models.JSONField(default=list, blank=True)
    
    device_count = models.PositiveIntegerField(default=0)
    connection_count = models.PositiveIntegerField(default=0)
    
    is_template = models.BooleanField(default=False)
    template_category = models.CharField(max_length=64, blank=True, default='')
    is_public = models.BooleanField(default=False)
    
    # Minimal metadata for hybrid storage sync
    metadata = models.JSONField(default=dict, blank=True, help_text="Summary metadata only; topology data resides in IndexedDB")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

class ProjectSnapshot(models.Model):
    project = models.ForeignKey(NetworkProject, on_delete=models.CASCADE, related_name='snapshots')
    title = models.CharField(max_length=128)
    snapshot_data = models.JSONField(help_text="Full topology and device configs snapshot")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
