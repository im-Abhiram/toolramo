import json
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from audit.logger import SecurityLogger
from .models import KnowledgeArticle, ConnectionRule
from commands.models import CommandEntry
from .ai_service import (
    MAX_MESSAGE_LENGTH,
    ai_chat_rate_limiter,
    ask_gemini_assistant,
)

@api_view(['GET'])
@permission_classes([AllowAny])
def device_guide_api(request):
    """
    Returns 15-section architectural learning guide for a given device type or category.
    """
    device_type = request.GET.get('device_type', '').lower()
    
    # Check if article exists
    article = KnowledgeArticle.objects.filter(device_type__icontains=device_type).first()
    if article and article.structured_guide:
        return Response({'guide': article.structured_guide, 'title': article.title})
        
    # Return structured fallback guide
    guide_data = {
        'section1': f'{device_type.replace("_", " ").title()} is a dedicated networking appliance operating in modern enterprise network infrastructures.',
        'section2': 'Inspects, translates, filters, or forwards digital communications using standardized IEEE and IETF network protocols.',
        'section3': 'Essential to ensure high throughput, fault tolerance, subnet separation, and network security across distributed systems.',
        'section4': 'Deployed in corporate wiring closets, datacenter top-of-rack switches, DMZ perimeter edges, and branch offices.',
        'section5': 'Processes frames/packets using specialized ASICs and maintains in-memory CAM/ARP/routing tables for wire-speed forwarding.',
        'section6': 'Connects via Category 6/6A RJ45 copper, OM3/OM4 LC-LC fiber optic patch cords, or 802.11 Wi-Fi airwaves.',
        'section7': 'Equipped with 10/100/1000 Mbps GigabitEthernet ports, 10G SFP+ optical slots, and optional PoE+ power sourcing ports.',
        'section8': 'Requires IP configuration (address, netmask, default gateway, DNS), administrative credentials, and VLAN/routing definitions.',
        'section9': 'Supports IPv4, IPv6, 802.1Q VLANs, STP/RSTP, OSPF, NAT, DHCP, DNS, and SNMP.',
        'section10': 'Supported commands include "show ip interface brief", "show ip route", "show running-config", "ping", and "traceroute".',
        'section11': 'Verify proper operation by testing ICMP Echo Requests (ping) and reviewing interface status counters.',
        'section12': 'Common failures include cabling disconnects, port shutdown states, subnet mask mismatches, and firewall deny policies.',
        'section13': 'Methodical troubleshooting begins at Layer 1 (cabling/LEDs) through Layer 2 (MAC/VLANs) and Layer 3 (IP/Gateways).',
        'section14': 'Disable unused switch ports, configure encrypted SSH/HTTPS management, and isolate management access to dedicated VLANs.',
        'section15': 'Real-world deployment includes connecting workstations, access points, surveillance cameras, and upstream edge routers.'
    }
    return Response({'guide': guide_data, 'title': device_type.title()})

