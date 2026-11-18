from django.db import models

class KnowledgeArticle(models.Model):
    CATEGORY_CHOICES = [
        ('device_guide', 'Device Learning Guide'),
        ('concept', 'Networking Concept'),
        ('how_to', 'Configuration Tutorial'),
        ('troubleshooting', 'Troubleshooting Procedure'),
        ('faq', 'Frequently Asked Question'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default='concept')
    device_type = models.CharField(max_length=64, blank=True, default='')
    summary = models.TextField()
    content = models.TextField(help_text="Detailed markdown or HTML content")
    
    # 15-section structured guide data if it's a device guide
    structured_guide = models.JSONField(default=dict, blank=True, help_text="Structured 15-section device guide data")
    
    search_keywords = models.TextField(blank=True, default='', help_text="Space or comma-separated keywords for local search")
    related_commands = models.JSONField(default=list, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'title']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

class ConnectionRule(models.Model):
    source_category = models.CharField(max_length=64)
    target_category = models.CharField(max_length=64)
    is_supported = models.BooleanField(default=True)
    recommended_cable = models.CharField(max_length=64, default='Copper Straight-Through (Cat6)')
    alternative_cables = models.JSONField(default=list, blank=True)
    required_ports = models.CharField(max_length=128, default='RJ45 Gigabit Ethernet')
    interface_compatibility = models.TextField(blank=True, default='')
    ip_requirements = models.TextField(blank=True, default='')
    vlan_requirements = models.TextField(blank=True, default='')
    gateway_requirements = models.TextField(blank=True, default='')
    power_requirements = models.TextField(blank=True, default='')
    step_by_step_instructions = models.JSONField(default=list, blank=True)
    verification_commands = models.JSONField(default=list, blank=True)
    troubleshooting_tips = models.JSONField(default=list, blank=True)

    class Meta:
        unique_together = ('source_category', 'target_category')
        ordering = ['source_category', 'target_category']

    def __str__(self):
        return f"{self.source_category} <-> {self.target_category}"
