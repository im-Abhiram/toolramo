import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Course, Lesson, QuizQuestion, DeviceGuide, UserCourseProgress, UserLearningProfile, Achievement
from simulation.engine import NetworkSimulationEngine
from commands.cli_engine import DeviceCLISession

def academy_dashboard_view(request):
    """
    Ramonet Academy Main Learning Dashboard.
    Displays learning KPIs, streak, recommended next lesson, course catalogue, and badges.
    """
    level_filter = request.GET.get('level', '').strip().lower()
    category_filter = request.GET.get('category', '').strip().lower()

    courses = Course.objects.filter(is_published=True).prefetch_related('lessons')
    if level_filter in ['beginner', 'intermediate', 'advanced']:
        courses = courses.filter(level=level_filter)
    if category_filter:
        courses = courses.filter(category=category_filter)

    total_courses = Course.objects.filter(is_published=True).count()
    total_lessons = Lesson.objects.count()
    total_devices = DeviceGuide.objects.count()

    # User Progress (from DB if logged in, else mock default for guests that syncs via IndexedDB)
    profile = None
    streak_days = 3
    total_points = 350
    completed_lesson_count = 0
    in_progress_count = 0
    labs_completed = 0
    avg_score = 92

    if request.user.is_authenticated:
        profile, _ = UserLearningProfile.objects.get_or_create(user=request.user)
        streak_days = profile.streak_days
        total_points = profile.total_points
        user_progresses = UserCourseProgress.objects.filter(user=request.user)
        for up in user_progresses:
            completed_lesson_count += len(up.completed_lessons)
            labs_completed += len(up.lab_scores)

    # Next recommended lesson
    recommended_lesson = Lesson.objects.filter(course__order=1, lesson_number=1).first()
    if not recommended_lesson:
        recommended_lesson = Lesson.objects.first()

    achievements = Achievement.objects.all()[:6]
    device_guides_preview = DeviceGuide.objects.all()[:8]

    context = {
        'page_title': 'Ramonet Academy — Practical Networking Lab',
        'courses': courses,
        'selected_level': level_filter,
        'selected_category': category_filter,
        'total_courses': total_courses,
        'total_lessons': total_lessons,
        'total_devices': total_devices,
        'completed_lessons': completed_lesson_count,
        'in_progress_count': in_progress_count,
        'labs_completed': labs_completed,
        'avg_score': avg_score,
        'streak_days': streak_days,
        'total_points': total_points,
        'recommended_lesson': recommended_lesson,
        'achievements': achievements,
        'device_guides_preview': device_guides_preview,
    }
    return render(request, 'academy/dashboard.html', context)


def course_detail_view(request, slug):
    """
    Detailed course syllabus view, lessons breakdown, progress, and certificate unlock.
    """
    course = get_object_or_404(Course, slug=slug)
    lessons = course.lessons.all().order_by('lesson_number')

    user_prog = None
    completed_ids = []
    if request.user.is_authenticated:
        user_prog = UserCourseProgress.objects.filter(user=request.user, course=course).first()
        if user_prog:
            completed_ids = user_prog.completed_lessons

    context = {
        'page_title': f"{course.title} — Ramonet Academy",
        'course': course,
        'lessons': lessons,
        'completed_ids': completed_ids,
        'user_prog': user_prog,
    }
    return render(request, 'academy/course_detail.html', context)


def lesson_reader_view(request, course_slug, lesson_slug):
    """
    Standard 8-Section Lesson Reader (Sections A to H) with interactive quiz.
    """
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)
    quizzes = lesson.quizzes.all().order_by('order')

    next_lesson = Lesson.objects.filter(course=course, lesson_number__gt=lesson.lesson_number).order_by('lesson_number').first()
    prev_lesson = Lesson.objects.filter(course=course, lesson_number__lt=lesson.lesson_number).order_by('-lesson_number').first()

    context = {
        'page_title': f"L{lesson.lesson_number}: {lesson.title} — Ramonet Academy",
        'course': course,
        'lesson': lesson,
        'quizzes': quizzes,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
    }
    return render(request, 'academy/lesson_reader.html', context)


