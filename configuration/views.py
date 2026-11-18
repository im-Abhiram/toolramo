import json
import ipaddress
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from devices.models import DeviceDefinition, DeviceCategory
from commands.models import CommandEntry
from knowledgebase.models import ConnectionRule, KnowledgeArticle
from ramonet_core import ConfigurationValidator

def assistant_view(request):
    """
    Ramonet Advanced Network Configuration Assistant Hub.
    """
    categories = DeviceCategory.objects.prefetch_related('devices').all()
    connection_rules = ConnectionRule.objects.all()
    featured_commands = CommandEntry.objects.filter(platform='cisco_ios')[:6]

    context = {
        'categories': categories,
        'connection_rules': connection_rules,
        'featured_commands': featured_commands,
        'page_title': 'Configuration Assistant',
    }
    return render(request, 'configuration/assistant.html', context)

def switches_view(request):
    """Switch Configuration Manager (VLANs, Trunk/Access ports, MAC table, STP, Port Security)"""
    switches = DeviceDefinition.objects.filter(category__slug='switches')
    return render(request, 'configuration/switches.html', {'switches': switches, 'page_title': 'Switch Configuration Manager'})

def routers_view(request):
    """Router Configuration Manager (Interfaces, Routing Table, Static Routes, OSPF, NAT, ACL)"""
    routers = DeviceDefinition.objects.filter(category__slug='routers')
    return render(request, 'configuration/routers.html', {'routers': routers, 'page_title': 'Router Configuration Manager'})

def firewalls_view(request):
    """Firewall Manager (Zones LAN/WAN/DMZ, Stateful Filtering, Rule Priority, NAT, Port Forwarding)"""
    firewalls = DeviceDefinition.objects.filter(category__slug='firewalls')
    return render(request, 'configuration/firewalls.html', {'firewalls': firewalls, 'page_title': 'Firewall Manager'})

def wireless_view(request):
    """Wireless Network Manager (SSIDs, WPA2/WPA3, Frequency Bands, VLAN Mapping)"""
    return render(request, 'configuration/wireless.html', {'page_title': 'Wireless Network Manager'})

def servers_view(request):
    """Server Manager (DNS records, DHCP Pools, Web HTTP/HTTPS, FTP, Authentication)"""
    return render(request, 'configuration/servers.html', {'page_title': 'Server Manager'})

def storage_view(request):
    """NAS & Storage Manager (RAID 0/1/5/6/10, SMB/NFS shares, LACP bonding)"""
    return render(request, 'configuration/storage.html', {'page_title': 'NAS & Storage Manager'})

def cctv_view(request):
    """
    Professional CCTV Network Planner.
    Calculates camera bandwidth, PoE power requirements, NVR channel capacity,
    and storage retention in TB. Detects bottlenecks and simulates camera registration.
    """
    return render(request, 'configuration/cctv.html', {'page_title': 'CCTV Network Planner — Ramonet'})

def ipam_view(request):
    """
    Central IP Address Management (IPAM) Hub.
    Subnet management, CIDR calculations, VLSM tree, duplicate IP scanning,
    and real-time device address synchronization.
    """
    return render(request, 'configuration/ipam.html', {'page_title': 'IP Address Manager (IPAM) — Ramonet'})


