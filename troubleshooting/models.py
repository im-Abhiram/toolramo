from django.db import models

class TroubleshootingScenario(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    code = models.CharField(max_length=32, unique=True)
    title = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=16, choices=DIFFICULTY_CHOICES, default='beginner')
    category = models.CharField(max_length=64, default='IP & Routing')
    
    symptoms = models.TextField(help_text="Visible network symptoms reported by users or monitoring")
    description = models.TextField(help_text="Context and background story of the incident")
    
    # Topology definition (devices and connections) with the fault built-in
    initial_topology = models.JSONField(help_text="Network topology JSON containing the fault")
    
    fault_device_id = models.CharField(max_length=64, blank=True, default='')
    fault_type = models.CharField(max_length=64, help_text="e.g. wrong_gateway, vlan_mismatch, acl_block")
    fault_summary = models.TextField()
    
    suggested_commands = models.JSONField(default=list, blank=True)
    hints = models.JSONField(default=list, blank=True)
    
    # Verification rule dictionary to check whether the student fixed the issue
    verification_rule = models.JSONField(
        default=dict,
        help_text="Rules: {'test_type': 'ping', 'source': 'PC1', 'destination': '192.168.1.1', 'expected': 'success'}"
    )
    
    root_cause_explanation = models.TextField()
    recommended_solution = models.TextField()
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['difficulty', 'display_order', 'title']

    def __str__(self):
        return f"[{self.get_difficulty_display()}] {self.title}"
