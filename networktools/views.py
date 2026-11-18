import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def toolbox_view(request):
    """
    Ramonet 20-in-1 Network Engineering Toolbox & Calculators.
    """
    return render(request, 'networktools/toolbox.html', {
        'page_title': 'Network Engineering Toolbox — Ramonet'
    })


def discovery_view(request):
    """
    Simulated Network Discovery & Device Inventory Hub.
    Runs simulated Link Layer Discovery Protocol (LLDP), Cisco Discovery Protocol (CDP),
    and Address Resolution Protocol (ARP) scans to identify adjacent neighbors,
    chassis IDs, remote ports, and unmanaged rogue nodes.
    """
    return render(request, 'networktools/discovery.html', {
        'page_title': 'Network Discovery & Inventory — Ramonet'
    })


@csrf_exempt
def api_run_discovery(request):
    """
    Executes simulated LLDP / CDP neighbor polling and ARP table resolution.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = {}

    protocol = data.get('protocol', 'lldp').lower()

    # Pre-calculated realistic topology discovery table
    lldp_neighbors = [
        {
            'local_interface': 'GigabitEthernet1/0/1',
            'chassis_id': '00:1a:2b:3c:4d:5e',
            'system_name': 'Edge-Router-01',
            'port_id': 'GigabitEthernet0/1',
            'system_description': 'Cisco IOS Software, ISR4331/K9',
            'management_ip': '192.168.1.1',
            'vlan': 1,
            'capabilities': 'Router'
        },
        {
            'local_interface': 'GigabitEthernet1/0/20',
            'chassis_id': '70:69:79:88:99:aa',
            'system_name': 'Corp-Firewall-01',
            'port_id': 'wan1',
            'system_description': 'Fortinet FortiGate 60F v7.2.4',
            'management_ip': '192.168.1.2',
            'vlan': 1,
            'capabilities': 'Firewall / Bridge'
        },
        {
            'local_interface': 'TenGigabit1/1/1',
            'chassis_id': 'cc:d5:39:10:20:30',
            'system_name': 'Access-Switch-Floor2',
            'port_id': 'TenGigabit0/1',
            'system_description': 'Cisco Catalyst 2960X-48TD-L',
            'management_ip': '192.168.1.12',
            'vlan': 1,
            'capabilities': 'Bridge (Switch)'
        },
        {
            'local_interface': 'GigabitEthernet1/0/38',
            'chassis_id': '00:09:0f:aa:bb:cc',
            'system_name': 'Cisco-AP-9120AX',
            'port_id': 'Eth0',
            'system_description': 'Cisco Catalyst 9120AXI Series Access Point',
            'management_ip': '192.168.1.55',
            'vlan': 1,
            'capabilities': 'WLAN AP'
        }
    ]

    arp_cache = [
        {'ip': '192.168.1.1', 'mac': '00:1a:2b:3c:4d:5e', 'interface': 'Vlan1', 'type': 'Dynamic', 'age_min': 4},
        {'ip': '192.168.1.2', 'mac': '70:69:79:88:99:aa', 'interface': 'Vlan1', 'type': 'Dynamic', 'age_min': 2},
        {'ip': '192.168.1.12', 'mac': 'cc:d5:39:10:20:30', 'interface': 'Vlan1', 'type': 'Dynamic', 'age_min': 15},
        {'ip': '192.168.1.55', 'mac': '00:09:0f:aa:bb:cc', 'interface': 'Vlan1', 'type': 'Dynamic', 'age_min': 8},
        {'ip': '192.168.1.199', 'mac': '48:2a:e3:11:22:33', 'interface': 'Vlan1', 'type': 'Dynamic (Rogue?)', 'age_min': 1}
    ]

    return JsonResponse({
        'protocol': protocol.upper(),
        'scan_status': 'Completed',
        'discovered_devices_count': len(lldp_neighbors),
        'neighbors': lldp_neighbors,
        'arp_table': arp_cache,
        'rogue_devices_detected': 1,
        'rogue_details': [
            {'ip': '192.168.1.199', 'mac': '48:2a:e3:11:22:33', 'port': 'Gig1/0/14', 'warning': 'Unrecognized MAC vendor: Unauthorized personal device connected to switchport Gig1/0/14'}
        ]
    })


# ==============================================================================
# NETWORK CAPACITY AND COST PLANNER (Priority 9)
# ==============================================================================
from .capacity_cost_planner import CapacityCostPlanner

def capacity_cost_view(request):
    """
    Renders the Infrastructure Capacity & Budgetary Cost Planner.
    Calculates switch port density, PoE budgets, rack units, thermal dissipation, and Bill of Materials.
    """
    default_plan = CapacityCostPlanner.calculate_plan({})
    return render(request, 'networktools/capacity_cost.html', {
        'page_title': 'Capacity & Cost Planner — Ramonet',
        'default_plan': default_plan
    })


def api_calculate_capacity_cost(request):
    """
    Recalculates infrastructure capacity and budgetary BOM based on input parameters.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = {}

    plan = CapacityCostPlanner.calculate_plan(data)
    return JsonResponse({'success': True, 'plan': plan})

