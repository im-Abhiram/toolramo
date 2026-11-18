from django.db import models

class CommandEntry(models.Model):
    PLATFORM_CHOICES = [
        ('cisco_ios', 'Cisco IOS'),
        ('linux_shell', 'Linux Shell (iproute2/sys)'),
        ('mikrotik', 'MikroTik RouterOS'),
        ('windows_cmd', 'Windows Command Prompt / Netsh'),
        ('iptables', 'Linux Firewall (iptables / ufw)'),
        ('frr', 'FRRouting Suite'),
        ('general', 'General Network Diagnostic'),
    ]

    MODE_CHOICES = [
        ('user_exec', 'User EXEC Mode (>)'),
        ('priv_exec', 'Privileged EXEC Mode (#)'),
        ('global_config', 'Global Configuration Mode (config)#'),
        ('interface_config', 'Interface Configuration Mode (config-if)#'),
        ('router_config', 'Router Configuration Mode (config-router)#'),
        ('vlan_config', 'VLAN Configuration Mode (config-vlan)#'),
        ('shell_user', 'Standard Shell ($)'),
        ('shell_root', 'Root Shell (#)'),
        ('mikrotik_root', 'MikroTik Root Menu'),
        ('windows_prompt', r'Windows Command Line (C:\>)'),
    ]

    CATEGORY_CHOICES = [
        ('interface', 'Interface Configuration'),
        ('vlan', 'VLAN & Trunking'),
        ('routing', 'Routing & Static Routes'),
        ('dynamic_routing', 'Dynamic Routing (OSPF/RIP/BGP)'),
        ('firewall', 'Firewall & ACLs'),
        ('nat', 'NAT & Port Forwarding'),
        ('dhcp', 'DHCP Server & Client'),
        ('dns', 'DNS Resolution & Hosts'),
        ('stp', 'Spanning Tree Protocol'),
        ('switching', 'MAC & Switching Operations'),
        ('storage', 'NAS & Storage Networking'),
        ('cctv', 'CCTV & Camera Networking'),
        ('system', 'System Management & Files'),
        ('troubleshooting', 'Troubleshooting & Diagnostics'),
    ]

    name = models.CharField(max_length=128)
    syntax = models.CharField(max_length=256)
    device_category = models.CharField(max_length=64, default='Routers & Switches')
    platform = models.CharField(max_length=32, choices=PLATFORM_CHOICES, default='cisco_ios')
    mode = models.CharField(max_length=32, choices=MODE_CHOICES, default='priv_exec')
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default='interface')
    
    description = models.TextField()
    purpose = models.TextField()
    parameters = models.JSONField(default=list, blank=True, help_text="[{'param': 'ip-address', 'desc': 'IPv4 address'}]")
    example_usage = models.TextField()
    example_output = models.TextField(blank=True, default='')
    prerequisites = models.TextField(blank=True, default='')
    expected_result = models.TextField(blank=True, default='')
    common_errors = models.TextField(blank=True, default='')
    related_commands = models.JSONField(default=list, blank=True, help_text="['show ip route', 'ping']")
    verification_command = models.CharField(max_length=256, blank=True, default='')
    
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['platform', 'category', 'name']
        verbose_name_plural = 'Command Entries'

    def __str__(self):
        return f"[{self.get_platform_display()}] {self.name}"