def cctv_calculate_api(request):
    """
    Computes exact aggregate surveillance bandwidth (Mbps), total PoE demand (Watts),
    and storage retention capacity (TB). Detects power or channel overload.
    Enforces safe input bounds to prevent resource exhaustion and unhandled exceptions.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if len(request.body) > 1 * 1024 * 1024:
        return JsonResponse({'error': 'Payload size exceeds 1 MB limit.'}, status=413)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({'error': 'Expected JSON object'}, status=400)

    cameras = data.get('cameras', [])
    if not isinstance(cameras, list):
        return JsonResponse({'error': '"cameras" must be a list'}, status=400)

    if len(cameras) > 128:
        return JsonResponse({'error': 'Maximum 128 cameras supported per calculation.'}, status=400)

    try:
        retention_days = max(1, min(365, int(data.get('retention_days', 30))))
    except (ValueError, TypeError):
        retention_days = 30

    try:
        nvr_channels = max(1, min(128, int(data.get('nvr_channels', 16))))
    except (ValueError, TypeError):
        nvr_channels = 16

    try:
        poe_budget = max(10.0, min(5000.0, float(data.get('poe_budget_watts', 370.0))))
    except (ValueError, TypeError):
        poe_budget = 370.0

    total_bw_mbps = 0.0
    total_poe_w = 0.0

    bitrate_lookup = {
        ('720p', 'H.264'): 2.0, ('720p', 'H.265'): 1.2,
        ('1080p', 'H.264'): 4.5, ('1080p', 'H.265'): 2.5,
        ('4MP', 'H.264'): 8.0, ('4MP', 'H.265'): 4.5,
        ('4K', 'H.264'): 16.0, ('4K', 'H.265'): 8.0
    }

    camera_details = []
    for c in cameras:
        if not isinstance(c, dict):
            continue
        res = str(c.get('resolution', '1080p'))[:16]
        codec = str(c.get('codec', 'H.265'))[:16]
        try:
            fps = max(1, min(120, int(c.get('fps', 30))))
        except (ValueError, TypeError):
            fps = 30
        cam_type = str(c.get('type', 'bullet'))[:32]

        base_bw = bitrate_lookup.get((res, codec), 3.0)
        bw = round(base_bw * (fps / 30.0), 2)
        poe_w = 25.0 if 'ptz' in cam_type.lower() else 12.0

        total_bw_mbps += bw
        total_poe_w += poe_w

        camera_details.append({
            'name': str(c.get('name', 'Camera'))[:64],
            'ip': str(c.get('ip', '192.168.50.10'))[:45],
            'type': cam_type,
            'resolution': res,
            'codec': codec,
            'fps': fps,
            'bandwidth_mbps': bw,
            'poe_watts': poe_w,
            'status': str(c.get('status', 'online'))[:16]
        })

    daily_gb = (total_bw_mbps * 3600 * 24) / (8 * 1024)
    storage_tb = round((daily_gb * retention_days) / 1024.0, 2)

    alerts = []
    if len(camera_details) > nvr_channels:
        alerts.append({
            'type': 'channel_overflow',
            'severity': 'danger',
            'message': f"Camera count ({len(camera_details)}) exceeds NVR channel capacity ({nvr_channels} channels)!"
        })

    if total_poe_w > poe_budget:
        alerts.append({
            'type': 'poe_overload',
            'severity': 'danger',
            'message': f"Total PoE demand ({round(total_poe_w, 1)}W) exceeds switch power budget ({poe_budget}W)!"
        })

    if total_bw_mbps > 900.0:
        alerts.append({
            'type': 'uplink_saturation',
            'severity': 'warning',
            'message': f"Aggregate stream traffic ({round(total_bw_mbps, 1)} Mbps) saturating 1Gbps uplink!"
        })

    return JsonResponse({
        'camera_count': len(camera_details),
        'cameras': camera_details,
        'total_bandwidth_mbps': round(total_bw_mbps, 2),
        'total_poe_watts': round(total_poe_w, 1),
        'poe_budget_watts': poe_budget,
        'poe_remaining_watts': max(0.0, round(poe_budget - total_poe_w, 1)),
        'retention_days': retention_days,
        'required_storage_tb': storage_tb,
        'alerts': alerts
    })


def ipam_validate_api(request):
    """
    Validates subnets, IP assignments, and duplicate IP conflicts across the network.
    Enforces payload bounds to prevent memory abuse.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if len(request.body) > 1 * 1024 * 1024:
        return JsonResponse({'error': 'Payload size exceeds 1 MB limit.'}, status=413)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({'error': 'Expected JSON object'}, status=400)

    devices = data.get('devices', [])
    if not isinstance(devices, list):
        return JsonResponse({'error': '"devices" must be a list'}, status=400)

    if len(devices) > 150:
        return JsonResponse({'error': 'Exceeded maximum device limit (150 items).'}, status=400)

    duplicates = ConfigurationValidator.check_duplicate_ips(devices)
    gateway_issues = ConfigurationValidator.validate_device_gateways(devices)

    return JsonResponse({
        'valid': len(duplicates) == 0 and len(gateway_issues) == 0,
        'duplicates': duplicates,
        'gateway_issues': gateway_issues,
        'device_count': len(devices)
    })
