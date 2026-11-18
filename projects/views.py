import json
import csv
import re
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from audit.logger import SecurityLogger
from .models import NetworkProject
from ramonet_core import (
    TopologyEngine,
    ConfigurationHistoryManager,
    DeviceConfigurationService,
    ConfigurationValidator
)

def sanitize_csv_cell(value) -> str:
    """
    Prevents CSV Formula Injection (CWE-1236).
    If a string cell starts with =, +, -, @, tab, or carriage return,
    prefix it with a single quote to force spreadsheet programs to treat it as plain text.
    """
    val_str = str(value) if value is not None else ''
    if val_str and val_str[0] in ('=', '+', '-', '@', '\t', '\r'):
        return f"'{val_str}"
    return val_str

def sanitize_filename(name: str, default: str = 'Ramonet_Project') -> str:
    """
    Sanitizes filenames to prevent HTTP response splitting, header injection,
    and filesystem path traversal.
    """
    if not name or not isinstance(name, str):
        return default
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', name.strip())
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean[:64] or default


def project_manager_view(request):
    """
    Project Management View (IndexedDB local projects and server backups).
    Enforces object-level authorization: users only view their own projects and public templates.
    """
    templates = NetworkProject.objects.filter(is_template=True)
    
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            server_projects = NetworkProject.objects.filter(is_template=False)
        else:
            server_projects = NetworkProject.objects.filter(is_template=False).filter(
                models.Q(user=request.user) | models.Q(is_public=True)
            )
    else:
        server_projects = NetworkProject.objects.filter(is_template=False, is_public=True)

    context = {
        'templates': templates,
        'server_projects': server_projects,
        'page_title': 'Project Manager — Ramonet',
    }
    return render(request, 'projects/manager.html', context)


