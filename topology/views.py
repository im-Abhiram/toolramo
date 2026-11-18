import json
from django.shortcuts import render
from django.http import JsonResponse
from devices.models import DeviceCategory, DeviceDefinition
from ramonet_core import DeviceRegistry, ConfigurationValidator
from audit.logger import SecurityLogger

def designer_view(request):
    """
    Ramonet Visual Network Topology Designer.
    Provides drag-and-drop canvas, device inspector, CLI terminal, and packet tracer.
    """
    categories = DeviceCategory.objects.prefetch_related('devices').all()
    context = {
        'categories': categories,
        'page_title': 'Network Designer',
    }
    return render(request, 'topology/designer.html', context)


def rack_designer_view(request):
    """
    Ramonet Physical Network Rack Designer.
    Multi-rack elevation layout planning, 12U/24U/42U support, front/rear view,
    power consumption monitoring, overlap detection, patch panel mapping,
    and logical-to-physical device integration.
    """
    rack_equip = DeviceDefinition.objects.filter(
        category__slug__in=['switches', 'routers', 'firewalls', 'servers', 'storage', 'cctv', 'infrastructure']
    ).select_related('category')

    context = {
        'page_title': 'Physical Network Rack Designer — Ramonet',
        'equipment_catalog': rack_equip,
    }
    return render(request, 'topology/rack_designer.html', context)


def api_validate_rack_layout(request):
    """
    Validates physical rack equipment placement for overlaps and calculates total power draw and BTU.
    Enforces strict integer bounds (1 to 52U) and device limits to prevent CPU/DoS exhaustion.
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

    devices = data.get('devices') or data.get('mounted_devices') or []
    if not isinstance(devices, list):
        return JsonResponse({'error': '"devices" must be a list'}, status=400)

    if len(devices) > 100:
        return JsonResponse({'error': 'Exceeded maximum device limit (100 units per rack).'}, status=400)

    # Safe parse of total_rack_u (min 1, max 52)
    try:
        raw_units = data.get('rack_units') if data.get('rack_units') is not None else data.get('total_rack_u', 42)
        total_rack_u = int(raw_units)
        if total_rack_u < 1 or total_rack_u > 52:
            return JsonResponse({'error': 'total_rack_u must be between 1 and 52 U.'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid rack_units format.'}, status=400)

    normalized = []
    total_watts = 0.0
    occupied_units_set = set()
    errors = []

    for idx, d in enumerate(devices):
        if not isinstance(d, dict):
            continue

        p = d.get('rack_placement', {}) if isinstance(d.get('rack_placement'), dict) else {}
        r_id = str(p.get('rack_id') or d.get('rack_id', 'rack_a'))[:32]

        try:
            raw_start = p.get('unit_start') if p.get('unit_start') is not None else d.get('start_u', 1)
            u_start = int(raw_start)
        except (ValueError, TypeError):
            u_start = 1

        try:
            raw_height = p.get('height_u') or d.get('size_u') or d.get('rack_units', 1)
            u_height = int(raw_height)
        except (ValueError, TypeError):
            u_height = 1

        try:
            w = float(d.get('power_watts', 0.0))
            w = max(0.0, min(50000.0, w))
        except (ValueError, TypeError):
            w = 0.0

        total_watts += w
        dev_name = str(d.get('device_name') or d.get('name', f'Device-{idx+1}'))[:64]

        # Enforce bounds
        if u_start < 1 or u_start > total_rack_u:
            errors.append(f"{dev_name}: Placement start unit {u_start} is out of bounds (1-{total_rack_u}U).")
            continue
        if u_height < 1 or u_height > total_rack_u:
            errors.append(f"{dev_name}: Unit height {u_height} is invalid (1-{total_rack_u}U).")
            continue
        if (u_start + u_height - 1) > total_rack_u:
            errors.append(f"{dev_name}: Equipment extends past top of rack (U{u_start} + {u_height}U > {total_rack_u}U).")
            continue

        normalized.append({
            'name': dev_name,
            'rack_placement': {
                'rack_id': r_id,
                'unit_start': u_start,
                'height_u': u_height
            }
        })

        for u in range(u_start, u_start + u_height):
            occupied_units_set.add(u)

    overlaps = ConfigurationValidator.validate_rack_placements(normalized)
    for o in overlaps:
        msg = o.get('message', 'Overlap detected')
        if msg not in errors:
            errors.append(msg)

    occupied_count = len(occupied_units_set)
    free_count = max(0, total_rack_u - occupied_count)
    btu_hr = round(total_watts * 3.412142, 1)

    return JsonResponse({
        'valid': len(errors) == 0,
        'overlaps': overlaps,
        'errors': errors,
        'occupied_u': occupied_count,
        'free_u': free_count,
        'total_watts': round(total_watts, 1),
        'total_btu_hr': btu_hr,
        'total_power_watts': round(total_watts, 1)
    })


# ==============================================================================
# INTELLIGENT CABLE AND PORT TRACING (Priority 8)
# ==============================================================================
from .cable_tracer import CableTracer

def cable_trace_view(request):
    """
    Renders the Intelligent Cable & Port Tracing Studio.
    Provides end-to-end hop inspection through patch panels, racks, and switches.
    """
    return render(request, 'topology/cable_trace.html', {
        'page_title': 'Intelligent Cable & Port Tracing — Ramonet'
    })


def api_trace_cable(request):
    """
    Performs end-to-end cable tracing between selected endpoints.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = {}

    src_dev = data.get('source_device') or {'name': 'Camera-North-Gate', 'category': 'Camera', 'vlan': 30, 'ip': '192.168.30.14'}
    src_port = str(data.get('source_port', 'eth0'))[:32]
    dst_dev = data.get('destination_device') or {'name': 'NVR-Master', 'category': 'Server', 'vlan': 30, 'ip': '192.168.30.5'}

    res = CableTracer.trace_path(src_dev, src_port, dst_dev)
    return JsonResponse({'success': True, 'trace': res})

