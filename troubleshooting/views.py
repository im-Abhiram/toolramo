from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import TroubleshootingScenario
from simulation.engine import NetworkSimulationEngine

def lab_view(request):
    """
    Ramonet Troubleshooting Lab View.
    Displays Beginner, Intermediate, and Advanced fault scenarios.
    """
    scenarios = TroubleshootingScenario.objects.all()
    selected_code = request.GET.get('scenario', '').strip()
    active_scenario = scenarios.filter(code=selected_code).first() if selected_code else scenarios.first()

    context = {
        'scenarios': scenarios,
        'active_scenario': active_scenario,
        'page_title': 'Network Troubleshooting Lab',
    }
    return render(request, 'troubleshooting/lab.html', context)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_solution_api(request):
    """
    Verifies whether a student's troubleshooting edits successfully resolved the active scenario.
    Runs active simulation checks against the modified topology.
    """
    scenario_code = request.data.get('scenario_code')
    topology = request.data.get('topology', {})

    scenario = get_object_or_404(TroubleshootingScenario, code=scenario_code)
    rule = scenario.verification_rule or {}

    # Check rule type
    target_dev_id = rule.get('target_device')
    dev = None
    for d in topology.get('devices', []):
        if str(d.get('id', '')) == target_dev_id or d.get('name', '') == target_dev_id:
            dev = d
            break

    # If verification requires ping test
    if rule.get('test_ping_dest'):
        engine = NetworkSimulationEngine(topology)
        res = engine.simulate_packet(target_dev_id, rule.get('test_ping_dest'), protocol='ICMP')
        if res.get('success'):
            return Response({
                'resolved': True,
                'message': 'Verification Passed! Ping test succeeded and end-to-end connectivity is restored.',
                'root_cause': scenario.root_cause_explanation,
                'solution': scenario.recommended_solution
            })
        else:
            return Response({
                'resolved': False,
                'message': f"Verification Failed: Ping test dropped. Reason: {res.get('drop_reason')} - {res.get('details')}",
                'hints': scenario.hints
            })

    # If verification checks field value
    req_field = rule.get('required_field')
    expected_val = rule.get('expected_value')
    if req_field and dev:
        actual_val = dev.get(req_field)
        if actual_val == expected_val:
            return Response({
                'resolved': True,
                'message': f"Verification Passed! Field '{req_field}' is now correctly set to '{expected_val}'.",
                'root_cause': scenario.root_cause_explanation,
                'solution': scenario.recommended_solution
            })
        else:
            return Response({
                'resolved': False,
                'message': f"Verification Incomplete: {dev.get('name')} {req_field} is '{actual_val}', expected '{expected_val}'.",
                'hints': scenario.hints
            })

    # Default success fallback
    return Response({
        'resolved': True,
        'message': 'Verification test completed successfully!',
        'root_cause': scenario.root_cause_explanation,
        'solution': scenario.recommended_solution
    })


# ==============================================================================
# NETWORK INCIDENT RESPONSE SIMULATOR (Priority 10)
# ==============================================================================
from .incident_engine import IncidentResponseEngine
from audit.logger import SecurityLogger

def incident_simulator_view(request):
    """
    Renders the Defensive Network Incident Response Learning Environment.
    Simulates SOC alert triage, threat containment, eradication, and post-mortem reporting.
    """
    scenarios = [
        {'key': k, **v} for k, v in IncidentResponseEngine.SCENARIOS.items()
    ]
    return render(request, 'troubleshooting/incident_simulator.html', {
        'page_title': 'Network Incident Response Simulator — Ramonet',
        'scenarios': scenarios
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def api_incident_action(request):
    """
    Executes an incident response containment or remediation action.
    """
    try:
        data = request.data if isinstance(request.data, dict) else json.loads(request.body.decode('utf-8'))
    except Exception:
        return Response({'success': False, 'error': 'Invalid JSON'}, status=400)

    scenario_key = str(data.get('scenario_key', 'ROGUE_DHCP'))[:64]
    action = str(data.get('action', 'Quarantine Switchport'))[:128]

    res = IncidentResponseEngine.execute_containment(scenario_key, action)

    SecurityLogger.log_event(
        action='INCIDENT_RESPONSE_ACTION',
        module='troubleshooting',
        request=request,
        details={'scenario': scenario_key, 'action': action, 'incident_id': res['incident_report']['incident_id']}
    )

    return Response(res)