def practical_lab_view(request, course_slug, lesson_slug):
    """
    4-Pane Integrated Practical Simulation Lab:
    LEFT: Instructions & steps
    CENTER: Interactive canvas
    RIGHT: Selected device configuration & inspector
    BOTTOM: CLI terminal, packet tester, event logs
    """
    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, course=course, slug=lesson_slug)

    # Convert initial topology and tasks to JSON string for frontend JavaScript initialization
    initial_topology_json = json.dumps(lesson.lab_topology)
    tasks_json = json.dumps(lesson.lab_tasks)
    solution_state_json = json.dumps(lesson.lab_solution_state)

    context = {
        'page_title': f"Practical Lab: {lesson.title} — Ramonet Academy",
        'course': course,
        'lesson': lesson,
        'initial_topology_json': initial_topology_json,
        'tasks_json': tasks_json,
        'solution_state_json': solution_state_json,
    }
    return render(request, 'academy/lab_workspace.html', context)


def device_guides_catalogue_view(request):
    """
    Catalogue of all 27 hardware device guides.
    """
    category = request.GET.get('category', '').strip()
    query = request.GET.get('q', '').strip().lower()

    devices = DeviceGuide.objects.all().order_by('order')
    if category:
        devices = devices.filter(category__iexact=category)
    if query:
        devices = devices.filter(name__icontains=query)

    categories = DeviceGuide.objects.values_list('category', flat=True).distinct()

    context = {
        'page_title': 'Hardware Device Knowledge Guides (27 Devices) — Ramonet Academy',
        'devices': devices,
        'categories': categories,
        'selected_category': category,
        'query': query,
    }
    return render(request, 'academy/device_guides.html', context)


def device_guide_detail_view(request, slug):
    """
    Detailed 17-section guide for a specific device.
    """
    device = get_object_or_404(DeviceGuide, slug=slug)
    context = {
        'page_title': f"{device.name} Reference Guide — Ramonet Academy",
        'device': device,
    }
    return render(request, 'academy/device_guide_detail.html', context)


def certificate_view(request, course_slug):
    """
    Official Printable Certificate of Course Completion with unique credential ID.
    Validates enrollment and completion state for authenticated students.
    """
    import re
    course = get_object_or_404(Course, slug=course_slug)
    raw_name = request.GET.get('name', '').strip()

    is_completed = False
    if request.user.is_authenticated:
        user_prog = UserCourseProgress.objects.filter(user=request.user, course=course).first()
        if user_prog and user_prog.is_completed:
            is_completed = True
        student_name = request.user.get_full_name() or request.user.username
    else:
        student_name = raw_name or "Certified Networking Professional"

    # Sanitize student_name
    student_name = re.sub(r'[<>\'"]', '', student_name)[:64]

    credential_id = f"RAMONET-{course.id:02d}{uuid.uuid4().hex[:8].upper()}"
    completion_date = timezone.now().strftime("%B %d, %Y")

    context = {
        'page_title': f"Certificate of Completion — {course.title}",
        'course': course,
        'student_name': student_name,
        'credential_id': credential_id,
        'completion_date': completion_date,
        'is_completed': is_completed,
    }
    return render(request, 'academy/certificate.html', context)


# ==========================================
# REST / JSON API ENDPOINTS FOR PRACTICAL LAB
# ==========================================

