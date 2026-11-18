"""
Ramonet Core - Device Registry & Capability Manager
Authoritative definition of device profiles, hardware capabilities, and defaults.
"""
from typing import Dict, List, Any, Optional

class DeviceCapabilities:
    SWITCHING_L2 = 'switching_l2'
    SWITCHING_L3 = 'switching_l3'
    ROUTING = 'routing'
    FIREWALL = 'firewall'
    WIRELESS = 'wireless'
    DHCP_SERVER = 'dhcp_server'
    DNS_SERVER = 'dns_server'
    WEB_SERVER = 'web_server'
    STORAGE_NAS = 'storage_nas'
    CCTV_CAMERA = 'cctv_camera'
    CCTV_NVR = 'cctv_nvr'
    POE_SOURCE = 'poe_source'
    POE_PD = 'poe_pd'
    RACK_MOUNTABLE = 'rack_mountable'
    CLI_MANAGED = 'cli_managed'

class DeviceCapabilityManager:
    """Defines and checks capabilities for all Ramonet device types."""
    
    TYPE_CAPABILITIES: Dict[str, List[str]] = {
        'router': [
            DeviceCapabilities.ROUTING,
            DeviceCapabilities.FIREWALL,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'layer2_switch': [
            DeviceCapabilities.SWITCHING_L2,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'layer3_switch': [
            DeviceCapabilities.SWITCHING_L2,
            DeviceCapabilities.SWITCHING_L3,
            DeviceCapabilities.ROUTING,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'managed_switch': [
            DeviceCapabilities.SWITCHING_L2,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'unmanaged_switch': [
            DeviceCapabilities.SWITCHING_L2
        ],
        'poe_switch': [
            DeviceCapabilities.SWITCHING_L2,
            DeviceCapabilities.POE_SOURCE,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'firewall': [
            DeviceCapabilities.ROUTING,
            DeviceCapabilities.FIREWALL,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'wireless_ap': [
            DeviceCapabilities.WIRELESS,
            DeviceCapabilities.POE_PD,
            DeviceCapabilities.CLI_MANAGED
        ],
        'wireless_controller': [
            DeviceCapabilities.WIRELESS,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'pc_workstation': [
            DeviceCapabilities.CLI_MANAGED
        ],
        'laptop': [
            DeviceCapabilities.WIRELESS,
            DeviceCapabilities.CLI_MANAGED
        ],
        'network_printer': [
            DeviceCapabilities.CLI_MANAGED
        ],
        'nas_storage': [
            DeviceCapabilities.STORAGE_NAS,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'nvr_recorder': [
            DeviceCapabilities.CCTV_NVR,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'ip_camera': [
            DeviceCapabilities.CCTV_CAMERA,
            DeviceCapabilities.POE_PD
        ],
        'windows_server': [
            DeviceCapabilities.DHCP_SERVER,
            DeviceCapabilities.DNS_SERVER,
            DeviceCapabilities.WEB_SERVER,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'linux_server': [
            DeviceCapabilities.DHCP_SERVER,
            DeviceCapabilities.DNS_SERVER,
            DeviceCapabilities.WEB_SERVER,
            DeviceCapabilities.ROUTING,
            DeviceCapabilities.FIREWALL,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'dhcp_server': [
            DeviceCapabilities.DHCP_SERVER,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'dns_server': [
            DeviceCapabilities.DNS_SERVER,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'web_server': [
            DeviceCapabilities.WEB_SERVER,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'file_server': [
            DeviceCapabilities.STORAGE_NAS,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'ups_power': [
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'patch_panel': [
            DeviceCapabilities.RACK_MOUNTABLE
        ],
        'vpn_gateway': [
            DeviceCapabilities.ROUTING,
            DeviceCapabilities.FIREWALL,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ],
        'load_balancer': [
            DeviceCapabilities.ROUTING,
            DeviceCapabilities.RACK_MOUNTABLE,
            DeviceCapabilities.CLI_MANAGED
        ]
    }

    @classmethod
    def supports(cls, device_type: str, capability: str) -> bool:
        caps = cls.TYPE_CAPABILITIES.get(device_type.lower(), [])
        return capability in caps

    @classmethod
    def get_capabilities(cls, device_type: str) -> List[str]:
        return cls.TYPE_CAPABILITIES.get(device_type.lower(), [])


class DeviceSpecCaps:
    def __init__(self, rack_units: int = 1, cli_platform: str = 'cisco_ios', supports_vlans: bool = True, supports_routing: bool = False):
        self.rack_units = rack_units
        self.cli_platform = cli_platform
        self.supports_vlans = supports_vlans
        self.supports_routing = supports_routing

class DeviceRegistry:
    """Authoritative Device Factory and Profile Registry."""

    @classmethod
    def get_default_capabilities(cls, category_or_type: str) -> DeviceSpecCaps:
        cat = (category_or_type or '').lower()
        if 'router' in cat:
            return DeviceSpecCaps(rack_units=2, cli_platform='cisco_ios', supports_vlans=True, supports_routing=True)
        elif 'switch' in cat:
            return DeviceSpecCaps(rack_units=1, cli_platform='cisco_ios', supports_vlans=True, supports_routing=False)
        elif 'firewall' in cat:
            return DeviceSpecCaps(rack_units=1, cli_platform='cisco_ios', supports_vlans=True, supports_routing=True)
        elif 'server' in cat:
            return DeviceSpecCaps(rack_units=2, cli_platform='windows_cmd', supports_vlans=False, supports_routing=False)
        return DeviceSpecCaps(rack_units=0, cli_platform='windows_cmd', supports_vlans=False, supports_routing=False)

    DEVICE_SPECS: Dict[str, Dict[str, Any]] = {
        'router': {
            'category': 'routers',
            'cli_platform': 'cisco_ios',
            'power_watts': 60.0,
            'rack_units': 1,
            'default_interfaces': [
                {'name': 'GigabitEthernet0/0', 'type': 'copper', 'speed': 1000, 'mode': 'routed', 'status': 'down'},
                {'name': 'GigabitEthernet0/1', 'type': 'copper', 'speed': 1000, 'mode': 'routed', 'status': 'down'}
            ]
        },
        'layer2_switch': {
            'category': 'switches',
            'cli_platform': 'cisco_ios',
            'power_watts': 35.0,
            'rack_units': 1,
            'default_interfaces': [
                {'name': f'FastEthernet0/{i}', 'type': 'copper', 'speed': 100, 'mode': 'access', 'vlan': 1, 'status': 'up'} for i in range(1, 25)
            ] + [
                {'name': 'GigabitEthernet0/1', 'type': 'copper', 'speed': 1000, 'mode': 'trunk', 'native_vlan': 1, 'status': 'up'},
                {'name': 'GigabitEthernet0/2', 'type': 'copper', 'speed': 1000, 'mode': 'trunk', 'native_vlan': 1, 'status': 'up'}
            ]
        },
        'layer3_switch': {
            'category': 'switches',
            'cli_platform': 'cisco_ios',
            'power_watts': 85.0,
            'rack_units': 1,
            'default_interfaces': [
                {'name': f'GigabitEthernet1/0/{i}', 'type': 'copper', 'speed': 1000, 'mode': 'access', 'vlan': 1, 'status': 'up'} for i in range(1, 25)
            ]
        },
        'poe_switch': {
            'category': 'switches',
            'cli_platform': 'cisco_ios',
            'power_watts': 65.0,
            'poe_budget_watts': 370.0,
            'rack_units': 1,
            'default_interfaces': [
                {'name': f'FastEthernet0/{i}', 'type': 'copper', 'speed': 100, 'mode': 'access', 'vlan': 1, 'poe': True, 'status': 'up'} for i in range(1, 25)
            ] + [
                {'name': 'GigabitEthernet0/1', 'type': 'copper', 'speed': 1000, 'mode': 'trunk', 'status': 'up'}
            ]
        },
        'firewall': {
            'category': 'firewalls',
            'cli_platform': 'cisco_ios',
            'power_watts': 75.0,
            'rack_units': 1,
            'default_interfaces': [
                {'name': 'ethernet0', 'type': 'copper', 'speed': 1000, 'zone': 'outside', 'status': 'up'},
                {'name': 'ethernet1', 'type': 'copper', 'speed': 1000, 'zone': 'inside', 'status': 'up'},
                {'name': 'ethernet2', 'type': 'copper', 'speed': 1000, 'zone': 'dmz', 'status': 'up'}
            ]
        },
        'pc_workstation': {
            'category': 'computers',
            'cli_platform': 'windows_cmd',
            'power_watts': 150.0,
            'rack_units': 0,
            'default_interfaces': [
                {'name': 'eth0', 'type': 'copper', 'speed': 1000, 'status': 'up'}
            ]
        },
        'laptop': {
            'category': 'computers',
            'cli_platform': 'windows_cmd',
            'power_watts': 65.0,
            'rack_units': 0,
            'default_interfaces': [
                {'name': 'eth0', 'type': 'copper', 'speed': 1000, 'status': 'up'},
                {'name': 'wlan0', 'type': 'wireless', 'speed': 300, 'status': 'up'}
            ]
        },
        'ip_camera': {
            'category': 'cctv',
            'cli_platform': 'web_gui',
            'power_watts': 12.0,
            'poe_pd': True,
            'rack_units': 0,
            'default_interfaces': [
                {'name': 'eth0', 'type': 'copper', 'speed': 100, 'poe_draw_watts': 12.0, 'status': 'up'}
            ]
        },
        'nvr_recorder': {
            'category': 'cctv',
            'cli_platform': 'web_gui',
            'power_watts': 90.0,
            'rack_units': 2,
            'default_interfaces': [
                {'name': 'eth0', 'type': 'copper', 'speed': 1000, 'status': 'up'}
            ]
        },
        'nas_storage': {
            'category': 'storage',
            'cli_platform': 'linux_shell',
            'power_watts': 110.0,
            'rack_units': 2,
            'default_interfaces': [
                {'name': 'eth0', 'type': 'copper', 'speed': 1000, 'status': 'up'},
                {'name': 'eth1', 'type': 'copper', 'speed': 1000, 'status': 'up'}
            ]
        },
        'windows_server': {
            'category': 'servers',
            'cli_platform': 'windows_cmd',
            'power_watts': 250.0,
            'rack_units': 2,
            'default_interfaces': [
                {'name': 'Ethernet0', 'type': 'copper', 'speed': 10000, 'status': 'up'}
            ]
        },
        'linux_server': {
            'category': 'servers',
            'cli_platform': 'linux_shell',
            'power_watts': 220.0,
            'rack_units': 1,
            'default_interfaces': [
                {'name': 'eth0', 'type': 'copper', 'speed': 10000, 'status': 'up'}
            ]
        },
        'ups_power': {
            'category': 'infrastructure',
            'cli_platform': 'web_gui',
            'power_watts': 0.0,
            'rack_units': 2,
            'default_interfaces': [
                {'name': 'management0', 'type': 'copper', 'speed': 100, 'status': 'up'}
            ]
        },
        'patch_panel': {
            'category': 'infrastructure',
            'cli_platform': 'none',
            'power_watts': 0.0,
            'rack_units': 1,
            'default_interfaces': [
                {'name': f'Port{i}', 'type': 'copper', 'speed': 1000, 'status': 'up'} for i in range(1, 25)
            ]
        }
    }

    @classmethod
    def create_default_device(cls, dev_id: str, name: str, device_type: str, x: int = 150, y: int = 150) -> Dict[str, Any]:
        """Creates an authoritative device configuration dictionary."""
        spec = cls.DEVICE_SPECS.get(device_type.lower(), {
            'category': 'general',
            'cli_platform': 'cisco_ios',
            'power_watts': 50.0,
            'rack_units': 1,
            'default_interfaces': [{'name': 'eth0', 'type': 'copper', 'speed': 1000, 'status': 'up'}]
        })

        interfaces = []
        for iface in spec.get('default_interfaces', []):
            iface_copy = dict(iface)
            if 'ip' not in iface_copy:
                iface_copy['ip'] = ''
            if 'mask' not in iface_copy:
                iface_copy['mask'] = '255.255.255.0'
            interfaces.append(iface_copy)

        return {
            'id': str(dev_id),
            'name': name,
            'type': device_type.lower(),
            'category': spec.get('category', 'general'),
            'cli_platform': spec.get('cli_platform', 'cisco_ios'),
            'x': x,
            'y': y,
            'ip': '',
            'mask': '255.255.255.0',
            'gateway': '',
            'power_watts': spec.get('power_watts', 50.0),
            'poe_budget_watts': spec.get('poe_budget_watts', 0.0),
            'rack_units': spec.get('rack_units', 1),
            'interfaces': interfaces,
            'vlans': [1],
            'port_vlans': {},
            'routing': {
                'enabled': DeviceCapabilityManager.supports(device_type, DeviceCapabilities.ROUTING),
                'static_routes': [],
                'ospf': {'enabled': False, 'router_id': '', 'networks': []}
            },
            'firewall': {
                'enabled': DeviceCapabilityManager.supports(device_type, DeviceCapabilities.FIREWALL),
                'default_policy': 'allow' if device_type != 'firewall' else 'deny',
                'rules': []
            },
            'services': {
                'dhcp_server': {'enabled': False, 'pools': []},
                'dns_server': {'enabled': False, 'records': []},
                'cctv': {'resolution': '1080p', 'fps': 30, 'codec': 'H.265', 'bitrate_kbps': 4096},
                'storage': {'raid_level': 'RAID 5', 'capacity_tb': 16, 'shares': []}
            },
            'stp': {
                'enabled': DeviceCapabilityManager.supports(device_type, DeviceCapabilities.SWITCHING_L2),
                'priority': 32768,
                'mode': 'pvst'
            },
            'rack_placement': {
                'rack_id': None,
                'unit_start': None,
                'height_u': spec.get('rack_units', 1)
            }
        }
