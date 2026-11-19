from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import CommandEntry
from .cli_engine import DeviceCLISession

def command_library_view(request):
    """
    Searchable Command Reference Library view.
    """
    platform = request.GET.get('platform', '').strip()
    category = request.GET.get('category', '').strip()
    q = request.GET.get('q', '').strip()

    commands = CommandEntry.objects.all()

    if platform:
        commands = commands.filter(platform=platform)
    if category:
        commands = commands.filter(category=category)
    if q:
        commands = commands.filter(name__icontains=q) | commands.filter(syntax__icontains=q) | commands.filter(description__icontains=q)

    platforms = CommandEntry.PLATFORM_CHOICES
    categories = CommandEntry.CATEGORY_CHOICES

    context = {
        'commands': commands,
        'platforms': platforms,
        'categories': categories,
        'selected_platform': platform,
        'selected_category': category,
        'search_query': q,
        'page_title': 'Command Reference Library',
    }
    return render(request, 'commands/library.html', context)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def execute_command_api(request):
    """
    Executes a command against a simulated device's state using the CLI session engine.
    Mutates device configuration in real-time and returns updated prompt and terminal output.
    Preserves interactive session modes across multi-command sequences.
    """
    try:
        cmd = request.data.get('command', '')
        dev_data = request.data.get('device', {})
        topology_data = request.data.get('topology', {})
        session_state = request.data.get('session_state', {})

        session = DeviceCLISession(dev_data, topology_data, session_state=session_state)
        result = session.execute(cmd)
        return Response(result)
    except Exception as exc:
        return Response({
            'output': f"% Execution error: {str(exc)}",
            'prompt': 'Device> ',
            'mode': 'user_exec',
            'session_state': {'mode': 'user_exec'},
            'device': dev_data if 'dev_data' in locals() else {}
        })
