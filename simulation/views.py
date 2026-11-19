import json
import ipaddress
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .engine import NetworkSimulationEngine

def visualizer_view(request):
    """
    Dedicated Packet Flow Visualizer view.
    """
    return render(request, 'simulation/visualizer.html', {
        'page_title': 'Packet Flow Visualizer'
    })

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def trace_packet_api(request):
    """
    Simulates packet flow through the specified network topology.
    Returns hop-by-hop forwarding decisions, interface ingress/egress, and drop diagnostics.
    Enforces IP format validation, port bounds, and topology size constraints.
    """
    data = request.data
    if not isinstance(data, dict):
        return Response({
            'success': False,
            'drop_reason': 'INVALID_REQUEST',
            'details': 'Payload must be a JSON object.',
            'hops': []
        }, status=400)

    src_dev_id = str(data.get('src_dev_id', '')).strip()[:64]
    dest_ip = str(data.get('dest_ip', '')).strip()[:45]
    protocol = str(data.get('protocol', 'ICMP')).upper()[:16]

    if not src_dev_id or not dest_ip:
        return Response({
            'success': False,
            'drop_reason': 'INVALID_REQUEST',
            'details': 'Source device ID and Destination IP are required.',
            'hops': []
        }, status=400)

    # Validate IP address syntax (support IPv4)
    try:
        ipaddress.ip_address(dest_ip)
    except ValueError:
        return Response({
            'success': False,
            'drop_reason': 'INVALID_IP_FORMAT',
            'details': f"Destination address '{dest_ip}' is not a valid IP address.",
            'hops': []
        }, status=400)

    # Safe parse of port numbers
    try:
        dest_port = max(1, min(65535, int(data.get('dest_port', 80))))
    except (ValueError, TypeError):
        dest_port = 80

    try:
        src_port = max(1, min(65535, int(data.get('src_port', 49152))))
    except (ValueError, TypeError):
        src_port = 49152

    topology = data.get('topology', {})
    if not isinstance(topology, dict):
        topology = {}

    devices = topology.get('devices', [])
    if isinstance(devices, list) and len(devices) > 100:
        return Response({
            'success': False,
            'drop_reason': 'TOPOLOGY_LIMIT_EXCEEDED',
            'details': 'Simulation limited to topologies with at most 100 devices.',
            'hops': []
        }, status=400)

    engine = NetworkSimulationEngine(topology)
    result = engine.simulate_packet(
        src_dev_id=src_dev_id,
        dest_ip=dest_ip,
        protocol=protocol,
        dest_port=dest_port,
        src_port=src_port
    )
    return Response(result)


# ==============================================================================
# PROTOCOL ANALYZER & WHAT-IF SIMULATION ENGINES (Priority 2 & 3)
# ==============================================================================
from .protocol_analyzer import ProtocolAnalyzerEngine
from .what_if_engine import WhatIfEngine

def packet_analyzer_view(request):
    """
    Renders the Interactive Packet Capture & Protocol Inspection Studio.
    Provides Wireshark-inspired frame dissection, OSI layering, and packet filtering.
    """
    scenarios = [
        {'id': 'dns_query', 'name': 'DNS Query & Resolution (UDP 53)'},
        {'id': 'dhcp_dora', 'name': 'DHCP 4-Way DORA Lease Handshake'},
        {'id': 'http_session', 'name': 'HTTP/1.1 Web Session & TCP 3-Way Handshake'},
        {'id': 'arp_resolution', 'name': 'ARP Resolution & MAC Learning'},
        {'id': 'icmp_ping', 'name': 'ICMP Echo Ping & RTT Verification'},
        {'id': 'vlan_trunk', 'name': '802.1Q Tagged Trunk Ingress/Egress'}
    ]
    return render(request, 'simulation/protocol_analyzer.html', {
        'page_title': 'Packet Capture & Protocol Analyzer — Ramonet',
        'scenarios': scenarios
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_generate_packet_capture(request):
    """
    Generates realistic, dissected simulation packets for the selected protocol scenario.
    Applies optional Wireshark-syntax filters.
    """
    try:
        data = request.data if isinstance(request.data, dict) else json.loads(request.body.decode('utf-8'))
    except Exception:
        return Response({'success': False, 'error': 'Invalid JSON'}, status=400)

    scenario = str(data.get('scenario', 'dns_query'))[:32]
    filter_query = str(data.get('filter', '')).strip()[:100]
    context = data.get('context', {})

    packets = ProtocolAnalyzerEngine.generate_capture(scenario, topology_context=context)
    if filter_query:
        packets = ProtocolAnalyzerEngine.filter_packets(packets, filter_query)

    return Response({
        'success': True,
        'scenario': scenario,
        'filter_applied': filter_query,
        'packet_count': len(packets),
        'packets': packets
    })


def what_if_view(request):
    """
    Renders the What-If Simulation & Scenario Comparison Studio.
    Provides non-destructive architectural failure simulation in an isolated sandbox.
    """
    scenarios = [
        {'key': k, **v} for k, v in WhatIfEngine.SCENARIOS.items()
    ]
    return render(request, 'simulation/what_if.html', {
        'page_title': 'What-If Simulation Engine — Ramonet',
        'scenarios': scenarios
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def api_run_what_if(request):
    """
    Executes a What-If failure or capacity scenario against an isolated copy of the topology.
    """
    try:
        data = request.data if isinstance(request.data, dict) else json.loads(request.body.decode('utf-8'))
    except Exception:
        return Response({'success': False, 'error': 'Invalid JSON'}, status=400)

    scenario_key = str(data.get('scenario_key', 'CORE_SWITCH_FAIL'))[:64]
    topology_data = data.get('topology', {})
    params = data.get('params', {})

    result = WhatIfEngine.evaluate_scenario(scenario_key, topology_data, params)
    return Response({'success': True, 'result': result})

