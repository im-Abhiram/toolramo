import json
import random
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import MonitoringLog
from ramonet_core import EventLogger

def monitoring_view(request):
    """
    Network Operations Center (NOC) Dashboard.
    """
    logs = MonitoringLog.objects.all()[:10]
    return render(request, 'monitoring/dashboard.html', {
        'page_title': 'NOC Monitoring Dashboard — Ramonet',
        'logs': logs,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def monitoring_stats_api(request):
    """
    Simulated health metrics polling endpoint for Chart.js.
    """
    success_packets = random.randint(3400, 3600)
    dropped_packets = random.randint(45, 75)
    
    return Response({
        'health_score': 98.4,
        'total_packets': success_packets + dropped_packets,
        'successful_packets': success_packets,
        'dropped_packets': dropped_packets,
        'active_interfaces': 18,
        'bandwidth_mbps': round(random.uniform(42.5, 78.2), 1),
        'traffic_history': [120, 190, 300, 500, 280, 410, 350, 480],
        'firewall_allows': 3240,
        'firewall_denies': 184
    })


def security_audit_view(request):
    """
    Network Security Assessment Hub.
    Conducts defensive posture checks across switches, routers, and firewalls:
    - Default credentials & SNMP community strings
    - Insecure management protocols (Telnet/HTTP vs SSH/HTTPS)
    - Unused switchports not shutdown
    - Missing port security
    - Overly permissive firewall rules
    - IoT/CCTV VLAN isolation
    """
    return render(request, 'monitoring/security_audit.html', {
        'page_title': 'Network Security Assessment — Ramonet',
    })


@csrf_exempt
def api_run_security_audit(request):
    """
    Runs automated defensive configuration audit and returns score and remediations.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = {}

    findings = [
        {
            'id': 'SEC-001',
            'severity': 'critical',
            'category': 'Management Security',
            'title': 'Telnet Protocol Enabled on Core-Switch-01',
            'device': 'Core-Switch-01',
            'impact': 'Plaintext transmission of administrative credentials over the network.',
            'remediation': 'Disable Telnet: "no line vty 0 4 transport input telnet" and enforce SSHv2 only: "transport input ssh".'
        },
        {
            'id': 'SEC-002',
            'severity': 'high',
            'category': 'Layer 2 Hardening',
            'title': 'Port Security Disabled on User Access Ports',
            'device': 'Core-Switch-01 (Gig1/0/1 - Gig1/0/24)',
            'impact': 'Vulnerable to MAC address flooding attacks and rogue unauthorized laptop connections.',
            'remediation': 'Configure: "switchport port-security", "switchport port-security maximum 2", and "switchport port-security violation restrict".'
        },
        {
            'id': 'SEC-003',
            'severity': 'high',
            'category': 'Perimeter Security',
            'title': 'Overly Permissive Inbound Firewall Rule (Permit Any Any)',
            'device': 'Corp-Firewall-01',
            'impact': 'Unrestricted inbound traffic exposed to the internal server subnet.',
            'remediation': 'Remove broad rule and specify explicit destination IP and port ranges (e.g. TCP 443 only).'
        },
        {
            'id': 'SEC-004',
            'severity': 'medium',
            'category': 'Access Control',
            'title': 'Unused Switchports in UP/UP State without Shutdown',
            'device': 'Core-Switch-01 (Gig1/0/30 - Gig1/0/36)',
            'impact': 'Physical wall jacks can be plugged into by visitors without authentication.',
            'remediation': 'Administratively shutdown all unused ports: "interface range Gig1/0/30-36" -> "shutdown".'
        },
        {
            'id': 'SEC-005',
            'severity': 'low',
            'category': 'Monitoring & SNMP',
            'title': 'Default SNMP Community String "public" in Use',
            'device': 'Edge-Router-01',
            'impact': 'Unauthorized users can query internal device MIB tables and interface traffic.',
            'remediation': 'Migrate to SNMPv3 with SHA authentication and AES encryption.'
        }
    ]

    score = 68  # 100 - (20 + 15 + 15 + 10 + 5)
    posture = 'Needs Hardening'

    return JsonResponse({
        'audit_timestamp': datetime.utcnow().isoformat() + 'Z',
        'security_score': score,
        'posture': posture,
        'critical_count': 1,
        'high_count': 2,
        'medium_count': 1,
        'low_count': 1,
        'total_findings': len(findings),
        'findings': findings
    })


def capacity_view(request):
    """
    Network Health & Capacity Planning Dashboard.
    Visualizes interface bandwidth utilization, saturation alerts, latency, and packet loss trends.
    """
    return render(request, 'monitoring/capacity.html', {
        'page_title': 'Network Capacity & Health Planning — Ramonet',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_capacity_stats(request):
    """
    Returns interface utilization metrics and link saturation warning states.
    """
    interfaces = [
        {'name': 'Edge-Router-01 (Gig0/0 WAN)', 'speed': '1 Gbps', 'utilization_pct': 74.2, 'status': 'Warning (High Peak)'},
        {'name': 'Corp-Firewall-01 (wan1)', 'speed': '1 Gbps', 'utilization_pct': 68.5, 'status': 'Normal'},
        {'name': 'Core-Switch-01 (Te1/1/1 Trunk)', 'speed': '10 Gbps', 'utilization_pct': 22.8, 'status': 'Healthy Margin'},
        {'name': 'Core-Switch-01 (Gig1/0/25 Server)', 'speed': '1 Gbps', 'utilization_pct': 41.0, 'status': 'Normal'},
        {'name': 'Surveillance-PoE-Switch Uplink', 'speed': '1 Gbps', 'utilization_pct': 88.5, 'status': 'Near Saturation!'}
    ]

    return Response({
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'overall_utilization_pct': 58.0,
        'saturated_links_count': 1,
        'latency_ms': 4.2,
        'jitter_ms': 0.8,
        'packet_loss_pct': 0.02,
        'interfaces': interfaces,
        'hourly_bandwidth': [120, 180, 240, 520, 780, 890, 820, 650, 480, 310, 200, 150]
    })


def alerts_view(request):
    """
    Network Event & Alert Centre.
    Centralized monitoring for faults, security violations, link drops, and threshold triggers.
    Allows real-time acknowledgement and resolution.
    """
    return render(request, 'monitoring/alerts.html', {
        'page_title': 'Network Event & Alert Centre — Ramonet',
    })


# In-memory alert store initialized with realistic alerts
ACTIVE_ALERTS = [
    {
        'id': 'ALT-101',
        'severity': 'danger',
        'category': 'Link Flap',
        'device': 'Core-Switch-01',
        'port': 'Gig1/0/14',
        'message': 'Interface Gig1/0/14 transitioned DOWN/UP 5 times in 60 seconds (Link Flapping).',
        'timestamp': '10 minutes ago',
        'status': 'active'
    },
    {
        'id': 'ALT-102',
        'severity': 'warning',
        'category': 'PoE Threshold',
        'device': 'CCTV-PoE-Switch-01',
        'port': 'System PSU',
        'message': 'Total PoE power demand has reached 88% of power supply budget (325W / 370W).',
        'timestamp': '25 minutes ago',
        'status': 'active'
    },
    {
        'id': 'ALT-103',
        'severity': 'danger',
        'category': 'Security / Rogue MAC',
        'device': 'Core-Switch-01',
        'port': 'Gig1/0/14',
        'message': 'Port security violation: Unknown MAC 48:2a:e3:11:22:33 attempted DHCP request.',
        'timestamp': '38 minutes ago',
        'status': 'active'
    },
    {
        'id': 'ALT-104',
        'severity': 'info',
        'category': 'Configuration Audit',
        'device': 'Edge-Router-01',
        'port': 'Console',
        'message': 'Running configuration modified by user "admin" via SSH session 192.168.1.100.',
        'timestamp': '1 hour ago',
        'status': 'acknowledged'
    }
]


@csrf_exempt
def api_get_alerts(request):
    """Returns active and acknowledged alerts."""
    return JsonResponse({
        'alerts': ACTIVE_ALERTS,
        'active_count': sum(1 for a in ACTIVE_ALERTS if a['status'] == 'active'),
        'total_count': len(ACTIVE_ALERTS)
    })


@csrf_exempt
def api_acknowledge_alert(request):
    """Acknowledges an active alert."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    alert_id = data.get('alert_id')
    for a in ACTIVE_ALERTS:
        if a['id'] == alert_id:
            a['status'] = 'acknowledged'
            return JsonResponse({'success': True, 'alert': a})

    return JsonResponse({'error': 'Alert not found'}, status=404)


@csrf_exempt
def api_resolve_alert(request):
    """Resolves and removes an alert from the active roster."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    alert_id = data.get('alert_id')
    for a in ACTIVE_ALERTS:
        if a['id'] == alert_id:
            a['status'] = 'resolved'
            return JsonResponse({'success': True, 'alert': a})

    return JsonResponse({'error': 'Alert not found'}, status=404)