@api_view(['GET'])
@permission_classes([AllowAny])
def project_template_api(request):
    """
    Returns prebuilt network topology template JSON.
    Generates devices, interfaces, and cable links.
    """
    raw_name = request.GET.get('name', 'Basic Home Network')
    name = sanitize_filename(raw_name, default='Basic Home Network').replace('_', ' ')
    
    devices = []
    connections = []

    if 'VLAN' in name:
        devices = [
            {'id': 'sw1', 'name': 'Switch-VLAN', 'category': 'switches', 'icon': 'fa-network-wired', 'x': 340, 'y': 150, 'interfaces': [{'name': 'Fa0/1', 'status': 'up'}, {'name': 'Fa0/2', 'status': 'up'}, {'name': 'Gi0/1', 'status': 'up'}], 'vlans': {'10': {'name': 'Sales'}, '20': {'name': 'Engineering'}}},
            {'id': 'pc1', 'name': 'Sales-PC', 'category': 'computers', 'icon': 'fa-desktop', 'x': 140, 'y': 80, 'ip': '192.168.10.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.10.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
            {'id': 'pc2', 'name': 'Eng-PC', 'category': 'computers', 'icon': 'fa-desktop', 'x': 140, 'y': 240, 'ip': '192.168.20.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.20.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
            {'id': 'r1', 'name': 'CoreRouter', 'category': 'routers', 'icon': 'fa-route', 'x': 580, 'y': 150, 'ip': '192.168.10.1', 'interfaces': [{'name': 'Gi0/0.10', 'ip': '192.168.10.1', 'mask': '255.255.255.0', 'status': 'up'}, {'name': 'Gi0/0.20', 'ip': '192.168.20.1', 'mask': '255.255.255.0', 'status': 'up'}]}
        ]
        connections = [
            {'id': 'c1', 'source_device': 'pc1', 'source_port': 'eth0', 'target_device': 'sw1', 'target_port': 'Fa0/1', 'type': 'copper_straight', 'status': 'connected'},
            {'id': 'c2', 'source_device': 'pc2', 'source_port': 'eth0', 'target_device': 'sw1', 'target_port': 'Fa0/2', 'type': 'copper_straight', 'status': 'connected'},
            {'id': 'c3', 'source_device': 'sw1', 'source_port': 'Gi0/1', 'target_device': 'r1', 'target_port': 'Gi0/0.10', 'type': 'copper_straight', 'status': 'connected'}
        ]
    elif 'CCTV' in name or 'Camera' in name:
        devices = [
            {'id': 'cam1', 'name': 'DomeCamera1', 'category': 'cctv', 'icon': 'fa-camera', 'x': 100, 'y': 100, 'ip': '192.168.50.11', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.50.1', 'interfaces': [{'name': 'eth0_PoE', 'status': 'up'}]},
            {'id': 'cam2', 'name': 'DomeCamera2', 'category': 'cctv', 'icon': 'fa-camera', 'x': 100, 'y': 220, 'ip': '192.168.50.12', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.50.1', 'interfaces': [{'name': 'eth0_PoE', 'status': 'up'}]},
            {'id': 'sw_poe', 'name': 'PoE-Switch', 'category': 'switches', 'icon': 'fa-bolt', 'x': 320, 'y': 160, 'interfaces': [{'name': 'Port1', 'status': 'up'}, {'name': 'Port2', 'status': 'up'}, {'name': 'Port8', 'status': 'up'}]},
            {'id': 'nvr1', 'name': 'NVR-16CH', 'category': 'cctv', 'icon': 'fa-video', 'x': 540, 'y': 160, 'ip': '192.168.10.100', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.10.1', 'interfaces': [{'name': 'LAN1', 'status': 'up'}]},
            {'id': 'pc_mon', 'name': 'SecurityPC', 'category': 'computers', 'icon': 'fa-desktop', 'x': 740, 'y': 160, 'ip': '192.168.10.50', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.10.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]}
        ]
        connections = [
            {'id': 'c1', 'source_device': 'cam1', 'source_port': 'eth0_PoE', 'target_device': 'sw_poe', 'target_port': 'Port1', 'type': 'copper_straight', 'status': 'connected'},
            {'id': 'c2', 'source_device': 'cam2', 'source_port': 'eth0_PoE', 'target_device': 'sw_poe', 'target_port': 'Port2', 'type': 'copper_straight', 'status': 'connected'},
            {'id': 'c3', 'source_device': 'sw_poe', 'source_port': 'Port8', 'target_device': 'nvr1', 'target_port': 'LAN1', 'type': 'copper_straight', 'status': 'connected'},
            {'id': 'c4', 'source_device': 'nvr1', 'source_port': 'LAN1', 'target_device': 'pc_mon', 'target_port': 'eth0', 'type': 'copper_straight', 'status': 'connected'}
        ]
    elif 'Firewall' in name or 'DMZ' in name:
        devices = [
            {'id': 'pc_lan', 'name': 'LAN-Workstation', 'category': 'computers', 'icon': 'fa-desktop', 'x': 100, 'y': 160, 'ip': '192.168.1.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
            {'id': 'fw1', 'name': 'NetGate-NGFW', 'category': 'firewalls', 'icon': 'fa-shield-halved', 'x': 350, 'y': 160, 'ip': '192.168.1.1', 'interfaces': [{'name': 'igb1_LAN', 'ip': '192.168.1.1', 'mask': '255.255.255.0', 'status': 'up'}, {'name': 'igb2_DMZ', 'ip': '172.16.1.1', 'mask': '255.255.255.0', 'status': 'up'}, {'name': 'igb0_WAN', 'ip': '203.0.113.2', 'mask': '255.255.255.0', 'status': 'up'}]},
            {'id': 'srv_dmz', 'name': 'Nginx-WebServer', 'category': 'servers', 'icon': 'fa-server', 'x': 350, 'y': 320, 'ip': '172.16.1.100', 'subnet_mask': '255.255.255.0', 'gateway': '172.16.1.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
            {'id': 'wan_gw', 'name': 'ISP-Gateway', 'category': 'routers', 'icon': 'fa-route', 'x': 600, 'y': 160, 'ip': '203.0.113.1', 'interfaces': [{'name': 'Gi0/0', 'ip': '203.0.113.1', 'mask': '255.255.255.0', 'status': 'up'}]}
        ]
        connections = [
            {'id': 'c1', 'source_device': 'pc_lan', 'source_port': 'eth0', 'target_device': 'fw1', 'target_port': 'igb1_LAN', 'type': 'copper_straight', 'status': 'connected'},
            {'id': 'c2', 'source_device': 'fw1', 'source_port': 'igb2_DMZ', 'target_device': 'srv_dmz', 'target_port': 'eth0', 'type': 'copper_straight', 'status': 'connected'},
            {'id': 'c3', 'source_device': 'fw1', 'source_port': 'igb0_WAN', 'target_device': 'wan_gw', 'target_port': 'Gi0/0', 'type': 'fiber', 'status': 'connected'}
        ]
    else:
        devices = [
            {'id': 'pc1', 'name': 'PC1', 'category': 'computers', 'icon': 'fa-desktop', 'x': 120, 'y': 180, 'ip': '192.168.1.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
            {'id': 'sw1', 'name': 'Switch1', 'category': 'switches', 'icon': 'fa-network-wired', 'x': 340, 'y': 180, 'interfaces': [{'name': 'Fa0/1', 'status': 'up'}, {'name': 'Fa0/2', 'status': 'up'}, {'name': 'Gi0/1', 'status': 'up'}]},
            {'id': 'r1', 'name': 'Router1', 'category': 'routers', 'icon': 'fa-route', 'x': 560, 'y': 180, 'ip': '192.168.1.1', 'interfaces': [{'name': 'Gi0/0', 'ip': '192.168.1.1', 'mask': '255.255.255.0', 'status': 'up'}, {'name': 'Gi0/1', 'ip': '10.0.0.1', 'mask': '255.255.255.0', 'status': 'up'}]},
            {'id': 'srv1', 'name': 'WebServer', 'category': 'servers', 'icon': 'fa-server', 'x': 780, 'y': 180, 'ip': '10.0.0.100', 'subnet_mask': '255.255.255.0', 'gateway': '10.0.0.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]}
        ]
        connections = [
            {'id': 'c1', 'source_device': 'pc1', 'source_port': 'eth0', 'target_device': 'sw1', 'target_port': 'Fa0/1', 'type': 'copper_straight', 'status': 'connected'},
            {'id': 'c2', 'source_device': 'sw1', 'source_port': 'Gi0/1', 'target_device': 'r1', 'target_port': 'Gi0/0', 'type': 'copper_straight', 'status': 'connected'},
            {'id': 'c3', 'source_device': 'r1', 'source_port': 'Gi0/1', 'target_device': 'srv1', 'target_port': 'eth0', 'type': 'copper_straight', 'status': 'connected'}
        ]

    return Response({
        'id': 'proj_' + sanitize_filename(name).lower(),
        'name': name,
        'devices': devices,
        'connections': connections
    })


def documentation_view(request):
    """
    Project Configuration Documentation Generator View.
    """
    context = {
        'page_title': 'Network Documentation Generator — Ramonet',
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    return render(request, 'projects/documentation.html', context)


def api_export_documentation(request):
    """
    Exports full project documentation as JSON or CSV format.
    Enforces filename sanitization, CSV formula injection defense (CWE-1236),
    payload size limits, and security audit logging.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if len(request.body) > 2 * 1024 * 1024:
        return JsonResponse({'error': 'Payload size exceeds 2 MB limit.'}, status=413)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({'error': 'Expected JSON object'}, status=400)

    export_format = str(data.get('format', 'json')).lower()
    raw_project_name = data.get('project_name', 'Ramonet-Network-Spec')
    project_name = sanitize_filename(str(raw_project_name), default='Ramonet_Network_Spec')

    SecurityLogger.log_event(
        action='EXPORT_DOCUMENTATION',
        module='projects',
        request=request,
        details={'format': export_format, 'project_name': project_name}
    )

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{project_name}_Inventory.csv"'
        response['X-Content-Type-Options'] = 'nosniff'
        writer = csv.writer(response)
        writer.writerow(['Category', 'Device Name', 'Role', 'IP Address', 'Interface Count', 'Status'])

        for dev in data.get('devices', []):
            if not isinstance(dev, dict):
                continue
            writer.writerow([
                sanitize_csv_cell(dev.get('category', 'Generic')),
                sanitize_csv_cell(dev.get('name', 'Unknown')),
                sanitize_csv_cell(dev.get('role', 'Node')),
                sanitize_csv_cell(dev.get('ip', 'N/A')),
                sanitize_csv_cell(len(dev.get('interfaces', []))),
                sanitize_csv_cell(dev.get('status', 'Active'))
            ])
        return response

    # Return full JSON documentation
    doc_payload = {
        'generator': 'Ramonet Network Architecture Suite',
        'version': '2.0.0',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'project': {
            'name': project_name,
            'author': str(data.get('author', 'Network Engineer'))[:64],
            'revision': str(data.get('revision', '1.0'))[:16],
            'description': str(data.get('description', 'Comprehensive Enterprise Network Infrastructure Plan'))[:512],
        },
        'devices': data.get('devices', [])[:100],
        'connections': data.get('connections', [])[:200],
        'subnets': data.get('subnets', [])[:50],
        'vlans': data.get('vlans', [])[:50],
        'racks': data.get('racks', [])[:10],
        'cctv': data.get('cctv', {}),
        'firewall_rules': data.get('firewall_rules', [])[:100],
    }
    return JsonResponse(doc_payload)


def scenarios_view(request):
    """
    Pre-built Network Scenarios Library (16+ practical enterprise network scenarios).
    """
    scenarios = [
        {'id': 'home_basic', 'title': '1. Basic Home Office LAN', 'category': 'Home & SOHO', 'badge': 'Beginner', 'devices_count': 4, 'description': 'Wi-Fi router, PC, smartphone, and laser printer sharing a single NAT gateway.', 'focus': 'DHCP, NAT, WPA2 Wi-Fi, Private IPv4'},
        {'id': 'small_office', 'title': '2. Small Office Branch (SOHO)', 'category': 'Home & SOHO', 'badge': 'Beginner', 'devices_count': 6, 'description': 'Unmanaged switch with PoE, router gateway, 3 workstations, and network printer.', 'focus': 'Default Gateway, ARP, Layer 2 Switching'},
        {'id': 'vlan_segmentation', 'title': '3. Dual-VLAN Corporate Segmentation', 'category': 'Enterprise Switching', 'badge': 'Intermediate', 'devices_count': 5, 'description': 'Sales VLAN 10 and Engineering VLAN 20 isolated on a single Managed Switch.', 'focus': '802.1Q Tags, Access Ports, Broadcast Isolation'},
        {'id': 'inter_vlan_router_stick', 'title': '4. Inter-VLAN Router-on-a-Stick', 'category': 'Enterprise Routing', 'badge': 'Intermediate', 'devices_count': 6, 'description': '802.1Q sub-interfaces on Cisco IOS Router routing packets between VLAN 10, 20, and 30.', 'focus': 'Router Sub-interfaces, 802.1Q Encapsulation, Trunking'},
        {'id': 'firewall_dmz', 'title': '5. Perimeter Firewall with DMZ', 'category': 'Network Security', 'badge': 'Intermediate', 'devices_count': 5, 'description': '3-Zone Security Architecture: WAN (Untrusted), DMZ (Public Web Server), and LAN (Internal).', 'focus': 'Stateful Packet Filtering, DMZ Isolation, NAT Port Forwarding'},
        {'id': 'branch_wan_ospf', 'title': '6. Multi-Branch OSPF Routed WAN', 'category': 'Dynamic Routing', 'badge': 'Advanced', 'devices_count': 8, 'description': 'Headquarters router connected to two Branch offices via serial/Gigabit point-to-point links running OSPF Area 0.', 'focus': 'OSPF Adjacency, Link-State Advertisements, Cost Metrics'},
        {'id': 'redundant_hsrp', 'title': '7. Redundant Gateway Failover (HSRP/VRRP)', 'category': 'High Availability', 'badge': 'Advanced', 'devices_count': 6, 'description': 'Active and Standby routers sharing a Virtual IP for seamless default gateway failover.', 'focus': 'Virtual IP, Priority Preemption, Keepalive Hellos'},
        {'id': 'cctv_poe_surveillance', 'title': '8. CCTV Surveillance & NVR Storage Network', 'category': 'Physical & IoT', 'badge': 'Intermediate', 'devices_count': 7, 'description': '802.3at PoE+ switch powering dome and PTZ cameras with dedicated 16-channel NVR.', 'focus': 'PoE Power Budget, ONVIF Streams, RTSP, Storage Retention'},
        {'id': 'datacenter_server_room', 'title': '9. Server Room & Physical Rack Architecture', 'category': 'Data Center', 'badge': 'Advanced', 'devices_count': 9, 'description': '42U equipment rack with redundant Top-of-Rack (ToR) switches, UPS battery backup, and SAN storage.', 'focus': 'Rack Elevation, Thermal Load (BTU), Dual PSU Feed'},
        {'id': 'enterprise_wifi_controller', 'title': '10. Enterprise Wireless with WLC & APs', 'category': 'Wireless', 'badge': 'Intermediate', 'devices_count': 6, 'description': 'Centralized Wireless LAN Controller (WLC) managing lightweight PoE Access Points.', 'focus': 'CAPWAP Tunnels, Centralized SSID, Fast Roaming'},
        {'id': 'stp_loop_prevention', 'title': '11. Spanning Tree Protocol (STP) Mesh', 'category': 'Enterprise Switching', 'badge': 'Advanced', 'devices_count': 5, 'description': 'Triangle switch topology preventing broadcast storms by blocking redundant loop links.', 'focus': 'BPDU, Root Bridge Election, Blocking Ports'},
        {'id': 'etherchannel_lacp', 'title': '12. Link Aggregation (LACP EtherChannel)', 'category': 'Enterprise Switching', 'badge': 'Intermediate', 'devices_count': 4, 'description': 'Two switches bundled over 4x 1Gbps interfaces into a high-bandwidth 4Gbps port-channel.', 'focus': '802.3ad LACP, Load Balancing, Link Redundancy'},
        {'id': 'nas_san_storage', 'title': '13. High-Throughput NAS & iSCSI SAN', 'category': 'Storage', 'badge': 'Intermediate', 'devices_count': 5, 'description': 'TrueNAS Enterprise storage server delivering NFS/SMB shares and iSCSI LUNs over 10G SFP+.', 'focus': 'RAID 5/10, MTU 9000 Jumbo Frames, Multi-path I/O'},
        {'id': 'multi_floor_campus', 'title': '14. Multi-Floor Campus Core-Distribution-Access', 'category': 'Campus Architecture', 'badge': 'Advanced', 'devices_count': 10, 'description': 'Hierarchical network design with Core Layer, Distribution Layer, and Floor Access Switches.', 'focus': 'Hierarchical 3-Tier Design, Fiber Backbones, Aggregation'},
        {'id': 'network_recovery_drill', 'title': '15. Disaster Recovery & Link Failure Drill', 'category': 'Troubleshooting', 'badge': 'Advanced', 'devices_count': 7, 'description': 'Simulated fiber cut drill to test dynamic convergence and routing table reconvergence.', 'focus': 'Convergence Time, Route Poisoning, Alternate Paths'},
        {'id': 'zero_trust_segmentation', 'title': '16. Zero-Trust Micro-Segmentation', 'category': 'Network Security', 'badge': 'Advanced', 'devices_count': 6, 'description': 'Strict East-West firewall inspection isolating database servers, APIs, and client pods.', 'focus': 'Microsegmentation, Zero Trust, Port-Level ACLs'}
    ]

    return render(request, 'projects/scenarios.html', {
        'page_title': 'Network Scenario Library — Ramonet',
        'scenarios': scenarios,
    })


def changes_view(request):
    """
    Network Change Management & Snapshot Diff View.
    """
    return render(request, 'projects/changes.html', {
        'page_title': 'Network Change Management & Diffs — Ramonet',
    })


def api_snapshot_diff(request):
    """
    Computes unified text diff and structural JSON diff between two configuration snapshots.
    Validates payload bounds to prevent ReDoS / memory exhaustion.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if len(request.body) > 2 * 1024 * 1024:
        return JsonResponse({'error': 'Payload size exceeds 2 MB limit.'}, status=413)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    config_before = str(data.get('config_before', ''))[:500000]
    config_after = str(data.get('config_after', ''))[:500000]
    device_name = sanitize_filename(str(data.get('device_name', 'Device')), default='Device')

    diff_lines = ConfigurationHistoryManager.compute_unified_diff(
        config_before, config_after,
        fromfile=f'{device_name}-Snapshot-1',
        tofile=f'{device_name}-Snapshot-2'
    )

    return JsonResponse({
        'device_name': device_name,
        'diff': diff_lines,
        'lines_added': sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++')),
        'lines_removed': sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---')),
        'is_identical': len(diff_lines) == 0
    })


def backups_view(request):
    """
    Configuration Backup, Export & Safe Restore View.
    """
    return render(request, 'projects/backups.html', {
        'page_title': 'Configuration Backup & Restore — Ramonet',
    })


def api_backup_restore(request):
    """
    Validates and restores a topology configuration JSON.
    Treats input strictly as untrusted, verifying schemas, duplicate IPs, and device integrity.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if len(request.body) > 2 * 1024 * 1024:
        return JsonResponse({'error': 'Payload size exceeds 2 MB limit.'}, status=413)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception as e:
        return JsonResponse({'error': f'Invalid JSON payload: {str(e)}'}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({'error': 'Payload must be a JSON object.'}, status=400)

    devices = data.get('devices', [])
    connections = data.get('connections', [])

    if not isinstance(devices, list):
        return JsonResponse({'error': 'Schema error: "devices" must be a list.'}, status=400)
    if not isinstance(connections, list):
        return JsonResponse({'error': 'Schema error: "connections" must be a list.'}, status=400)

    # Resource exhaustion protection limits
    if len(devices) > 100:
        return JsonResponse({'error': 'Device limit exceeded (maximum 100 devices per topology).'}, status=400)
    if len(connections) > 200:
        return JsonResponse({'error': 'Connection limit exceeded (maximum 200 links per topology).'}, status=400)

    for dev in devices:
        if not isinstance(dev, dict):
            return JsonResponse({'error': 'Invalid device item: must be an object.'}, status=400)
        for str_key in ('name', 'ip', 'subnet_mask', 'gateway', 'category', 'model_name'):
            if str_key in dev and isinstance(dev[str_key], str) and len(dev[str_key]) > 128:
                dev[str_key] = dev[str_key][:128]

    # Run core configuration validator
    duplicate_ips = ConfigurationValidator.check_duplicate_ips(devices)
    gateway_issues = ConfigurationValidator.validate_device_gateways(devices)

    is_valid = len(duplicate_ips) == 0 and len(gateway_issues) == 0

    SecurityLogger.log_event(
        action='RESTORE_BACKUP_VALIDATION',
        module='projects',
        request=request,
        details={'device_count': len(devices), 'connection_count': len(connections), 'is_valid': is_valid}
    )

    return JsonResponse({
        'success': True,
        'is_valid': is_valid,
        'device_count': len(devices),
        'connection_count': len(connections),
        'duplicate_ips': duplicate_ips,
        'gateway_issues': gateway_issues,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })
