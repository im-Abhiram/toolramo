from django.db import models

class DeviceCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True)
    icon = models.CharField(max_length=64, default='fa-network-wired')
    description = models.TextField(blank=True, default='')
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Device Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

class DeviceDefinition(models.Model):
    CLI_PLATFORMS = [
        ('cisco_ios', 'Cisco IOS CLI'),
        ('linux_shell', 'Linux Shell / iproute2'),
        ('mikrotik', 'MikroTik RouterOS'),
        ('windows_cmd', 'Windows CMD / PowerShell'),
        ('web_gui', 'Web Administration GUI Only'),
        ('none', 'Unmanaged / Passive'),
    ]

    name = models.CharField(max_length=100)
    category = models.ForeignKey(DeviceCategory, on_delete=models.CASCADE, related_name='devices')
    manufacturer = models.CharField(max_length=100, default='Generic / Standard')
    model_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=64, help_text="e.g. layer2_switch, core_router, firewall, ip_camera")
    description = models.TextField()
    icon = models.CharField(max_length=64, default='fa-server')
    is_layer3 = models.BooleanField(default=False)
    cli_platform = models.CharField(max_length=32, choices=CLI_PLATFORMS, default='cisco_ios')
    
    # JSON specifications for ports, protocols, and config templates
    available_interfaces = models.JSONField(
        default=list, 
        help_text="List of interfaces: [{'name': 'GigabitEthernet0/1', 'type': 'copper', 'speed': 1000, 'poe': False}]"
    )
    supported_protocols = models.JSONField(
        default=list, 
        help_text="List of protocols: ['IPv4', 'VLAN', 'STP', 'OSPF', 'NAT', 'DHCP']"
    )
    supported_connection_types = models.JSONField(
        default=list, 
        help_text="List of cable types: ['copper_straight', 'fiber', 'console']"
    )
    default_config = models.JSONField(
        default=dict, 
        help_text="Default running configuration dictionary"
    )
    
    # Hardware specs
    power_watts = models.FloatField(default=15.0)
    poe_budget_watts = models.FloatField(default=0.0)
    storage_capacity_gb = models.IntegerField(default=0)
    bandwidth_mbps = models.FloatField(default=0.0)
    
    # Educational guide content
    overview_text = models.TextField(blank=True, default='')
    troubleshooting_notes = models.TextField(blank=True, default='')
    security_notes = models.TextField(blank=True, default='')
    
    status = models.CharField(max_length=20, default='active')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def to_palette_json(self):
        import json
        payload = {
            'id': self.id,
            'name': self.name,
            'category': self.category.slug,
            'model_name': self.model_name,
            'manufacturer': self.manufacturer,
            'device_type': self.device_type,
            'icon': self.icon,
            'is_layer3': self.is_layer3,
            'cli_platform': self.cli_platform,
            'power_watts': self.power_watts,
            'poe_budget_watts': self.poe_budget_watts,
            'available_interfaces': self.available_interfaces,
            'supported_protocols': self.supported_protocols,
            'default_config': self.default_config
        }
        return json.dumps(payload)

    def __str__(self):
        return f"{self.name} ({self.manufacturer} {self.model_name})"