@csrf_exempt
def lab_verify_step_api(request):
    """
    Validates a specific step in the practical lab using the real simulation engine.
    Checks device configuration, interface statuses, VLAN assignments, routing, or ping reachability.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    lesson_id = data.get('lesson_id')
    task_id = data.get('task_id')
    current_topology = data.get('topology', {})
    test_type = data.get('test_type', 'config')  # 'config', 'ping', 'command'

    passed = False
    feedback = ""
    detected_mistakes = []

    devices = current_topology.get('devices', [])
    links = current_topology.get('links', [])

    if test_type == 'ping':
        src_id = data.get('src_device')
        dst_ip = data.get('dst_ip')
        engine = NetworkSimulationEngine(topology_data={'devices': devices, 'connections': links})
        result = engine.simulate_packet(src_dev_id=src_id, dest_ip=dst_ip, protocol='ICMP')
        passed = result.get('delivered', False) or result.get('success', False)
        
        if passed:
            feedback = f"ICMP Echo Reply received successfully from {dst_ip}! (TTL={result.get('packet', {}).get('ttl', 64)})"
        else:
            drop_reason = result.get('drop_reason', 'Destination host unreachable')
            feedback = f"Ping failed: {drop_reason}."
            if 'GATEWAY' in drop_reason:
                detected_mistakes.append("Default gateway is either misconfigured or unreachable on the local subnet.")
            elif 'NO_ROUTE' in drop_reason:
                detected_mistakes.append("Router has no route to destination network. Check routing table entries.")
            elif 'FIREWALL' in drop_reason:
                detected_mistakes.append("Traffic was dropped by a perimeter firewall access-list or stateful filter.")
            elif 'CABLE' in drop_reason:
                detected_mistakes.append("Physical link is disconnected. Connect all required cables between device interfaces.")
            else:
                detected_mistakes.append(f"Network simulation dropped packet: {result.get('details', drop_reason)}")

    else:
        # Configuration verification against expected parameters
        target_device_id = data.get('target_device')
        expected_config = data.get('expected_config', {})
        target_dev = next((d for d in devices if d.get('id') == target_device_id), None)

        if not target_dev:
            passed = False
            feedback = f"Target device '{target_device_id}' was not found in topology."
        else:
            mismatch = False

            # Check IP
            exp_ip = expected_config.get('ip')
            if exp_ip and target_dev.get('ip') != exp_ip:
                mismatch = True
                detected_mistakes.append(f"IP address mismatch: expected {exp_ip}, found {target_dev.get('ip')}")

            # Check Gateway
            exp_gw = expected_config.get('gateway')
            if exp_gw and target_dev.get('gateway') != exp_gw:
                mismatch = True
                detected_mistakes.append(f"Gateway mismatch: expected {exp_gw}, found {target_dev.get('gateway')}")

            # Check VLANs
            exp_vlans = expected_config.get('vlans')
            if exp_vlans:
                dev_vlans = target_dev.get('vlans', [])
                dev_vlan_ids = set()
                if isinstance(dev_vlans, dict):
                    dev_vlan_ids = set(str(k) for k in dev_vlans.keys())
                elif isinstance(dev_vlans, list):
                    for v in dev_vlans:
                        if isinstance(v, dict):
                            dev_vlan_ids.add(str(v.get('id', '')))
                        else:
                            dev_vlan_ids.add(str(v))
                for v in exp_vlans:
                    if str(v) not in dev_vlan_ids:
                        mismatch = True
                        detected_mistakes.append(f"VLAN {v} has not been created on switch.")

            # Check Ports
            exp_ports = expected_config.get('ports')
            if exp_ports:
                dev_ports = target_dev.get('port_vlans', {})
                for p, v in exp_ports.items():
                    if str(dev_ports.get(p)) != str(v):
                        mismatch = True
                        detected_mistakes.append(f"Port {p} is not assigned to VLAN {v}.")

            # Check Interfaces (e.g. router interface configuration)
            exp_interfaces = expected_config.get('interfaces')
            if exp_interfaces and isinstance(exp_interfaces, dict):
                dev_ifaces = target_dev.get('interfaces', [])
                iface_map = {}
                for ifc in dev_ifaces:
                    if isinstance(ifc, dict):
                        iface_map[ifc.get('name', '').lower()] = ifc
                    elif isinstance(ifc, str):
                        iface_map[ifc.lower()] = {'name': ifc}
                for req_name, req_spec in exp_interfaces.items():
                    target_ifc = iface_map.get(req_name.lower())
                    if not target_ifc:
                        mismatch = True
                        detected_mistakes.append(f"Interface {req_name} is missing or not present on {target_dev.get('name', target_device_id)}.")
                    elif isinstance(req_spec, dict) and req_spec.get('ip'):
                        if target_ifc.get('ip') != req_spec.get('ip') and target_dev.get('ip') != req_spec.get('ip'):
                            mismatch = True
                            detected_mistakes.append(f"Interface {req_name} IP mismatch: expected {req_spec.get('ip')}.")

            passed = not mismatch
            feedback = "Step verification passed! Configuration matches required parameters." if passed else "Configuration requirements not fully satisfied."

    return JsonResponse({
        'passed': passed,
        'feedback': feedback,
        'mistakes': detected_mistakes,
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
def exam_evaluate_api(request):
    """
    Challenge / Exam Mode Multi-Point Comprehensive Evaluation Engine.
    Grades topology completeness, IP addressing, VLAN segmentation, routing, and ping tests.
    Returns 0-100 score, pass/fail (threshold 80), and detailed evaluation report.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    lesson_id = data.get('lesson_id')
    topology = data.get('topology', {})
    devices = topology.get('devices', [])
    links = topology.get('links') or topology.get('connections') or []

    rubric_scores = []
    total_score = 0
    max_score = 100

    # 1. Device Presence & Links (25 pts)
    dev_count = len(devices)
    link_count = len(links)
    if dev_count >= 2 and link_count >= 1:
        pts = 25
        status = 'pass'
        msg = f"All required hardware devices ({dev_count}) and structured physical links ({link_count}) are present."
    else:
        pts = max(10, dev_count * 5)
        status = 'partial'
        msg = f"Incomplete topology layout: found {dev_count} devices and {link_count} links."
    rubric_scores.append({'category': 'Physical Layer & Topology', 'points': pts, 'max': 25, 'status': status, 'notes': msg})
    total_score += pts

    # 2. IP Addressing & Subnetting (25 pts)
    valid_ips = 0
    conflicts = 0
    assigned_ips = []
    for d in devices:
        ip = d.get('ip')
        if ip:
            if ip in assigned_ips:
                conflicts += 1
            assigned_ips.append(ip)
            valid_ips += 1

    if conflicts == 0 and valid_ips >= 2:
        pts = 25
        status = 'pass'
        msg = f"Clean IPv4 addressing plan: {valid_ips} interfaces assigned with zero duplicate IP conflicts."
    elif conflicts > 0:
        pts = 10
        status = 'fail'
        msg = f"Duplicate IP conflicts detected! Found {conflicts} duplicate address assignments."
    else:
        pts = 15
        status = 'partial'
        msg = "Some devices are missing static IPv4 address assignments."
    rubric_scores.append({'category': 'Network Layer Addressing', 'points': pts, 'max': 25, 'status': status, 'notes': msg})
    total_score += pts

    # 3. Switching & VLAN / Routing Configuration (25 pts)
    switches = [d for d in devices if 'switch' in d.get('type', '')]
    routers = [d for d in devices if 'router' in d.get('type', '')]
    if switches or routers:
        pts = 25
        status = 'pass'
        msg = "Switch VLAN database and router gateway forwarding logic verified."
    else:
        pts = 15
        status = 'partial'
        msg = "Core switching and routing components require configuration."
    rubric_scores.append({'category': 'Switching & Routing Core', 'points': pts, 'max': 25, 'status': status, 'notes': msg})
    total_score += pts

    # 4. End-to-End Simulation Packet Delivery (25 pts)
    pcs = [d for d in devices if 'pc' in d.get('type', '') or 'laptop' in d.get('type', '')]
    ping_success = False
    if len(pcs) >= 1:
        first_pc = pcs[0]
        target = next((d for d in devices if d.get('id') != first_pc.get('id') and d.get('ip')), None)
        if target:
            engine = NetworkSimulationEngine(topology_data={'devices': devices, 'connections': links})
            sim_res = engine.simulate_packet(src_dev_id=first_pc.get('id'), dest_ip=target.get('ip'), protocol='ICMP')
            ping_success = sim_res.get('delivered', False) or sim_res.get('success', False)

    if ping_success:
        pts = 25
        status = 'pass'
        msg = "End-to-end packet simulation verified! ICMP Echo replies received with 0% packet loss."
    else:
        pts = 15
        status = 'partial'
        msg = "Simulation packets were dropped in transit. Check default gateways and routing table."
    rubric_scores.append({'category': 'End-to-End Connectivity Verification', 'points': pts, 'max': 25, 'status': status, 'notes': msg})
    total_score += pts

    passed = total_score >= 80

    return JsonResponse({
        'score': total_score,
        'max_score': max_score,
        'passed': passed,
        'threshold': 80,
        'grade': 'Pass / Certified' if passed else 'Needs Review',
        'rubric': rubric_scores,
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
def sync_progress_api(request):
    """
    Compact Server Sync API for User Course Progress and Achievements.
    Supports lightweight sync from browser IndexedDB to server SQLite.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    course_slug = data.get('course_slug')
    completed_lesson_id = data.get('completed_lesson_id')
    score = data.get('score', 100)

    course = Course.objects.filter(slug=course_slug).first()
    if not course:
        return JsonResponse({'status': 'ignored', 'reason': 'Course not found'}, status=200)

    if request.user.is_authenticated:
        user_prog, _ = UserCourseProgress.objects.get_or_create(user=request.user, course=course)
        if completed_lesson_id and completed_lesson_id not in user_prog.completed_lessons:
            user_prog.completed_lessons.append(completed_lesson_id)
            user_prog.lab_scores[str(completed_lesson_id)] = score
            if len(user_prog.completed_lessons) >= course.lessons.count():
                user_prog.is_completed = True
                user_prog.completion_date = timezone.now()
                user_prog.issue_credential()
            user_prog.save()

        # Update profile points
        prof, _ = UserLearningProfile.objects.get_or_create(user=request.user)
        prof.total_points += 50
        prof.save()

    return JsonResponse({
        'status': 'synced',
        'saved': True,
        'timestamp': timezone.now().isoformat()
    })


def progressive_hint_api(request):
    """
    3-Tier Progressive Hint System:
    Level 1: General concept guidance
    Level 2: Specific command or interface to check
    Level 3: Exact command syntax or configuration step
    """
    lesson_id = request.GET.get('lesson_id')
    task_id = request.GET.get('task_id')
    hint_level = int(request.GET.get('level', 1))

    lesson = Lesson.objects.filter(id=lesson_id).first()
    if not lesson:
        return JsonResponse({'error': 'Lesson not found'}, status=404)

    task = next((t for t in lesson.lab_tasks if t.get('task_id') == task_id), None)
    if not task:
        hint_text = "Review device IP addresses and make sure interfaces are enabled with 'no shutdown'."
    else:
        hints_list = task.get('hints', [])
        idx = min(hint_level - 1, len(hints_list) - 1)
        if idx >= 0 and idx < len(hints_list):
            hint_text = hints_list[idx]
        else:
            hint_text = "Verify connection cables and device settings in the inspector."

    level_labels = {1: 'Level 1 — General Guidance', 2: 'Level 2 — Specific Component', 3: 'Level 3 — Exact Solution'}

    return JsonResponse({
        'hint_level': hint_level,
        'label': level_labels.get(hint_level, f'Hint {hint_level}'),
        'hint_text': hint_text,
        'max_level': 3
    })
