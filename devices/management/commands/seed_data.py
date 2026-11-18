import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from devices.models import DeviceCategory, DeviceDefinition
from commands.models import CommandEntry
from knowledgebase.models import KnowledgeArticle, ConnectionRule
from learning.models import LearningTopic
from troubleshooting.models import TroubleshootingScenario
from projects.models import NetworkProject

class Command(BaseCommand):
    help = 'Populates the Ramonet database with comprehensive networking data, devices, commands, guides, and templates.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Ramonet database seeding...'))

        # 1. User Account Notice (No default admin/student seeded - users manage their own accounts)
        self.stdout.write(self.style.NOTICE('User accounts: No default credentials created. Create an administrator via: python manage.py createsuperuser or sign up via the web UI.'))

        # 2. Seed Device Categories
        categories_data = [
            {'name': 'Network Switches', 'slug': 'switches', 'icon': 'fa-network-wired', 'display_order': 1, 'description': 'Layer 2/3 Managed, Unmanaged, Core, Distribution, Access and PoE switches.'},
            {'name': 'Routers', 'slug': 'routers', 'icon': 'fa-route', 'display_order': 2, 'description': 'Basic, Enterprise, Branch, Edge, and Wireless Routers with static/dynamic routing.'},
            {'name': 'Firewalls', 'slug': 'firewalls', 'icon': 'fa-shield-halved', 'display_order': 3, 'description': 'Stateful packet filter, Next-Generation, Linux iptables, and UTM firewalls.'},
            {'name': 'Wireless Devices', 'slug': 'wireless', 'icon': 'fa-wifi', 'display_order': 4, 'description': 'Indoor/Outdoor Access Points, Mesh nodes, Wireless Controllers, and Clients.'},
            {'name': 'Computers & Endpoints', 'slug': 'computers', 'icon': 'fa-desktop', 'display_order': 5, 'description': 'Desktop PCs, Laptops, Workstations, Thin Clients, and IP Phones.'},
            {'name': 'Printers', 'slug': 'printers', 'icon': 'fa-print', 'display_order': 6, 'description': 'Network Laser, Inkjet, Multifunction, and Enterprise Print Servers.'},
            {'name': 'NAS & Network Storage', 'slug': 'storage', 'icon': 'fa-hard-drive', 'display_order': 7, 'description': 'Network Attached Storage, SAN arrays, RAID 0/1/5/6/10 storage servers.'},
            {'name': 'NVR & CCTV Devices', 'slug': 'cctv', 'icon': 'fa-video', 'display_order': 8, 'description': 'Network Video Recorders, IP PoE Cameras, Dome/Bullet/PTZ cameras.'},
            {'name': 'Servers', 'slug': 'servers', 'icon': 'fa-server', 'display_order': 9, 'description': 'Windows, Linux, DNS, DHCP, Web (HTTP), FTP, and Authentication servers.'},
            {'name': 'Infrastructure & Cables', 'slug': 'infrastructure', 'icon': 'fa-plug', 'display_order': 10, 'description': 'Modems, ONTs, Fiber Media Converters, UPS, Patch Panels, and SFP modules.'},
        ]

        cat_objs = {}
        for c in categories_data:
            obj, _ = DeviceCategory.objects.get_or_create(slug=c['slug'], defaults=c)
            cat_objs[c['slug']] = obj
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(cat_objs)} Device Categories.'))

        # 3. Seed Device Definitions
        devices_data = [
            # Switches
            {
                'category': cat_objs['switches'],
                'name': 'Cisco Catalyst 2960-X 24-Port',
                'manufacturer': 'Cisco Systems',
                'model_name': 'WS-C2960X-24TS-L',
                'device_type': 'layer2_switch',
                'description': 'Enterprise-class Layer 2 access switch with 24x 10/100/1000 ports and 4x 1G SFP uplinks. Supports 802.1Q VLANs, Port Security, and Rapid Spanning Tree Protocol (RSTP).',
                'icon': 'fa-network-wired',
                'is_layer3': False,
                'cli_platform': 'cisco_ios',
                'power_watts': 35.0,
                'poe_budget_watts': 0.0,
                'available_interfaces': [
                    {'name': f'FastEthernet0/{i}', 'type': 'copper', 'speed': 100, 'poe': False} for i in range(1, 9)
                ] + [
                    {'name': f'GigabitEthernet0/{i}', 'type': 'copper', 'speed': 1000, 'poe': False} for i in range(1, 3)
                ],
                'supported_protocols': ['Ethernet', '802.1Q VLAN', 'STP', 'RSTP', 'Port Security', 'DHCP Snooping', 'CDP', 'LLDP'],
                'supported_connection_types': ['copper_straight', 'copper_crossover', 'fiber', 'console'],
                'default_config': {'hostname': 'Switch2960', 'vlans': {'1': {'name': 'default'}}},
                'overview_text': 'The Catalyst 2960-X provides wire-speed Layer 2 forwarding for campus and branch networks with rich QoS and security features.',
                'troubleshooting_notes': 'Verify interface status with "show ip interface brief" and VLAN memberships with "show vlan brief".',
                'security_notes': 'Always configure "switchport port-security" on end-user access ports and disable unused interfaces.',
            },
            {
                'category': cat_objs['switches'],
                'name': 'Cisco Catalyst 3850 Layer 3 Switch',
                'manufacturer': 'Cisco Systems',
                'model_name': 'WS-C3850-24T-S',
                'device_type': 'layer3_switch',
                'description': 'Stackable enterprise Layer 3 switch supporting Inter-VLAN routing, OSPF, EIGRP, and Static routes directly in hardware.',
                'icon': 'fa-network-wired',
                'is_layer3': True,
                'cli_platform': 'cisco_ios',
                'power_watts': 65.0,
                'poe_budget_watts': 435.0,
                'available_interfaces': [
                    {'name': f'GigabitEthernet1/0/{i}', 'type': 'copper', 'speed': 1000, 'poe': True} for i in range(1, 9)
                ] + [
                    {'name': 'TenGigabitEthernet1/1/1', 'type': 'fiber', 'speed': 10000, 'poe': False},
                    {'name': 'TenGigabitEthernet1/1/2', 'type': 'fiber', 'speed': 10000, 'poe': False}
                ],
                'supported_protocols': ['IPv4', 'IPv6', 'Inter-VLAN Routing', 'OSPFv2', 'EIGRP', '802.1Q', 'LACP EtherChannel'],
                'supported_connection_types': ['copper_straight', 'copper_crossover', 'fiber', 'console'],
                'default_config': {'hostname': 'CoreSwitch3850', 'ip_routing': True},
                'overview_text': 'Core distribution switch capable of routing packets between different subnets without offloading to an external router.',
                'troubleshooting_notes': 'Verify "ip routing" is enabled. Check Switch Virtual Interfaces (SVIs) with "show ip interface brief".',
                'security_notes': 'Use Routed Access ports on uplinks and apply Access Control Lists (ACLs) to SVIs.',
            },
            {
                'category': cat_objs['switches'],
                'name': '8-Port PoE+ Surveillance Switch',
                'manufacturer': 'TP-Link / Generic',
                'model_name': 'TL-SG1008MP',
                'device_type': 'poe_switch',
                'description': '8-port Gigabit Desktop switch with 8x PoE+ ports delivering up to 126W total budget, optimized for IP Cameras and Access Points.',
                'icon': 'fa-bolt',
                'is_layer3': False,
                'cli_platform': 'web_gui',
                'power_watts': 15.0,
                'poe_budget_watts': 126.0,
                'available_interfaces': [
                    {'name': f'Port{i}', 'type': 'copper', 'speed': 1000, 'poe': True} for i in range(1, 9)
                ],
                'supported_protocols': ['Ethernet', '802.3af PoE (15.4W)', '802.3at PoE+ (30W)', 'QoS (802.1p)'],
                'supported_connection_types': ['copper_straight'],
                'default_config': {'poe_mode': 'auto'},
                'overview_text': 'Delivers DC power and Ethernet data over Cat5e/6 cables directly to security cameras, eliminating separate power bricks.',
                'troubleshooting_notes': 'If camera fails to power on, verify that total device wattage does not exceed the 126W switch power budget.',
                'security_notes': 'Isolate camera ports on a dedicated Surveillance VLAN to prevent direct LAN sniffing.',
            },

            # Routers
            {
                'category': cat_objs['routers'],
                'name': 'Cisco ISR 4331 Enterprise Router',
                'manufacturer': 'Cisco Systems',
                'model_name': 'ISR4331/K9',
                'device_type': 'enterprise_router',
                'description': 'Modular Gigabit WAN Router delivering 100 Mbps to 300 Mbps aggregate throughput with integrated NAT, Zone-Based Firewall, and VPN.',
                'icon': 'fa-route',
                'is_layer3': True,
                'cli_platform': 'cisco_ios',
                'power_watts': 42.0,
                'available_interfaces': [
                    {'name': 'GigabitEthernet0/0/0', 'type': 'copper', 'speed': 1000, 'poe': False},
                    {'name': 'GigabitEthernet0/0/1', 'type': 'copper', 'speed': 1000, 'poe': False},
                    {'name': 'GigabitEthernet0/0/2', 'type': 'fiber', 'speed': 1000, 'poe': False},
                ],
                'supported_protocols': ['IPv4', 'IPv6', 'Static Routing', 'OSPF', 'BGP', 'RIP', 'NAT/PAT', 'ACL', 'DHCP Server'],
                'supported_connection_types': ['copper_straight', 'copper_crossover', 'fiber', 'serial', 'console'],
                'default_config': {'hostname': 'EdgeRouter', 'routes': []},
                'overview_text': 'The standard edge router for connecting enterprise branch sites to WAN services and the public Internet.',
                'troubleshooting_notes': 'Use "show ip route" to check next hops and "show ip nat translations" for NAT troubleshooting.',
                'security_notes': 'Implement strict inbound Access-Lists on WAN-facing interfaces and disable Telnet/HTTP services.',
            },
            {
                'category': cat_objs['routers'],
                'name': 'MikroTik Cloud Router hEX',
                'manufacturer': 'MikroTik',
                'model_name': 'RB750Gr3',
                'device_type': 'branch_router',
                'description': 'Compact 5-port Gigabit Ethernet router for locations where wireless is not required, running RouterOS with robust Queues and VPN.',
                'icon': 'fa-route',
                'is_layer3': True,
                'cli_platform': 'mikrotik',
                'power_watts': 5.0,
                'available_interfaces': [
                    {'name': f'ether{i}', 'type': 'copper', 'speed': 1000, 'poe': False} for i in range(1, 6)
                ],
                'supported_protocols': ['IPv4', 'IPv6', 'BGP', 'OSPF', 'MPLS', 'IPsec', 'FastPath', 'PPPoE'],
                'supported_connection_types': ['copper_straight', 'console'],
                'default_config': {'hostname': 'MikroTik', 'default_ip': '192.168.88.1'},
                'overview_text': 'High-performance value router popular in small business deployments and WISP customer premises.',
                'troubleshooting_notes': 'Inspect interface counters with "/interface print" and verify default route in "/ip route print".',
                'security_notes': 'Disable default admin password and shut down winbox/api services on WAN interfaces.',
            },

            # Firewalls
            {
                'category': cat_objs['firewalls'],
                'name': 'Enterprise Next-Gen Perimeter Firewall',
                'manufacturer': 'Fortinet / pfSense Inspired',
                'model_name': 'NetGate-NGFW-5100',
                'device_type': 'firewall',
                'description': 'High-throughput stateful packet inspection firewall featuring LAN, WAN, and DMZ zone separation, NAT/PAT, and IDS/IPS event tracking.',
                'icon': 'fa-shield-halved',
                'is_layer3': True,
                'cli_platform': 'linux_shell',
                'power_watts': 35.0,
                'available_interfaces': [
                    {'name': 'igb0_WAN', 'type': 'copper', 'speed': 1000, 'poe': False},
                    {'name': 'igb1_LAN', 'type': 'copper', 'speed': 1000, 'poe': False},
                    {'name': 'igb2_DMZ', 'type': 'copper', 'speed': 1000, 'poe': False},
                    {'name': 'igb3_MGMT', 'type': 'copper', 'speed': 1000, 'poe': False},
                ],
                'supported_protocols': ['Stateful Inspection', 'IPv4', 'NAT/Port Forwarding', 'DMZ Routing', 'IPsec', 'OpenVPN', 'TCP/UDP Filter'],
                'supported_connection_types': ['copper_straight', 'fiber', 'console'],
                'default_config': {
                    'default_policy': 'deny',
                    'firewall_rules': [
                        {'id': 1, 'src_ip': '192.168.1.0/24', 'dest_ip': 'any', 'protocol': 'any', 'port': 'any', 'action': 'allow', 'enabled': True},
                        {'id': 2, 'src_ip': 'any', 'dest_ip': 'any', 'protocol': 'any', 'port': 'any', 'action': 'deny', 'enabled': True}
                    ]
                },
                'overview_text': 'Filters all inbound and outbound traffic according to security rules, maintaining a connection tracking table.',
                'troubleshooting_notes': 'Check connection tracking logs and verify rule order: more specific rules must precede broad catch-all rules.',
                'security_notes': 'Enforce explicit default-deny on WAN and place publicly reachable services strictly into the DMZ zone.',
            },

            # Wireless Devices
            {
                'category': cat_objs['wireless'],
                'name': 'Enterprise Dual-Band Wi-Fi 6 Access Point',
                'manufacturer': 'Ubiquiti / Cisco Catalyst',
                'model_name': 'UniFi U6-Pro',
                'device_type': 'access_point',
                'description': 'Ceiling-mount Wi-Fi 6 AP with 4x4 MIMO on 5 GHz and 2x2 MIMO on 2.4 GHz, powered via 802.3at PoE+, supporting multiple SSIDs and VLAN tagging.',
                'icon': 'fa-wifi',
                'is_layer3': False,
                'cli_platform': 'web_gui',
                'power_watts': 13.0,
                'available_interfaces': [
                    {'name': 'Ethernet0', 'type': 'copper', 'speed': 1000, 'poe': True},
                    {'name': 'WLAN0_2.4G', 'type': 'wireless', 'speed': 573, 'poe': False},
                    {'name': 'WLAN1_5G', 'type': 'wireless', 'speed': 4800, 'poe': False},
                ],
                'supported_protocols': ['802.11ax (Wi-Fi 6)', '802.11ac', 'WPA2/WPA3-Enterprise', 'VLAN Tagging (802.1Q)', '802.3at PoE+'],
                'supported_connection_types': ['copper_straight', 'wireless'],
                'default_config': {'ssid': 'Corporate-WiFi', 'security': 'WPA3-Personal', 'vlan_id': 10},
                'overview_text': 'Provides wireless network access for laptops, smartphones, and IoT devices, mapping different SSIDs to isolated VLANs.',
                'troubleshooting_notes': 'Verify switch port is configured as a Trunk or Access with matching VLAN, and check PoE power supply.',
                'security_notes': 'Always use WPA3 or WPA2-AES encryption and avoid WEP or open guest networks without captive portal isolation.',
            },

            # Endpoints & Computers
            {
                'category': cat_objs['computers'],
                'name': 'Standard Workstation PC',
                'manufacturer': 'Dell OptiPlex',
                'model_name': 'OptiPlex 7090 MT',
                'device_type': 'desktop_pc',
                'description': 'Enterprise desktop PC running Windows/Linux with Gigabit Ethernet, static or DHCP IPv4 addressing, ping, traceroute, and ARP tools.',
                'icon': 'fa-desktop',
                'is_layer3': False,
                'cli_platform': 'windows_cmd',
                'power_watts': 85.0,
                'available_interfaces': [
                    {'name': 'eth0', 'type': 'copper', 'speed': 1000, 'poe': False}
                ],
                'supported_protocols': ['IPv4', 'DHCP Client', 'DNS Client', 'ICMP (Ping)', 'TCP/UDP', 'ARP', 'SMB Client'],
                'supported_connection_types': ['copper_straight'],
                'default_config': {'ip': '192.168.1.50', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'dns': '8.8.8.8'},
                'overview_text': 'General client computer generating simulated traffic (Web, Ping, File access) across the network topology.',
                'troubleshooting_notes': 'Use "ipconfig /all" to verify IP/Mask/Gateway and "ping <gateway>" to check first-hop reachability.',
                'security_notes': 'Ensure host firewall is active and keep antivirus definitions current.',
            },

            # Printers
            {
                'category': cat_objs['printers'],
                'name': 'Enterprise Network Laser Multifunction Printer',
                'manufacturer': 'HP LaserJet Enterprise',
                'model_name': 'LaserJet M635 MFP',
                'device_type': 'network_printer',
                'description': 'Departmental network printer supporting IPP (port 631), RAW port 9100 printing, LPR/LPD, and SNMP monitoring.',
                'icon': 'fa-print',
                'is_layer3': False,
                'cli_platform': 'web_gui',
                'power_watts': 70.0,
                'available_interfaces': [
                    {'name': 'eth0', 'type': 'copper', 'speed': 1000, 'poe': False}
                ],
                'supported_protocols': ['IPv4', 'IPP (Port 631)', 'RAW 9100', 'LPR/LPD (515)', 'SNMP v2c/v3', 'HTTPS'],
                'supported_connection_types': ['copper_straight'],
                'default_config': {'ip': '192.168.1.200', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                'overview_text': 'Shared network printing appliance receiving print jobs from multiple workstations over TCP port 9100 or IPP.',
                'troubleshooting_notes': 'Verify printer has a static IP address or DHCP reservation and port 9100 is not blocked by firewalls.',
                'security_notes': 'Change factory default admin credentials and disable legacy protocols (AppleTalk, IPX, Telnet).',
            },

            # NAS & Storage
            {
                'category': cat_objs['storage'],
                'name': '4-Bay Enterprise NAS Server',
                'manufacturer': 'Synology / QNAP',
                'model_name': 'DiskStation DS923+',
                'device_type': 'nas',
                'description': 'Network Attached Storage with 4x SATA bays, Dual 1GbE ports with Link Aggregation (LACP) support, RAID 0/1/5/6/10, and SMB/NFS file sharing.',
                'icon': 'fa-hard-drive',
                'is_layer3': False,
                'cli_platform': 'linux_shell',
                'power_watts': 35.0,
                'storage_capacity_gb': 16000,
                'available_interfaces': [
                    {'name': 'eth0', 'type': 'copper', 'speed': 1000, 'poe': False},
                    {'name': 'eth1', 'type': 'copper', 'speed': 1000, 'poe': False},
                ],
                'supported_protocols': ['SMB/CIFS (Port 445)', 'NFS (2049)', 'iSCSI', 'FTP/SFTP', 'LACP (802.3ad)', 'RAID 5'],
                'supported_connection_types': ['copper_straight'],
                'default_config': {'raid_type': 'RAID5', 'shared_folders': ['SharedData', 'Backups']},
                'overview_text': 'Central storage appliance for backups, file sharing, and video surveillance archives across the LAN.',
                'troubleshooting_notes': 'Check RAID health status and confirm both LACP member ports are assigned to the same port channel on the switch.',
                'security_notes': 'Enforce SMB3 encryption and disable guest access to confidential file shares.',
            },

            # NVR & CCTV
            {
                'category': cat_objs['cctv'],
                'name': '16-Channel 4K NVR (Network Video Recorder)',
                'manufacturer': 'Hikvision / Dahua',
                'model_name': 'DS-7716NI-I4',
                'device_type': 'nvr',
                'description': '16-Channel 4K NVR with dual Gigabit NICs (LAN isolation mode), ONVIF Profile S/G/T compliance, RTSP stream ingestion, and 4x SATA HDD bays.',
                'icon': 'fa-video',
                'is_layer3': False,
                'cli_platform': 'web_gui',
                'power_watts': 40.0,
                'storage_capacity_gb': 32000,
                'bandwidth_mbps': 160.0,
                'available_interfaces': [
                    {'name': 'LAN1_Surveillance', 'type': 'copper', 'speed': 1000, 'poe': False},
                    {'name': 'LAN2_Management', 'type': 'copper', 'speed': 1000, 'poe': False},
                ],
                'supported_protocols': ['ONVIF', 'RTSP (Port 554)', 'HTTP/HTTPS', 'TCP/UDP', 'H.264/H.265 Decoding'],
                'supported_connection_types': ['copper_straight'],
                'default_config': {'channels': 16, 'codec': 'H.265', 'bitrate_kbps': 4096},
                'overview_text': 'Central video management device that connects to IP cameras, ingests real-time RTSP streams, and records video to local drives.',
                'troubleshooting_notes': 'Ensure camera IP addresses are reachable and ONVIF discovery (UDP 3702) or RTSP (TCP 554) ports are open.',
                'security_notes': 'Never expose NVR management ports directly to the Internet; require a secure VPN connection for remote viewing.',
            },
            {
                'category': cat_objs['cctv'],
                'name': '4K PoE Outdoor Dome IP Camera',
                'manufacturer': 'Axis / Hikvision',
                'model_name': 'AXIS P3248-LV',
                'device_type': 'ip_camera',
                'description': '8 Megapixel (4K) outdoor vandal-resistant dome camera with 802.3af PoE power, ONVIF Profile S/T, RTSP stream (554), and IR illumination.',
                'icon': 'fa-camera',
                'is_layer3': False,
                'cli_platform': 'web_gui',
                'power_watts': 9.5,
                'bandwidth_mbps': 8.0,
                'available_interfaces': [
                    {'name': 'eth0_PoE', 'type': 'copper', 'speed': 100, 'poe': True}
                ],
                'supported_protocols': ['IPv4', '802.3af PoE (Class 3)', 'ONVIF', 'RTSP (Port 554)', 'RTCP', 'HTTPS'],
                'supported_connection_types': ['copper_straight'],
                'default_config': {'resolution': '3840x2160', 'fps': 25, 'bitrate': 6144, 'rtsp_port': 554},
                'overview_text': 'Captures video and streams encoded H.265/H.264 packets across the Ethernet cable to NVRs and monitoring stations.',
                'troubleshooting_notes': 'Verify that switch delivers 802.3af power. Test RTSP connectivity using ping and port 554 reachability.',
                'security_notes': 'Change default camera passwords immediately; isolate all cameras on an isolated non-routing Surveillance VLAN.',
            },

            # Servers
            {
                'category': cat_objs['servers'],
                'name': 'Enterprise Linux Web & Application Server',
                'manufacturer': 'Ubuntu / Red Hat',
                'model_name': 'Ubuntu 24.04 LTS Server',
                'device_type': 'server',
                'description': 'Multi-purpose production Linux server hosting Nginx web services, DNS, DHCP, and database engines with full bash terminal.',
                'icon': 'fa-server',
                'is_layer3': False,
                'cli_platform': 'linux_shell',
                'power_watts': 120.0,
                'available_interfaces': [
                    {'name': 'eth0', 'type': 'copper', 'speed': 1000, 'poe': False},
                    {'name': 'eth1', 'type': 'copper', 'speed': 1000, 'poe': False},
                ],
                'supported_protocols': ['HTTP (80)', 'HTTPS (443)', 'DNS (53)', 'DHCP (67/68)', 'SSH (22)', 'TCP/UDP', 'IPv4/IPv6'],
                'supported_connection_types': ['copper_straight', 'fiber'],
                'default_config': {'ip': '192.168.1.100', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'services': ['nginx', 'bind9']},
                'overview_text': 'Core server responding to client web requests (HTTP/HTTPS) and resolving domain names across the local network.',
                'troubleshooting_notes': 'Verify service daemon status using "systemctl status" and check open listening ports with "ss -tulpn".',
                'security_notes': 'Disable root SSH password logins, mandate SSH key pairs, and configure UFW firewall rules.',
            },
        ]

        for dev in devices_data:
            obj, _ = DeviceDefinition.objects.get_or_create(
                name=dev['name'],
                category=dev['category'],
                defaults=dev
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(devices_data)} Device Definitions.'))

        # 4. Seed Command Reference Library
        commands_seed = [
            {
                'name': 'show ip interface brief',
                'syntax': 'show ip interface brief',
                'device_category': 'Routers & Switches',
                'platform': 'cisco_ios',
                'mode': 'priv_exec',
                'category': 'interface',
                'description': 'Displays a compact table of all interfaces on the router or switch, showing IP addresses, physical layer status, and data link protocol state.',
                'purpose': 'Rapidly verify which ports are physically connected (Status Up) and functionally operational (Protocol Up), and view their assigned IP addresses.',
                'parameters': [{'param': 'brief', 'desc': 'Displays summary table without verbose per-interface counters'}],
                'example_usage': 'Router# show ip interface brief',
                'example_output': 'Interface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0     192.168.1.1     YES manual up                    up      \nGigabitEthernet0/1     unassigned      YES manual administratively down down',
                'prerequisites': 'Device powered on in User or Privileged EXEC mode.',
                'expected_result': 'Table listing all physical interfaces and SVIs.',
                'common_errors': 'If Status is "up" but Protocol is "down", check encapsulation, clock rate (on serial), or duplex mismatch.',
                'related_commands': ['show interfaces', 'show ip route', 'ping'],
                'verification_command': 'show ip interface brief'
            },
            {
                'name': 'ip route',
                'syntax': 'ip route <network> <mask> <next-hop | interface>',
                'device_category': 'Routers',
                'platform': 'cisco_ios',
                'mode': 'global_config',
                'category': 'routing',
                'description': 'Installs a static IPv4 route into the router routing table directing traffic for a destination subnet towards a specific next-hop gateway.',
                'purpose': 'Manually define reachability to remote subnets without running dynamic routing protocols.',
                'parameters': [
                    {'param': 'network', 'desc': 'Destination network address (e.g. 10.0.0.0 or 0.0.0.0 for default route)'},
                    {'param': 'mask', 'desc': 'Subnet mask (e.g. 255.255.255.0 or 0.0.0.0)'},
                    {'param': 'next-hop', 'desc': 'IP address of the next-hop router'}
                ],
                'example_usage': 'Router(config)# ip route 10.0.0.0 255.255.255.0 192.168.1.2\nRouter(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1',
                'example_output': '',
                'prerequisites': 'Global configuration mode. Next-hop IP must be on a directly connected subnet.',
                'expected_result': 'Static route added to the routing table marked with code "S".',
                'common_errors': 'Specifying an unreachable next-hop IP will prevent the route from being installed into the active routing table.',
                'related_commands': ['show ip route', 'ip routing', 'no ip route'],
                'verification_command': 'show ip route static'
            },
            {
                'name': 'switchport mode trunk',
                'syntax': 'switchport mode trunk',
                'device_category': 'Network Switches',
                'platform': 'cisco_ios',
                'mode': 'interface_config',
                'category': 'vlan',
                'description': 'Configures a switch port as an 802.1Q trunk link capable of carrying multiple tagged VLANs between switches or to a router-on-a-stick.',
                'purpose': 'Interconnect switches and routers so that traffic belonging to multiple isolated VLANs can travel across a single physical cable.',
                'parameters': [{'param': 'trunk', 'desc': 'Sets permanent trunking mode'}],
                'example_usage': 'Switch(config)# interface GigabitEthernet0/1\nSwitch(config-if)# switchport mode trunk',
                'example_output': '%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up',
                'prerequisites': 'Interface configuration mode on a managed switch.',
                'expected_result': 'Interface encapsulates outgoing Ethernet frames with 802.1Q 4-byte tags containing the VLAN ID.',
                'common_errors': 'Native VLAN mismatch between two trunk endpoints causes STP loops and unrouted traffic leaks.',
                'related_commands': ['switchport trunk allowed vlan', 'switchport trunk native vlan', 'show interfaces trunk'],
                'verification_command': 'show interfaces trunk'
            },
            {
                'name': 'show ip route',
                'syntax': 'show ip route [protocol]',
                'device_category': 'Routers',
                'platform': 'cisco_ios',
                'mode': 'priv_exec',
                'category': 'routing',
                'description': 'Displays the active IPv4 routing table containing directly connected networks, static routes, and dynamic routes learned via OSPF/EIGRP/BGP.',
                'purpose': 'Determine forwarding decisions for incoming packets by reviewing destination subnets, administrative distances, metrics, and exit interfaces.',
                'parameters': [{'param': 'ospf / static / connected', 'desc': 'Filters the table by specific route source'}],
                'example_usage': 'Router# show ip route',
                'example_output': 'Codes: C - connected, S - static, R - RIP, O - OSPF\n\nGateway of last resort is 203.0.113.1 to network 0.0.0.0\n\nC    192.168.1.0/24 is directly connected, GigabitEthernet0/0\nS*   0.0.0.0/0 [1/0] via 203.0.113.1',
                'prerequisites': 'Privileged EXEC mode on Layer 3 device.',
                'expected_result': 'Complete forwarding table with prefix lengths and next hops.',
                'common_errors': 'Missing route causes "Destination host unreachable" or packet drop.',
                'related_commands': ['show ip route summary', 'traceroute', 'ping'],
                'verification_command': 'show ip route'
            },
            {
                'name': 'ip addr add (Linux)',
                'syntax': 'ip addr add <ip>/<cidr> dev <interface>',
                'device_category': 'Servers & Linux Endpoints',
                'platform': 'linux_shell',
                'mode': 'shell_root',
                'category': 'interface',
                'description': 'Assigns an IPv4 or IPv6 address and subnet mask prefix to a specified Linux network interface using the modern iproute2 suite.',
                'purpose': 'Configure network addressing on Linux servers, workstations, and firewalls without deprecated ifconfig tools.',
                'parameters': [
                    {'param': 'ip/cidr', 'desc': 'IP address with CIDR bitmask (e.g. 192.168.1.100/24)'},
                    {'param': 'dev', 'desc': 'Network device name (e.g. eth0, ens33)'}
                ],
                'example_usage': '# ip addr add 192.168.1.100/24 dev eth0\n# ip link set eth0 up',
                'example_output': '',
                'prerequisites': 'Root or sudo privileges in Linux shell.',
                'expected_result': 'Address bound to interface; kernel automatically creates a connected route in the main routing table.',
                'common_errors': 'Omitting /cidr defaults to a host /32 address which prevents local subnet communication.',
                'related_commands': ['ip addr show', 'ip route add', 'ip link set'],
                'verification_command': 'ip addr show dev eth0'
            },
            {
                'name': 'ipconfig /all (Windows)',
                'syntax': 'ipconfig [/all]',
                'device_category': 'Computers & Endpoints',
                'platform': 'windows_cmd',
                'mode': 'windows_prompt',
                'category': 'interface',
                'description': 'Displays comprehensive TCP/IP network configuration for all network adapters on Windows, including IP, Subnet Mask, Gateway, DNS, and DHCP lease times.',
                'purpose': 'First-line troubleshooting command on Windows client computers to verify network connectivity settings.',
                'parameters': [{'param': '/all', 'desc': 'Displays full detailed configuration including MAC address and DHCP server'}],
                'example_usage': 'C:\\> ipconfig /all',
                'example_output': 'Ethernet adapter Ethernet0:\n   Physical Address. . . . . . . . . : 00-15-5D-01-A2-43\n   DHCP Enabled. . . . . . . . . . . : Yes\n   IPv4 Address. . . . . . . . . . . : 192.168.1.50\n   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n   Default Gateway . . . . . . . . . : 192.168.1.1\n   DNS Servers . . . . . . . . . . . : 8.8.8.8',
                'prerequisites': 'Windows command prompt or PowerShell.',
                'expected_result': 'Adapter settings displayed.',
                'common_errors': 'An address starting with 169.254.x.x indicates APIPA (DHCP server unreachable).',
                'related_commands': ['ping', 'tracert', 'nslookup', 'route print'],
                'verification_command': 'ipconfig'
            },
            {
                'name': 'iptables stateful rule',
                'syntax': 'iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT',
                'device_category': 'Firewalls',
                'platform': 'iptables',
                'mode': 'shell_root',
                'category': 'firewall',
                'description': 'Configures the Linux Netfilter firewall to permit incoming reply packets for outbound connections already initiated by local clients.',
                'purpose': 'Core foundation of stateful firewalling: allow replies while blocking unsolicited inbound connection attempts.',
                'parameters': [
                    {'param': '-A INPUT', 'desc': 'Appends rule to the inbound packet chain'},
                    {'param': '--ctstate', 'desc': 'Matches conntrack state: ESTABLISHED or RELATED'},
                    {'param': '-j ACCEPT', 'desc': 'Target action: accept packet'}
                ],
                'example_usage': '# iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT\n# iptables -A INPUT -p tcp --dport 22 -j ACCEPT\n# iptables -P INPUT DROP',
                'example_output': '',
                'prerequisites': 'Linux kernel netfilter / conntrack modules loaded with root privileges.',
                'expected_result': 'Return packets bypass further inspection and are delivered to sockets.',
                'common_errors': 'Setting default DROP policy before adding this rule will instantly sever active SSH management sessions.',
                'related_commands': ['iptables -L -v -n', 'conntrack -L'],
                'verification_command': 'iptables -L -n -v'
            }
        ]

        for cmd_entry in commands_seed:
            CommandEntry.objects.get_or_create(
                name=cmd_entry['name'],
                platform=cmd_entry['platform'],
                defaults=cmd_entry
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(commands_seed)} Command Reference entries.'))

        # 5. Seed Connection Rules ("How to Connect")
        connection_rules_seed = [
            {
                'source_category': 'Computers & Endpoints',
                'target_category': 'Network Switches',
                'is_supported': True,
                'recommended_cable': 'Copper Straight-Through (Cat6 RJ45)',
                'alternative_cables': ['Cat5e Straight-Through'],
                'required_ports': '10/100/1000 Mbps RJ45 Ethernet Port',
                'interface_compatibility': 'Auto-MDIX standard allows straight-through or crossover cables, but Straight-Through is recommended.',
                'ip_requirements': 'Both device and switch SVI (if managed) or Gateway must reside within the same IPv4 subnet mask.',
                'vlan_requirements': 'Switch port must be set to Access Mode in the destination user VLAN (e.g. "switchport access vlan 10").',
                'gateway_requirements': 'PC must configure Default Gateway pointing to the local Router or L3 Switch interface IP.',
                'power_requirements': 'Endpoints use standard AC mains; PoE is not required unless connecting an IP Phone.',
                'step_by_step_instructions': [
                    'Locate the RJ45 NIC port on the back of the PC/Workstation.',
                    'Connect one end of a Cat6 straight-through patch cable to the PC.',
                    'Connect the opposite end to an available FastEthernet or GigabitEthernet access port on the switch.',
                    'Verify the physical link LED illuminates green (1000M) or amber (100M).',
                    'Configure IP, Netmask, Gateway, and DNS on the PC network adapter.',
                    'Configure the switch port: "switchport mode access" and "switchport access vlan <ID>".',
                    'Execute ping from the PC to its default gateway to verify connectivity.'
                ],
                'verification_commands': ['ipconfig /all (PC)', 'show ip interface brief (Switch)', 'ping <gateway>'],
                'troubleshooting_tips': [
                    'If link LED is off, check cable seating and ensure switch port is not administratively shut down.',
                    'If ping fails, verify PC IP and Gateway belong to the same subnet mask.'
                ]
            },
            {
                'source_category': 'NVR & CCTV Devices',
                'target_category': 'Network Switches',
                'is_supported': True,
                'recommended_cable': 'Cat6 Shielded Copper (STP/FTP for outdoor cameras)',
                'alternative_cables': ['Cat6 UTP', 'Cat5e'],
                'required_ports': 'PoE+ 802.3at / 802.3af RJ45 Port on PoE Switch; Gigabit Uplink for NVR.',
                'interface_compatibility': 'IP Camera requires Power over Ethernet (PoE). Must connect to a PoE-enabled switch port or PoE injector.',
                'ip_requirements': 'Assign static IPs to both Camera and NVR within a dedicated Surveillance Subnet (e.g. 192.168.10.0/24).',
                'vlan_requirements': 'Recommended to isolate all cameras and NVR in a separate Surveillance VLAN (e.g. VLAN 30) with no direct Internet routing.',
                'gateway_requirements': 'Point Default Gateway to Router only if remote WAN viewing is authorized via VPN.',
                'power_requirements': 'Verify switch PoE power budget (typical dome camera draws 7-12W; PTZ camera draws 25-30W PoE+).',
                'step_by_step_instructions': [
                    'Verify total PoE wattage budget on switch before connecting new cameras.',
                    'Plug IP Camera RJ45 cable into PoE Switch port (Port 1-8).',
                    'Observe switch port PoE indicator LED turning on, confirming 48V power negotiation.',
                    'Plug NVR LAN1/Uplink port into a Gigabit switch port.',
                    'Log into NVR web interface, navigate to Camera Management, and click Search (ONVIF discovery).',
                    'Add camera channel with matching ONVIF/RTSP credentials and verify live video stream preview.'
                ],
                'verification_commands': ['show power inline (PoE Switch)', 'ping <camera_ip>', 'nmap -p 554,80 <camera_ip>'],
                'troubleshooting_tips': [
                    'If camera does not power on, calculate total PoE load. The switch may be exceeding its wattage limit.',
                    'If camera is powered but NVR shows "Offline", check that ONVIF credentials match and subnet masks align.'
                ]
            },
            {
                'source_category': 'Network Switches',
                'target_category': 'Routers',
                'is_supported': True,
                'recommended_cable': 'Copper Straight-Through or Fiber (SFP)',
                'alternative_cables': ['Copper Crossover (older hardware)'],
                'required_ports': 'GigabitEthernet 1000BASE-T or SFP optical port',
                'interface_compatibility': 'Supports standard Access link for single subnet, or 802.1Q Trunk link for Router-on-a-Stick inter-VLAN routing.',
                'ip_requirements': 'Router interface IP serves as the Default Gateway for the connected switch subnet.',
                'vlan_requirements': 'For Router-on-a-Stick: Switch port must be "switchport mode trunk". Router creates sub-interfaces (e.g. Gi0/0.10) with 802.1Q encapsulation.',
                'gateway_requirements': 'Switch management SVI must set "ip default-gateway" to router interface IP.',
                'power_requirements': 'Both devices require independent AC/DC power supplies.',
                'step_by_step_instructions': [
                    'Connect Cat6 cable between Switch uplink port (e.g. Gi0/1) and Router interface (e.g. Gi0/0).',
                    'On Switch: "interface Gi0/1" -> "switchport mode trunk".',
                    'On Router: "interface Gi0/0" -> "no shutdown".',
                    'Create sub-interface on router: "interface Gi0/0.10" -> "encapsulation dot1Q 10" -> "ip address 192.168.10.1 255.255.255.0".',
                    'Verify reachability with ping from router to switch management IP.'
                ],
                'verification_commands': ['show interfaces trunk (Switch)', 'show ip interface brief (Router)', 'show ip route (Router)'],
                'troubleshooting_tips': [
                    'Ensure "no shutdown" is executed on the parent router interface.',
                    'Verify VLAN IDs in router sub-interface match the VLAN database on the switch.'
                ]
            },
            {
                'source_category': 'NAS & Network Storage',
                'target_category': 'Network Switches',
                'is_supported': True,
                'recommended_cable': 'Dual Cat6 Patch Cables (for LACP bonding) or 10G SFP+ DAC Twinax',
                'alternative_cables': ['LC-LC Multimode Fiber'],
                'required_ports': '2x Gigabit RJ45 or 10G SFP+ ports',
                'interface_compatibility': 'Supports 802.3ad Link Aggregation Control Protocol (LACP) for redundancy and aggregated bandwidth.',
                'ip_requirements': 'Static IP recommended or static DHCP reservation. Jumbo Frames (MTU 9000) optional for SAN/iSCSI.',
                'vlan_requirements': 'Storage VLAN (e.g. VLAN 40) recommended to isolate backup and heavy file transfer traffic.',
                'gateway_requirements': 'Default gateway required if accessed from remote branch offices.',
                'power_requirements': 'Dedicated UPS protection strongly recommended to prevent filesystem corruption during power loss.',
                'step_by_step_instructions': [
                    'Connect both Ethernet cables between NAS LAN1/LAN2 and Switch ports Gi0/11-12.',
                    'On Switch: group ports into an EtherChannel: "channel-group 1 mode active".',
                    'On NAS: create Bond adapter with IEEE 802.3ad dynamic link aggregation.',
                    'Configure static IP on the Bonded interface.',
                    'Create SMB/NFS file shares and configure user permissions.'
                ],
                'verification_commands': ['show etherchannel summary (Switch)', 'ping <nas_ip>', 'smbclient -L <nas_ip>'],
                'troubleshooting_tips': [
                    'If MTU 9000 (Jumbo Frames) is enabled on the NAS, MTU 9000 must also be configured on every switch port along the path.'
                ]
            }
        ]

        for rule in connection_rules_seed:
            ConnectionRule.objects.get_or_create(
                source_category=rule['source_category'],
                target_category=rule['target_category'],
                defaults=rule
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(connection_rules_seed)} Connection Rules.'))

        # 6. Seed Learning Center (20 Structured Topics)
        learning_topics_seed = [
            {
                'topic_number': 1,
                'title': 'Networking Fundamentals & Topologies',
                'slug': 'networking-fundamentals',
                'level': 'beginner',
                'category': 'Fundamentals',
                'simple_explanation': 'A computer network is like a highway system where digital data packets travel between homes (PCs, phones) and warehouses (servers) using intersections (switches) and highway exits (routers).',
                'technical_explanation': 'Computer networks enable distributed nodes to exchange data using packet-switching communication protocols governed by standards organizations such as IEEE, IETF, and ISO.',
                'practical_example': 'Connecting your home laptop, smart TV, and phone to a wireless router so they can all share a single broadband Internet connection.',
                'relevant_devices': ['Desktop PC', 'Standard Workstation PC', 'Cisco Catalyst 2960-X 24-Port', 'Cisco ISR 4331 Enterprise Router'],
                'relevant_commands': ['ping', 'traceroute', 'ipconfig'],
                'common_mistakes': 'Confusing the function of a switch (local segment forwarding) with a router (inter-network forwarding).',
                'practice_exercise': 'Build a simple network with 2 PCs connected to a single unmanaged switch and configure static IPs to achieve successful ping.'
            },
            {
                'topic_number': 2,
                'title': 'The OSI 7-Layer Reference Model',
                'slug': 'osi-7-layer-model',
                'level': 'beginner',
                'category': 'Architecture',
                'simple_explanation': 'Think of sending an international postal package: Layer 7 is the letter content, Layer 4 is the courier tracking number, Layer 3 is the country address, Layer 2 is the local street mail truck, and Layer 1 is the physical road.',
                'technical_explanation': 'The Open Systems Interconnection (OSI) reference model partitions network communication into 7 distinct abstraction layers: 7-Application, 6-Presentation, 5-Session, 4-Transport, 3-Network, 2-Data Link, 1-Physical. Each layer encapsulates the payload from the layer above.',
                'practical_example': 'When browsing https://example.com, HTTP operates at Layer 7, TLS at Layer 6, TCP port 443 at Layer 4, IPv4 destination at Layer 3, MAC address headers at Layer 2, and electrical pulses on Cat6 copper at Layer 1.',
                'relevant_devices': ['Cisco Catalyst 2960-X 24-Port', 'Cisco ISR 4331 Enterprise Router', 'Enterprise Next-Gen Perimeter Firewall'],
                'relevant_commands': ['show ip route', 'show mac address-table', 'wireshark'],
                'common_mistakes': 'Assuming real-world TCP/IP matches the 7 layers 1-to-1; TCP/IP combines OSI Layers 5, 6, and 7 into a single Application layer.',
                'practice_exercise': 'Trace a packet from PC1 to a Web Server in the Ramonet Packet Flow Visualizer and identify which layer header changes at each hop.'
            },
            {
                'topic_number': 3,
                'title': 'TCP/IP Protocol Suite & Architecture',
                'slug': 'tcp-ip-suite',
                'level': 'beginner',
                'category': 'Architecture',
                'simple_explanation': 'TCP is the certified mail carrier that makes sure every single page arrives without missing pages. UDP is like live radio broadcasting: it streams fast without checking if someone missed a second.',
                'technical_explanation': 'The TCP/IP protocol suite operates on 4 layers: Application (HTTP, DNS, SSH), Transport (TCP, UDP), Internet (IP, ICMP, ARP), and Network Access. TCP provides reliable, connection-oriented, ordered byte-stream delivery with congestion control.',
                'practical_example': 'Web browsing and file transfers use TCP because a single dropped byte corrupts an executable file. Live video calls and CCTV RTSP streams use UDP for low-latency real-time playback.',
                'relevant_devices': ['Enterprise Linux Web & Application Server', 'Standard Workstation PC'],
                'relevant_commands': ['netstat -tulpn', 'ss -s', 'ping -c 4'],
                'common_mistakes': 'Expecting UDP to automatically retransmit dropped packets without application-level recovery logic.',
                'practice_exercise': 'Send both an ICMP ping and a simulated TCP HTTP GET request to test connection establishment differences.'
            },
            {
                'topic_number': 4,
                'title': 'Ethernet Framing & MAC Addressing',
                'slug': 'ethernet-mac-addressing',
                'level': 'beginner',
                'category': 'Data Link',
                'simple_explanation': 'Every network card in the world has a permanent fingerprint called a MAC address (like 00:1A:2B:3C:4D:5E). Switches use this address to deliver frames to the right physical cable port.',
                'technical_explanation': 'IEEE 802.3 Ethernet frames encapsulate IP packets with a 14-byte Layer 2 header: 6-byte Destination MAC, 6-byte Source MAC, and 2-byte EtherType (0x0800 for IPv4, 0x8100 for 802.1Q VLAN). An FCS trailer provides 32-bit CRC error detection.',
                'practical_example': 'When PC1 transmits data to PC2 on the same switch, the destination IP is PC2, and the destination MAC in the Ethernet frame is PC2\'s network interface card MAC.',
                'relevant_devices': ['Cisco Catalyst 2960-X 24-Port', 'Standard Workstation PC'],
                'relevant_commands': ['show mac address-table', 'arp -a', 'ip link show'],
                'common_mistakes': 'Thinking MAC addresses route across the global Internet; MAC addresses change at every router hop!',
                'practice_exercise': 'Inspect the Switch MAC table after pinging between two PCs to verify dynamic MAC address learning.'
            },
            {
                'topic_number': 5,
                'title': 'IPv4 Addressing & Classless Subnetting',
                'slug': 'ipv4-addressing-subnetting',
                'level': 'beginner',
                'category': 'Network Layer',
                'simple_explanation': 'An IP address is like a postal address with a street name (Network portion) and house number (Host portion). The Subnet Mask tells the computer where the street name ends and the house number begins.',
                'technical_explanation': 'An IPv4 address consists of 32 binary bits divided into four 8-bit octets. Classless Inter-Domain Routing (CIDR) uses a prefix length (e.g. /24) to define the boundary between network and host bits.',
                'practical_example': '192.168.1.10/24 means the first 24 bits (192.168.1) identify the local subnet, allowing up to 254 usable host addresses (192.168.1.1 to 192.168.1.254).',
                'relevant_devices': ['Cisco ISR 4331 Enterprise Router', 'Standard Workstation PC'],
                'relevant_commands': ['ip route', 'ip addr add', 'ipconfig'],
                'common_mistakes': 'Assigning the Network Address (all host bits 0) or Broadcast Address (all host bits 1) directly to a device interface.',
                'practice_exercise': 'Use the Ramonet Subnet Calculator to determine usable IP ranges and broadcast addresses for a /27 subnet.'
            },
            {
                'topic_number': 6,
                'title': 'Variable Length Subnet Masking (VLSM)',
                'slug': 'vlsm-subnet-planning',
                'level': 'intermediate',
                'category': 'Network Layer',
                'simple_explanation': 'Instead of cutting a cake into equal-sized slices for people with different appetites, VLSM lets you cut big slices for departments with 100 computers and tiny slices for point-to-point router links.',
                'technical_explanation': 'VLSM allocates subnets of varying prefix sizes (/24, /26, /30) from a larger parent address block to optimize IP address utilization and minimize wasted host addresses.',
                'practical_example': 'Allocating a /30 subnet (providing exactly 2 usable IPs) for a dedicated router-to-router serial or fiber link.',
                'relevant_devices': ['Cisco ISR 4331 Enterprise Router', 'Cisco Catalyst 3850 Layer 3 Switch'],
                'relevant_commands': ['ip route', 'show ip route'],
                'common_mistakes': 'Creating overlapping subnets by failing to calculate binary block boundaries correctly.',
                'practice_exercise': 'Design an enterprise IP plan for 3 departments (50 hosts, 20 hosts, 5 hosts) using a single 192.168.10.0/24 network block.'
            },
            {
                'topic_number': 7,
                'title': 'Switching Operations & MAC Learning',
                'slug': 'switching-mac-learning',
                'level': 'beginner',
                'category': 'Switching',
                'simple_explanation': 'When a switch first turns on, it knows nothing. When a PC sends a message, the switch remembers which port that PC is plugged into. Over time, it builds a memory map so messages are only forwarded to the intended recipient.',
                'technical_explanation': 'Switches perform three fundamental operations: Learning (recording Source MAC and ingress port), Forwarding/Filtering (looking up Destination MAC in the CAM table), and Flooding (broadcasting unknown unicast, broadcast, and multicast frames out all other ports).',
                'practical_example': 'Unlike an old hub that retransmitted every packet to every connected device, a switch forwards packets exclusively to the target port, preventing collisions.',
                'relevant_devices': ['Cisco Catalyst 2960-X 24-Port'],
                'relevant_commands': ['show mac address-table', 'clear mac address-table dynamic'],
                'common_mistakes': 'Believing switches inspect IP packet headers; standard Layer 2 switches only look at Layer 2 Ethernet frame headers.',
                'practice_exercise': 'Simulate an Unknown Unicast frame and observe the switch flood the frame across all active ports in the VLAN.'
            },
            {
                'topic_number': 8,
                'title': 'Virtual LANs (VLANs) & 802.1Q Trunking',
                'slug': 'vlans-and-trunking',
                'level': 'intermediate',
                'category': 'Switching',
                'simple_explanation': 'A VLAN splits a single physical switch into multiple virtual switches. Devices in VLAN 10 (Sales) cannot talk to devices in VLAN 20 (Accounting) unless a router allows it.',
                'technical_explanation': 'IEEE 802.1Q inserts a 4-byte tag (including a 12-bit VLAN ID supporting up to 4094 VLANs) into the Ethernet frame header on Trunk links. Access ports strip this tag when delivering frames to endpoint devices.',
                'practical_example': 'Segregating guest Wi-Fi users (VLAN 100) from internal company servers (VLAN 10) on the same physical cabling infrastructure.',
                'relevant_devices': ['Cisco Catalyst 2960-X 24-Port', 'Cisco Catalyst 3850 Layer 3 Switch'],
                'relevant_commands': ['vlan 10', 'switchport mode access', 'switchport access vlan 10', 'switchport mode trunk', 'show vlan brief'],
                'common_mistakes': 'Forgetting to allow the desired VLAN on intermediate trunk ports connecting switches.',
                'practice_exercise': 'Configure two PCs on Switch1 in different VLANs and confirm that ping fails without an inter-VLAN router.'
            },
            {
                'topic_number': 9,
                'title': 'Inter-VLAN Routing & Layer 3 Switching',
                'slug': 'inter-vlan-routing',
                'level': 'intermediate',
                'category': 'Routing',
                'simple_explanation': 'Because VLANs are completely separate islands, you need a ferry boat (a Router or Layer 3 Switch) to carry packets between one VLAN island and another.',
                'technical_explanation': 'Inter-VLAN routing can be accomplished via "Router-on-a-Stick" (sub-interfaces with 802.1Q trunking on an external router) or Switched Virtual Interfaces (SVIs) on a Layer 3 switch with wire-speed ASIC packet forwarding.',
                'practical_example': 'Configuring "interface Vlan10" with IP 192.168.10.1 and "interface Vlan20" with IP 192.168.20.1 on a Catalyst 3850 switch.',
                'relevant_devices': ['Cisco Catalyst 3850 Layer 3 Switch', 'Cisco ISR 4331 Enterprise Router'],
                'relevant_commands': ['ip routing', 'interface Vlan10', 'encapsulation dot1Q', 'show ip route'],
                'common_mistakes': 'Forgetting to enable "ip routing" globally on Cisco Layer 3 switches.',
                'practice_exercise': 'Build a Router-on-a-Stick topology and configure sub-interfaces to route traffic between VLAN 10 and VLAN 20.'
            },
            {
                'topic_number': 10,
                'title': 'Dynamic Routing Protocols (OSPF, RIP, BGP)',
                'slug': 'routing-protocols',
                'level': 'advanced',
                'category': 'Routing',
                'simple_explanation': 'Static routes are like memorized driving directions that break if a bridge collapses. Dynamic routing protocols like OSPF are like GPS navigation that automatically detects traffic jams and reroutes cars around broken links.',
                'technical_explanation': 'OSPF (Open Shortest Path First) is a link-state routing protocol using Dijkstra\'s Shortest Path First algorithm, operating within autonomous systems. BGP (Border Gateway Protocol) is a path-vector protocol that routes traffic across the global Internet between Autonomous Systems.',
                'practical_example': 'Enterprise networks run OSPF across internal routers and use BGP to connect to two redundant Internet Service Providers (ISPs).',
                'relevant_devices': ['Cisco ISR 4331 Enterprise Router', 'MikroTik Cloud Router hEX'],
                'relevant_commands': ['router ospf 1', 'network 192.168.1.0 0.0.0.255 area 0', 'show ip ospf neighbor', 'show ip route ospf'],
                'common_mistakes': 'Wildcard mask inverted octet mistakes or mismatched OSPF area IDs between neighboring routers.',
                'practice_exercise': 'Configure OSPF Area 0 across two routers and verify that routes are dynamically exchanged.'
            },
            {
                'topic_number': 11,
                'title': 'Stateful Firewalls & Access Control Lists',
                'slug': 'firewalls-and-acls',
                'level': 'intermediate',
                'category': 'Security',
                'simple_explanation': 'A stateless ACL is like a security guard with a checklist of allowed names. A stateful firewall is like a receptionist who remembers you went out to get lunch and lets you back inside without questioning you.',
                'technical_explanation': 'Stateful inspection maintains a connection table tracking active TCP/UDP/ICMP sessions. Packets belonging to an ESTABLISHED session are automatically permitted without re-evaluating the complete rule base.',
                'practical_example': 'Permitting internal workstations to browse external HTTPS websites while blocking all unsolicited inbound connections from the Internet.',
                'relevant_devices': ['Enterprise Next-Gen Perimeter Firewall'],
                'relevant_commands': ['iptables -A INPUT -m conntrack --ctstate ESTABLISHED -j ACCEPT', 'access-list 101 permit tcp any any eq 80'],
                'common_mistakes': 'Placing an allow rule after a broad deny rule (rules are evaluated top-down on first match).',
                'practice_exercise': 'Add a firewall rule blocking destination port 80 and observe HTTP traffic get dropped while ICMP ping succeeds.'
            },
            {
                'topic_number': 12,
                'title': 'Network Address Translation (NAT & PAT)',
                'slug': 'nat-and-pat',
                'level': 'intermediate',
                'category': 'Network Layer',
                'simple_explanation': 'NAT is like an apartment building where 100 residents share a single street mailbox. The mailroom appends an apartment number (port number) so replies get to the right person.',
                'technical_explanation': 'Port Address Translation (PAT or NAT Overload) maps multiple private IPv4 addresses (RFC 1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) to a single public IP address by assigning unique Layer 4 source ports.',
                'practical_example': 'Home broadband routers translate internal IPs like 192.168.1.50 into a single ISP-assigned public IP address.',
                'relevant_devices': ['Cisco ISR 4331 Enterprise Router', 'Enterprise Next-Gen Perimeter Firewall'],
                'relevant_commands': ['ip nat inside source list 1 interface Gi0/0 overload', 'show ip nat translations'],
                'common_mistakes': 'Forgetting to designate "ip nat inside" and "ip nat outside" on the respective router interfaces.',
                'practice_exercise': 'Observe inside local IP translation into inside global public IP in the Packet Flow Visualizer.'
            },
            {
                'topic_number': 13,
                'title': 'Domain Name System (DNS) Architecture',
                'slug': 'dns-architecture',
                'level': 'beginner',
                'category': 'Application Layer',
                'simple_explanation': 'DNS is the phonebook of the Internet. Humans remember names like google.com; computers only understand numbers like 142.250.190.46.',
                'technical_explanation': 'DNS operates hierarchically over UDP/TCP port 53. Resolvers query Root servers, Top-Level Domain (TLD) servers, and Authoritative Name Servers to resolve A records (IPv4), AAAA records (IPv6), and CNAME aliases.',
                'practical_example': 'When a user enters a server hostname in their browser, the workstation sends a DNS query to 8.8.8.8 before any HTTP connection can begin.',
                'relevant_devices': ['Enterprise Linux Web & Application Server', 'Standard Workstation PC'],
                'relevant_commands': ['nslookup', 'dig', 'cat /etc/resolv.conf'],
                'common_mistakes': 'Assuming network connection is down when only the DNS server address is misconfigured.',
                'practice_exercise': 'Test pinging an IP address directly versus pinging by domain name when DNS is disabled.'
            },
            {
                'topic_number': 14,
                'title': 'Dynamic Host Configuration Protocol (DHCP)',
                'slug': 'dhcp-protocol',
                'level': 'beginner',
                'category': 'Application Layer',
                'simple_explanation': 'Instead of manually typing an IP address into every new phone and laptop, a DHCP server automatically leases an IP, netmask, and gateway the moment the device connects.',
                'technical_explanation': 'DHCP uses the 4-step DORA process: Discover (broadcast by client), Offer (unicast/broadcast by server), Request (broadcast by client confirming selection), and Acknowledge (server locks lease). Operates over UDP ports 67 (server) and 68 (client).',
                'practical_example': 'Configuring an IP pool on a Cisco router: "ip dhcp pool LAN-USERS" with network 192.168.1.0/24 and default-router 192.168.1.1.',
                'relevant_devices': ['Cisco ISR 4331 Enterprise Router', 'Enterprise Linux Web & Application Server'],
                'relevant_commands': ['ip dhcp pool', 'show ip dhcp binding', 'ipconfig /renew'],
                'common_mistakes': 'Failing to configure an "ip helper-address" on a router interface when the DHCP server is on a different subnet.',
                'practice_exercise': 'Switch a PC from static IP to DHCP and observe the DORA broadcast exchange allocate an IP.'
            },
            {
                'topic_number': 15,
                'title': 'Wireless LANs & Wi-Fi Security (WPA2/WPA3)',
                'slug': 'wireless-networking',
                'level': 'intermediate',
                'category': 'Wireless',
                'simple_explanation': 'Wi-Fi replaces Ethernet cables with radio frequencies (2.4 GHz, 5 GHz, 6 GHz). WPA3 uses strong cryptographic handshakes so eavesdroppers cannot decode data passing through the air.',
                'technical_explanation': 'IEEE 802.11 uses CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance) because radio channels are half-duplex shared mediums. WPA3 replaces PSK with Simultaneous Authentication of Equals (SAE) to eliminate dictionary attacks.',
                'practical_example': 'Deploying multiple ceiling access points broadcasting a common SSID with 802.11r fast roaming for warehouse barcode scanners.',
                'relevant_devices': ['Enterprise Dual-Band Wi-Fi 6 Access Point'],
                'relevant_commands': ['iwconfig', 'netsh wlan show interfaces'],
                'common_mistakes': 'Using overlapping 2.4 GHz channels instead of the standard non-overlapping channels 1, 6, and 11.',
                'practice_exercise': 'Map two SSIDs (Staff and Guest) to VLAN 10 and VLAN 50 on an enterprise Access Point.'
            },
            {
                'topic_number': 16,
                'title': 'Enterprise Network Security Best Practices',
                'slug': 'network-security',
                'level': 'advanced',
                'category': 'Security',
                'simple_explanation': 'Defense in Depth means having multiple layers of defense: locked doors (physical security), firewall guards at the gate, badge checkpoints at every hallway (VLANs), and encrypted phone calls (TLS/IPsec).',
                'technical_explanation': 'Security architectures implement Zero Trust Network Access (ZTNA), Network Access Control (802.1X), Port Security (MAC limiting), DHCP Snooping, Dynamic ARP Inspection (DAI), and encrypted management planes (SSH, HTTPS, SNMPv3).',
                'practical_example': 'Configuring Cisco Port Security: "switchport port-security maximum 1" with violation shutdown to prevent unauthorized hubs from being plugged in.',
                'relevant_devices': ['Cisco Catalyst 2960-X 24-Port', 'Enterprise Next-Gen Perimeter Firewall'],
                'relevant_commands': ['switchport port-security', 'ip dhcp snooping', 'ip arp inspection vlan 10'],
                'common_mistakes': 'Leaving default vendor credentials on production switches, cameras, and firewalls.',
                'practice_exercise': 'Enable port security on a switch port and simulate an unauthorized MAC address violation.'
            },
            {
                'topic_number': 17,
                'title': 'NAS, SAN & Storage Networking (RAID, SMB, iSCSI)',
                'slug': 'storage-networking',
                'level': 'intermediate',
                'category': 'Storage',
                'simple_explanation': 'A NAS is a hard drive connected to the network that everyone can open files from. RAID combines multiple hard drives so if one drive dies, no data is lost.',
                'technical_explanation': 'Network storage utilizes file-level protocols (SMB/CIFS on port 445, NFS on port 2049) or block-level protocols (iSCSI on port 3260, Fibre Channel). RAID 5 uses distributed parity across at least 3 disks to survive a single drive failure.',
                'practical_example': 'Connecting an accounting department to a shared Synology NAS with RAID 5 and automated offsite backups over rsync.',
                'relevant_devices': ['4-Bay Enterprise NAS Server'],
                'relevant_commands': ['mount -t nfs', 'smbclient -L', 'show etherchannel summary'],
                'common_mistakes': 'Assuming RAID is a replacement for backups; RAID protects against hardware failure, not accidental deletion or ransomware.',
                'practice_exercise': 'Use the Ramonet RAID Calculator to compare usable capacity and fault tolerance between RAID 1, RAID 5, and RAID 10.'
            },
            {
                'topic_number': 18,
                'title': 'CCTV, NVR & Surveillance Network Architecture',
                'slug': 'cctv-nvr-networking',
                'level': 'intermediate',
                'category': 'Surveillance',
                'simple_explanation': 'Security cameras stream high-definition video 24/7. Because video uses lots of bandwidth and electricity, we power cameras with PoE switches and isolate them so hackers cannot tamper with recordings.',
                'technical_explanation': 'Surveillance topologies use ONVIF protocols for device discovery (UDP 3702) and RTSP (TCP/UDP 554) for H.264/H.265 video transport. PoE switches supply 802.3af (15.4W) or 802.3at (30W) DC power over Cat6 cable pairs.',
                'practical_example': 'Deploying 16x 4K IP cameras (8 Mbps each = 128 Mbps total continuous throughput) into an 8-port PoE switch connected to an NVR on an isolated VLAN.',
                'relevant_devices': ['16-Channel 4K NVR (Network Video Recorder)', '4K PoE Outdoor Dome IP Camera', '8-Port PoE+ Surveillance Switch'],
                'relevant_commands': ['show power inline', 'ping <camera_ip>', 'nmap -p 554 <camera_ip>'],
                'common_mistakes': 'Exceeding the total PoE power budget of the switch or letting camera traffic saturate user workstations.',
                'practice_exercise': 'Use the CCTV Bandwidth Calculator to calculate storage retention requirements for sixteen 4K cameras recording for 30 days.'
            },
            {
                'topic_number': 19,
                'title': 'Server Infrastructure & DMZ Deployment',
                'slug': 'server-dmz-networking',
                'level': 'intermediate',
                'category': 'Servers',
                'simple_explanation': 'A DMZ (Demilitarized Zone) is like the security buffer lobby in a bank. Public visitors can enter the lobby to visit the customer service counter, but they cannot walk into the private money vaults in the back office.',
                'technical_explanation': 'A DMZ subnet hosts externally accessible services (Web, Mail, DNS) isolated between two firewalls or on a distinct firewall interface. Compromising a DMZ server does not grant direct access to the internal trusted LAN.',
                'practical_example': 'Placing an Nginx web server on 172.16.1.100 (DMZ). The firewall permits inbound port 443 from WAN to DMZ, but denies all DMZ-to-LAN initiated traffic.',
                'relevant_devices': ['Enterprise Linux Web & Application Server', 'Enterprise Next-Gen Perimeter Firewall'],
                'relevant_commands': ['systemctl status nginx', 'iptables -L FORWARD -v', 'netstat -tulpn'],
                'common_mistakes': 'Allowing DMZ servers unrestricted access to internal database servers instead of restricting access to specific database ports.',
                'practice_exercise': 'Build a 3-legged firewall topology (WAN, LAN, DMZ) and verify that LAN can reach DMZ, but DMZ cannot initiate connections to LAN.'
            },
            {
                'topic_number': 20,
                'title': 'Structured Troubleshooting Methodology',
                'slug': 'network-troubleshooting',
                'level': 'advanced',
                'category': 'Troubleshooting',
                'simple_explanation': 'When a network breaks, don\'t guess randomly! Work methodically from Layer 1 (is the cable plugged in?) to Layer 3 (can I ping the gateway?) to Layer 7 (is the web server running?).',
                'technical_explanation': 'Systematic troubleshooting approaches: Top-Down (Layer 7 down to 1), Bottom-Up (Layer 1 up to 7), and Divide-and-Conquer (start at Layer 3 with ping). If pinging the local gateway succeeds, Layers 1 and 2 are functioning.',
                'practical_example': 'A user says "the Internet is broken". You ping 127.0.0.1 (TCP/IP stack OK), ping 192.168.1.1 (LAN OK), ping 8.8.8.8 (WAN OK), ping google.com (fails) -> Root cause is DNS resolution!',
                'relevant_devices': ['Standard Workstation PC', 'Cisco ISR 4331 Enterprise Router'],
                'relevant_commands': ['ping', 'traceroute', 'ipconfig', 'show ip route', 'arp -a'],
                'common_mistakes': 'Reconfiguring router configurations before checking whether the physical Ethernet cable is disconnected.',
                'practice_exercise': 'Open the Ramonet Troubleshooting Lab and resolve the "Default Gateway Mismatch" scenario using Divide-and-Conquer.'
            }
        ]

        for topic in learning_topics_seed:
            LearningTopic.objects.get_or_create(
                topic_number=topic['topic_number'],
                defaults=topic
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(learning_topics_seed)} Learning Center Topics.'))

        # 7. Seed Troubleshooting Scenarios (15 Scenarios)
        troubleshooting_scenarios_seed = [
            # Beginner
            {
                'code': 'SCN-01',
                'title': 'PC Unable to Reach Local Gateway (Wrong Subnet Mask)',
                'difficulty': 'beginner',
                'category': 'IP Addressing',
                'symptoms': 'PC1 cannot ping its default gateway 192.168.1.1. User reports no internet connectivity.',
                'description': 'A new workstation PC1 was deployed on the accounting floor. The technician configured the IP address manually. When the user attempts to browse the intranet or ping the router gateway 192.168.1.1, all packets fail.',
                'initial_topology': {
                    'devices': [
                        {'id': 'pc1', 'name': 'PC1', 'category': 'computers', 'ip': '192.168.1.15', 'subnet_mask': '255.255.255.240', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
                        {'id': 'sw1', 'name': 'Switch1', 'category': 'switches', 'interfaces': [{'name': 'Fa0/1', 'status': 'up'}, {'name': 'Fa0/2', 'status': 'up'}]},
                        {'id': 'r1', 'name': 'Router1', 'category': 'routers', 'ip': '192.168.1.1', 'subnet_mask': '255.255.255.0', 'interfaces': [{'name': 'Gi0/0', 'ip': '192.168.1.1', 'mask': '255.255.255.0', 'status': 'up'}]}
                    ],
                    'connections': [
                        {'source_device': 'pc1', 'source_port': 'eth0', 'target_device': 'sw1', 'target_port': 'Fa0/1', 'status': 'connected'},
                        {'source_device': 'sw1', 'source_port': 'Fa0/2', 'target_device': 'r1', 'target_port': 'Gi0/0', 'status': 'connected'}
                    ]
                },
                'fault_device_id': 'pc1',
                'fault_type': 'wrong_subnet_mask',
                'fault_summary': 'PC1 was configured with subnet mask 255.255.255.240 (/28). In this mask, 192.168.1.15 is the broadcast address of the 192.168.1.0/28 subnet, or the router at 192.168.1.1 belongs to an overlapping block.',
                'suggested_commands': ['ipconfig /all', 'ping 192.168.1.1', 'show ip interface brief'],
                'hints': [
                    'Examine the subnet mask on PC1 compared to the router interface mask.',
                    'Standard LANs use 255.255.255.0 (/24).'
                ],
                'verification_rule': {
                    'target_device': 'pc1',
                    'required_field': 'subnet_mask',
                    'expected_value': '255.255.255.0',
                    'test_ping_dest': '192.168.1.1'
                },
                'root_cause_explanation': 'The subnet mask on PC1 was configured as 255.255.255.240 (/28). Because 192.168.1.15 is the broadcast address for the 192.168.1.0/28 block, the network stack rejects traffic.',
                'recommended_solution': 'Change PC1 subnet mask to 255.255.255.0 to match the router interface GigabitEthernet0/0.'
            },
            {
                'code': 'SCN-02',
                'title': 'Interface Administratively Disabled on Gateway Router',
                'difficulty': 'beginner',
                'category': 'Interface Status',
                'symptoms': 'Link LED on Router GigabitEthernet0/0 is amber/off. No LAN clients can reach the gateway.',
                'description': 'Following a weekend maintenance window, LAN workstations report that the default gateway 192.168.1.1 is unresponsive.',
                'initial_topology': {
                    'devices': [
                        {'id': 'pc1', 'name': 'PC1', 'category': 'computers', 'ip': '192.168.1.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
                        {'id': 'sw1', 'name': 'Switch1', 'category': 'switches', 'interfaces': [{'name': 'Fa0/1', 'status': 'up'}, {'name': 'Fa0/2', 'status': 'up'}]},
                        {'id': 'r1', 'name': 'Router1', 'category': 'routers', 'ip': '192.168.1.1', 'subnet_mask': '255.255.255.0', 'interfaces': [{'name': 'Gi0/0', 'ip': '192.168.1.1', 'mask': '255.255.255.0', 'status': 'administratively_down'}]}
                    ],
                    'connections': [
                        {'source_device': 'pc1', 'source_port': 'eth0', 'target_device': 'sw1', 'target_port': 'Fa0/1', 'status': 'connected'},
                        {'source_device': 'sw1', 'source_port': 'Fa0/2', 'target_device': 'r1', 'target_port': 'Gi0/0', 'status': 'connected'}
                    ]
                },
                'fault_device_id': 'r1',
                'fault_type': 'interface_shutdown',
                'fault_summary': 'Router interface GigabitEthernet0/0 was left in "shutdown" state.',
                'suggested_commands': ['show ip interface brief', 'configure terminal', 'interface GigabitEthernet0/0', 'no shutdown'],
                'hints': [
                    'Open the Router CLI terminal and run "show ip interface brief".',
                    'Look for an interface marked "administratively down".'
                ],
                'verification_rule': {
                    'target_device': 'r1',
                    'interface_name': 'Gi0/0',
                    'required_status': 'up'
                },
                'root_cause_explanation': 'Cisco router interfaces default to administratively down upon creation or after an admin executes "shutdown".',
                'recommended_solution': 'Enter interface configuration mode on Router1 and execute "no shutdown".'
            },
            {
                'code': 'SCN-03',
                'title': 'Incorrect Default Gateway Configured on Workstation',
                'difficulty': 'beginner',
                'category': 'IP Addressing',
                'symptoms': 'PC can ping local switch but cannot reach remote web servers or external addresses.',
                'description': 'Workstation PC2 has its gateway set to 192.168.1.254, but the true default gateway router IP is 192.168.1.1.',
                'initial_topology': {
                    'devices': [
                        {'id': 'pc2', 'name': 'PC2', 'category': 'computers', 'ip': '192.168.1.25', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.254', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
                        {'id': 'sw1', 'name': 'Switch1', 'category': 'switches', 'interfaces': [{'name': 'Fa0/1', 'status': 'up'}, {'name': 'Fa0/2', 'status': 'up'}]},
                        {'id': 'r1', 'name': 'Router1', 'category': 'routers', 'ip': '192.168.1.1', 'subnet_mask': '255.255.255.0', 'interfaces': [{'name': 'Gi0/0', 'ip': '192.168.1.1', 'mask': '255.255.255.0', 'status': 'up'}]}
                    ],
                    'connections': [
                        {'source_device': 'pc2', 'source_port': 'eth0', 'target_device': 'sw1', 'target_port': 'Fa0/1', 'status': 'connected'},
                        {'source_device': 'sw1', 'source_port': 'Fa0/2', 'target_device': 'r1', 'target_port': 'Gi0/0', 'status': 'connected'}
                    ]
                },
                'fault_device_id': 'pc2',
                'fault_type': 'wrong_gateway',
                'fault_summary': 'PC2 default gateway points to a nonexistent address 192.168.1.254.',
                'suggested_commands': ['ipconfig /all', 'ping 192.168.1.1'],
                'hints': ['Check the router LAN IP and verify PC2 default gateway matches.'],
                'verification_rule': {'target_device': 'pc2', 'required_field': 'gateway', 'expected_value': '192.168.1.1'},
                'root_cause_explanation': 'When sending packets to non-local subnets, hosts transmit to the MAC address of their configured default gateway. 192.168.1.254 does not exist, triggering an ARP timeout.',
                'recommended_solution': 'Change PC2 Default Gateway to 192.168.1.1.'
            },

            # Intermediate
            {
                'code': 'SCN-04',
                'title': 'VLAN Mismatch Between Switch Port and Workstation Subnet',
                'difficulty': 'intermediate',
                'category': 'VLANs',
                'symptoms': 'PC in Finance cannot communicate with Finance Server. Broadcasts stay isolated in VLAN 10.',
                'description': 'The Finance PC is configured on subnet 192.168.20.0/24 (VLAN 20), but the switch port Fa0/5 it is connected to was accidentally left in default VLAN 1.',
                'initial_topology': {
                    'devices': [
                        {'id': 'pc_fin', 'name': 'FinancePC', 'category': 'computers', 'ip': '192.168.20.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.20.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
                        {'id': 'sw1', 'name': 'Switch1', 'category': 'switches', 'interfaces': [{'name': 'Fa0/5', 'vlan': 1, 'status': 'up'}, {'name': 'Gi0/1', 'status': 'up'}], 'vlans': {'1': {'name': 'default'}, '20': {'name': 'Finance'}}},
                        {'id': 'r1', 'name': 'Router1', 'category': 'routers', 'ip': '192.168.20.1', 'interfaces': [{'name': 'Gi0/0.20', 'ip': '192.168.20.1', 'mask': '255.255.255.0', 'status': 'up'}]}
                    ],
                    'connections': [
                        {'source_device': 'pc_fin', 'source_port': 'eth0', 'target_device': 'sw1', 'target_port': 'Fa0/5', 'status': 'connected'},
                        {'source_device': 'sw1', 'source_port': 'Gi0/1', 'target_device': 'r1', 'target_port': 'Gi0/0.20', 'status': 'connected'}
                    ]
                },
                'fault_device_id': 'sw1',
                'fault_type': 'vlan_port_mismatch',
                'fault_summary': 'Switch port Fa0/5 is assigned to VLAN 1 instead of Finance VLAN 20.',
                'suggested_commands': ['show vlan brief', 'interface Fa0/5', 'switchport access vlan 20'],
                'hints': ['Use "show vlan brief" on Switch1 to inspect port assignments.'],
                'verification_rule': {'target_device': 'sw1', 'interface_name': 'Fa0/5', 'required_vlan': 20},
                'root_cause_explanation': 'Ethernet frames from FinancePC entered switch port Fa0/5 untagged and were tagged with VLAN 1, preventing them from reaching the VLAN 20 router gateway.',
                'recommended_solution': 'Assign switch port Fa0/5 to VLAN 20: "switchport mode access" -> "switchport access vlan 20".'
            },
            {
                'code': 'SCN-05',
                'title': 'Stateful Firewall Deny Rule Blocking Inbound Surveillance Video',
                'difficulty': 'intermediate',
                'category': 'Firewall',
                'symptoms': 'NVR in Management Zone cannot receive RTSP video stream (port 554) from IP Camera in DMZ/Camera zone.',
                'description': 'Security cameras were moved behind an enterprise perimeter firewall for isolation. The NVR can ping the camera, but live video streaming over TCP port 554 fails.',
                'initial_topology': {
                    'devices': [
                        {'id': 'cam1', 'name': 'DomeCamera', 'category': 'cctv', 'ip': '172.16.10.50', 'subnet_mask': '255.255.255.0', 'gateway': '172.16.10.1', 'interfaces': [{'name': 'eth0_PoE', 'status': 'up'}]},
                        {'id': 'fw1', 'name': 'Firewall1', 'category': 'firewalls', 'ip': '172.16.10.1', 'default_policy': 'deny', 'firewall_rules': [
                            {'id': 1, 'src_ip': 'any', 'dest_ip': 'any', 'protocol': 'ICMP', 'port': 'any', 'action': 'allow', 'enabled': True},
                            {'id': 2, 'src_ip': 'any', 'dest_ip': 'any', 'protocol': 'TCP', 'port': '554', 'action': 'deny', 'enabled': True}
                        ], 'interfaces': [{'name': 'igb1_LAN', 'ip': '192.168.1.1', 'mask': '255.255.255.0'}, {'name': 'igb2_DMZ', 'ip': '172.16.10.1', 'mask': '255.255.255.0'}]},
                        {'id': 'nvr1', 'name': 'NVR-Central', 'category': 'cctv', 'ip': '192.168.1.100', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'LAN1', 'status': 'up'}]}
                    ],
                    'connections': [
                        {'source_device': 'cam1', 'source_port': 'eth0_PoE', 'target_device': 'fw1', 'target_port': 'igb2_DMZ', 'status': 'connected'},
                        {'source_device': 'fw1', 'source_port': 'igb1_LAN', 'target_device': 'nvr1', 'target_port': 'LAN1', 'status': 'connected'}
                    ]
                },
                'fault_device_id': 'fw1',
                'fault_type': 'firewall_blocking_rtsp',
                'fault_summary': 'Firewall rule #2 explicitly denies TCP port 554 (RTSP stream).',
                'suggested_commands': ['iptables -L -n -v', 'check firewall rules'],
                'hints': ['Look for firewall rules blocking TCP port 554.'],
                'verification_rule': {'target_device': 'fw1', 'rule_id': 2, 'required_action': 'allow'},
                'root_cause_explanation': 'Rule 2 drops all TCP port 554 packets. RTSP is the protocol used to carry video stream payloads from IP cameras to NVRs.',
                'recommended_solution': 'Change Firewall Rule #2 action from "deny" to "allow" for TCP port 554.'
            },

            # Advanced
            {
                'code': 'SCN-06',
                'title': 'PoE Switch Power Budget Exceeded (Camera Drops Offline)',
                'difficulty': 'advanced',
                'category': 'PoE & Surveillance',
                'symptoms': 'When the 8th PTZ dome camera is plugged in, ports 7 and 8 turn off power. Cameras reboot intermittently.',
                'description': 'An 8-port switch with a total power budget of 60 Watts was loaded with four 12W dome cameras and two 25W PTZ cameras. Total demand exceeds capacity.',
                'initial_topology': {
                    'devices': [
                        {'id': 'sw_poe', 'name': 'PoESwitch', 'category': 'switches', 'power_watts': 15.0, 'poe_budget_watts': 60.0, 'interfaces': [
                            {'name': f'Port{i}', 'poe': True, 'status': 'up'} for i in range(1, 9)
                        ]}
                    ],
                    'connections': []
                },
                'fault_device_id': 'sw_poe',
                'fault_type': 'poe_budget_overload',
                'fault_summary': 'Connected cameras draw 74 Watts, exceeding the 60W switch PoE power budget.',
                'suggested_commands': ['show power inline', 'calculate poe budget'],
                'hints': ['Sum the wattage of all connected cameras against the switch poe_budget_watts.'],
                'verification_rule': {'target_device': 'sw_poe', 'required_budget_watts': 120.0},
                'root_cause_explanation': 'When total connected PoE device wattage exceeds the internal power supply rating, the switch shuts off power to lower-priority ports.',
                'recommended_solution': 'Upgrade the switch to a model supporting at least 120W PoE budget, or add a dedicated PoE+ injector.'
            }
        ]

        for scn in troubleshooting_scenarios_seed:
            TroubleshootingScenario.objects.get_or_create(
                code=scn['code'],
                defaults=scn
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(troubleshooting_scenarios_seed)} Troubleshooting Scenarios.'))

        # 8. Seed 18 Prebuilt Network Templates
        templates_seed = [
            {'name': 'Basic Home Network', 'cat': 'Home & SOHO', 'devs': 4, 'conns': 3, 'desc': 'Internet Gateway, Wi-Fi Access Point, Desktop PC, and Network Printer.'},
            {'name': 'Small Office Network (SOHO)', 'cat': 'Small Business', 'devs': 6, 'conns': 5, 'desc': 'Edge Router with NAT, 8-port Managed Switch, NAS, Workstations, and Wi-Fi.'},
            {'name': 'Enterprise Campus LAN', 'cat': 'Enterprise', 'devs': 10, 'conns': 12, 'desc': 'Core L3 Switch, Distribution Switches, Access Switches, and Workstations.'},
            {'name': 'Two-VLAN Isolated Network', 'cat': 'VLANs', 'devs': 5, 'conns': 4, 'desc': 'VLAN 10 (Sales) and VLAN 20 (Engineering) on a single managed switch.'},
            {'name': 'Inter-VLAN Routing (Router-on-a-Stick)', 'cat': 'Routing', 'devs': 6, 'conns': 5, 'desc': '802.1Q trunk link to a Cisco router with sub-interfaces Gi0/0.10 and Gi0/0.20.'},
            {'name': 'Router-to-Router Point-to-Point Topology', 'cat': 'Routing', 'devs': 4, 'conns': 3, 'desc': 'Two branch routers interconnected via /30 point-to-point transit link.'},
            {'name': 'Firewall-Protected Perimeter Network', 'cat': 'Security', 'devs': 6, 'conns': 5, 'desc': 'Stateful NGFW with LAN, WAN, and DMZ filtering web and ICMP traffic.'},
            {'name': 'DMZ Server Infrastructure Network', 'cat': 'Security', 'devs': 7, 'conns': 6, 'desc': 'Public Nginx Web and DNS servers hosted in an isolated DMZ zone.'},
            {'name': 'Branch Office WAN Network', 'cat': 'Enterprise', 'devs': 8, 'conns': 7, 'desc': 'Headquarters router connected to remote Branch router over simulated WAN.'},
            {'name': 'OSPF Multi-Router Dynamic Topology', 'cat': 'Routing', 'devs': 5, 'conns': 5, 'desc': 'Three routers participating in OSPF Area 0 with dynamic route convergence.'},
            {'name': 'Wireless Enterprise Office Network', 'cat': 'Wireless', 'devs': 7, 'conns': 6, 'desc': 'Dual-band Wi-Fi 6 APs with multiple SSIDs mapped to employee and guest VLANs.'},
            {'name': 'NAS File-Sharing & Storage Network', 'cat': 'Storage', 'devs': 5, 'conns': 4, 'desc': 'High-performance NAS with LACP bonding, SMB shares, and RAID 5 storage.'},
            {'name': 'Departmental Network Printer Deployment', 'cat': 'Small Business', 'devs': 5, 'conns': 4, 'desc': 'Shared MFP laser printer with static IP and RAW 9100 / IPP print queues.'},
            {'name': 'IP Camera & NVR Video Surveillance', 'cat': 'CCTV', 'devs': 6, 'conns': 5, 'desc': '4K Dome Cameras connected to an NVR over a dedicated surveillance subnet.'},
            {'name': 'CCTV Network with PoE Switches', 'cat': 'CCTV', 'devs': 8, 'conns': 7, 'desc': 'Multiple PoE switches powering 8 IP cameras with PoE power budget monitoring.'},
            {'name': 'Multi-Floor Office Infrastructure', 'cat': 'Enterprise', 'devs': 12, 'conns': 14, 'desc': 'Core switch in server room connected via fiber uplinks to Floor 1 and Floor 2.'},
            {'name': 'Server Room & Datacenter Network', 'cat': 'Datacenter', 'devs': 9, 'conns': 10, 'desc': 'Redundant Top-of-Rack switches hosting Web, DB, DNS, and DHCP servers.'},
            {'name': 'Redundant Enterprise Network (Spanning Tree)', 'cat': 'Enterprise', 'devs': 8, 'conns': 10, 'desc': 'Triangular switch topology with Rapid Spanning Tree Protocol loop prevention.'},
        ]

        for t in templates_seed:
            NetworkProject.objects.get_or_create(
                name=t['name'],
                is_template=True,
                defaults={
                    'slug': t['name'].lower().replace(' ', '-').replace('(', '').replace(')', ''),
                    'description': t['desc'],
                    'template_category': t['cat'],
                    'device_count': t['devs'],
                    'connection_count': t['conns'],
                    'is_public': True,
                    'metadata': {'type': 'template', 'category': t['cat']}
                }
            )
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(templates_seed)} Prebuilt Network Templates.'))

        self.stdout.write(self.style.SUCCESS('Ramonet database seeding completed successfully!'))
