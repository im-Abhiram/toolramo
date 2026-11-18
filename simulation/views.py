import json
import ipaddress
from django.shortcuts import render
from django.http import JsonResponse
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