@api_view(['GET'])
@permission_classes([AllowAny])
def how_to_connect_api(request):
    """
    Returns compatibility analysis and step-by-step connection instructions for two device categories.
    """
    src = request.GET.get('src', '').strip()
    target = request.GET.get('target', '').strip()

    # Query rule in either order
    rule = ConnectionRule.objects.filter(source_category=src, target_category=target).first()
    if not rule:
        rule = ConnectionRule.objects.filter(source_category=target, target_category=src).first()

    if rule:
        return Response({
            'source_category': rule.source_category,
            'target_category': rule.target_category,
            'is_supported': rule.is_supported,
            'recommended_cable': rule.recommended_cable,
            'alternative_cables': rule.alternative_cables,
            'required_ports': rule.required_ports,
            'power_requirements': rule.power_requirements,
            'step_by_step_instructions': rule.step_by_step_instructions,
            'verification_commands': rule.verification_commands,
            'troubleshooting_tips': rule.troubleshooting_tips
        })

    # Default fallback rule
    return Response({
        'source_category': src,
        'target_category': target,
        'is_supported': True,
        'recommended_cable': 'Copper Straight-Through (Cat6 RJ45)',
        'required_ports': 'GigabitEthernet 1000BASE-T RJ45',
        'power_requirements': 'Standard AC power supplies required for both devices.',
        'step_by_step_instructions': [
            f'Locate an available RJ45 Ethernet port on the {src}.',
            f'Plug one end of a Cat6 patch cable into the {src}.',
            f'Plug the opposite end into an available port on the {dest_category if (dest_category := target) else "destination"}.',
            'Verify that physical link LEDs illuminate green on both ports.',
            'Assign IP addresses in the same subnet mask or configure DHCP.',
            'Execute "ping" to verify network layer communication.'
        ],
        'verification_commands': ['show ip interface brief', 'ping <target_ip>'],
        'troubleshooting_tips': ['If link LED is off, check that the port is not administratively shut down.']
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def search_api(request):
    """
    Global instant search API across commands, devices, and knowledgebase articles.
    """
    q = request.GET.get('q', '').strip()
    if not q or len(q) < 2:
        return Response([])

    results = []

    # Search Commands
    cmd_matches = CommandEntry.objects.filter(name__icontains=q) | CommandEntry.objects.filter(description__icontains=q) | CommandEntry.objects.filter(syntax__icontains=q)
    for c in cmd_matches[:6]:
        results.append({
            'type': 'command',
            'id': c.id,
            'title': c.name,
            'syntax': c.syntax,
            'category': c.get_category_display(),
            'platform': c.get_platform_display(),
            'summary': c.description[:100] + '...' if len(c.description) > 100 else c.description
        })

    # Search Knowledge Articles
    kb_matches = KnowledgeArticle.objects.filter(title__icontains=q) | KnowledgeArticle.objects.filter(summary__icontains=q)
    for a in kb_matches[:6]:
        results.append({
            'type': 'article',
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'category': a.get_category_display(),
            'summary': a.summary[:100] + '...' if len(a.summary) > 100 else a.summary
        })

    return Response(results)


def ai_chat_api(request):
    """
    CSRF-protected JSON POST endpoint powering the global RAMONET AI Chatbot.
    Proxies validated questions to Gemini server-side while keeping the API key secret.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    if len(request.body) > 65536:
        return JsonResponse({'error': 'Payload exceeds 64 KB limit.'}, status=413)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({'error': 'Expected JSON object.'}, status=400)

    raw_message = data.get('message')
    if not isinstance(raw_message, str) or not raw_message.strip():
        return JsonResponse({'error': 'Please enter a non-empty message.'}, status=400)

    message = raw_message.strip()
    if len(message) > MAX_MESSAGE_LENGTH:
        return JsonResponse(
            {'error': f'Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters.'},
            status=400,
        )

    history = data.get('history', [])
    if history is not None and not isinstance(history, list):
        return JsonResponse({'error': '"history" must be a list.'}, status=400)

    page_context = data.get('context', {})
    if page_context is not None and not isinstance(page_context, dict):
        page_context = {}

    client_ip = SecurityLogger.get_client_ip(request) or '127.0.0.1'
    if request.user.is_authenticated:
        limiter_key = f"user:{request.user.id}:{client_ip}"
    else:
        limiter_key = f"ip:{client_ip}"

    allowed, retry_after = ai_chat_rate_limiter.allow_request(limiter_key)
    if not allowed:
        SecurityLogger.log_event(
            action='AI_CHAT_RATE_LIMIT',
            module='knowledgebase',
            request=request,
            details={'retry_after': retry_after},
            severity='warning',
        )
        return JsonResponse(
            {
                'error': f'Too many AI requests. Please wait {retry_after} seconds before sending another question.',
                'retry_after': retry_after,
            },
            status=429,
        )

    result = ask_gemini_assistant(
        message=message,
        history=history or [],
        page_context=page_context,
    )
    return JsonResponse(result, status=200)
