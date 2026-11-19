from django.shortcuts import render, get_object_or_404
from .models import LearningTopic

TOPIC_META = {
    'networking-fundamentals': {
        'scenario': 'Basic Home Network',
        'course_slug': 'intro-to-networking',
        'lesson_slug': 'osi-model-tcp-ip',
        'label': 'Intro to Networking Practical Lab'
    },
    'osi-7-layer-model': {
        'scenario': 'Basic Home Network',
        'course_slug': 'intro-to-networking',
        'lesson_slug': 'osi-model-tcp-ip',
        'label': 'OSI & Encapsulation Practical Lab'
    },
    'tcp-ip-suite': {
        'scenario': 'Basic Home Network',
        'course_slug': 'intro-to-networking',
        'lesson_slug': 'osi-model-tcp-ip',
        'label': 'TCP/IP Architecture Practical Lab'
    },
    'ethernet-mac-addressing': {
        'scenario': 'STP Loop Prevention',
        'course_slug': 'ethernet-cabling-devices',
        'lesson_slug': 'ethernet-cabling-types',
        'label': 'Ethernet Cabling & MAC Lab'
    },
    'ipv4-addressing-subnetting': {
        'scenario': 'Basic Home Network',
        'course_slug': 'intro-to-networking',
        'lesson_slug': 'ipv4-subnetting-mac',
        'label': 'IPv4 Subnetting & Addressing Lab'
    },
    'vlsm-subnet-planning': {
        'scenario': 'Basic Home Network',
        'course_slug': 'router-config-subnetting',
        'lesson_slug': 'router-interface-config',
        'label': 'VLSM Subnet Planning Lab'
    },
    'switching-mac-learning': {
        'scenario': 'STP Loop Prevention',
        'course_slug': 'switch-config-vlan',
        'lesson_slug': 'vlan-configuration-ports',
        'label': 'Switching & MAC Learning Lab'
    },
    'vlans-and-trunking': {
        'scenario': 'VLAN Segmentation',
        'course_slug': 'switch-config-vlan',
        'lesson_slug': 'vlan-configuration-ports',
        'label': 'VLAN & 802.1Q Trunking Lab'
    },
    'inter-vlan-routing': {
        'scenario': 'VLAN Segmentation',
        'course_slug': 'switch-config-vlan',
        'lesson_slug': 'vlan-configuration-ports',
        'label': 'Inter-VLAN Routing Lab'
    },
    'routing-protocols': {
        'scenario': 'OSPF Branch WAN',
        'course_slug': 'routing-protocols-static-dynamic',
        'lesson_slug': 'static-routing-default-routes',
        'label': 'Routing Protocols & OSPF Lab'
    },
    'firewalls-and-acls': {
        'scenario': 'Firewall DMZ',
        'course_slug': 'network-security-firewall',
        'lesson_slug': 'stateful-firewall-acl',
        'label': 'Firewall & Stateful ACL Lab'
    },
    'nat-and-pat': {
        'scenario': 'Firewall DMZ',
        'course_slug': 'network-security-firewall',
        'lesson_slug': 'stateful-firewall-acl',
        'label': 'NAT & PAT Translation Lab'
    },
    'dns-architecture': {
        'scenario': 'Basic Home Network',
        'course_slug': 'server-networking-windows-linux',
        'lesson_slug': 'dhcp-server-scopes-reservations',
        'label': 'DNS & Server Infrastructure Lab'
    },
    'dhcp-protocol': {
        'scenario': 'Basic Home Network',
        'course_slug': 'server-networking-windows-linux',
        'lesson_slug': 'dhcp-server-scopes-reservations',
        'label': 'DHCP Server & Scope Lab'
    },
    'wireless-networking': {
        'scenario': 'Wireless Multi-SSID',
        'course_slug': 'wireless-networking-ap',
        'lesson_slug': 'enterprise-ap-multi-ssid',
        'label': 'Enterprise Wireless & AP Lab'
    },
    'network-security': {
        'scenario': 'Firewall DMZ',
        'course_slug': 'network-security-firewall',
        'lesson_slug': 'stateful-firewall-acl',
        'label': 'Network Security Defense Lab'
    },
    'storage-networking': {
        'scenario': 'Enterprise Storage NAS',
        'course_slug': 'nas-san-storage-networking',
        'lesson_slug': 'nas-raid-smb-storage-subnets',
        'label': 'NAS, SAN & Storage Networking Lab'
    },
    'cctv-nvr-networking': {
        'scenario': 'CCTV PoE Surveillance',
        'course_slug': 'cctv-ipcamera-nvr-networking',
        'lesson_slug': 'cctv-poe-nvr-isolation',
        'label': 'CCTV, PoE & NVR Surveillance Lab'
    },
    'server-dmz-networking': {
        'scenario': 'Firewall DMZ',
        'course_slug': 'network-security-firewall',
        'lesson_slug': 'stateful-firewall-acl',
        'label': 'Server Infrastructure & DMZ Lab'
    },
    'network-troubleshooting': {
        'scenario': 'Basic Home Network',
        'course_slug': 'network-troubleshooting-diagnostics',
        'lesson_slug': 'systematic-fault-isolation',
        'label': 'Fault Isolation & Diagnostics Lab'
    }
}

def learning_center_view(request):
    """
    Ramonet Structured Learning Center Hub.
    """
    level = request.GET.get('level', '').strip()
    topics = LearningTopic.objects.all()

    if level:
        topics = topics.filter(level=level)

    context = {
        'topics': topics,
        'selected_level': level,
        'page_title': 'Learning Center',
    }
    return render(request, 'learning/center.html', context)

def topic_detail_view(request, slug):
    """
    Individual structured topic view with Simple/Technical explanations, diagrams, and exercises.
    """
    topic = get_object_or_404(LearningTopic, slug=slug)
    next_topic = LearningTopic.objects.filter(topic_number__gt=topic.topic_number).order_by('topic_number').first()
    prev_topic = LearningTopic.objects.filter(topic_number__lt=topic.topic_number).order_by('-topic_number').first()

    meta = TOPIC_META.get(slug, {
        'scenario': 'Basic Home Network',
        'course_slug': 'intro-to-networking',
        'lesson_slug': 'osi-model-tcp-ip',
        'label': 'Hands-on Practice Lab'
    })

    context = {
        'topic': topic,
        'next_topic': next_topic,
        'prev_topic': prev_topic,
        'scenario_name': meta['scenario'],
        'academy_course_slug': meta['course_slug'],
        'academy_lesson_slug': meta['lesson_slug'],
        'lab_label': meta['label'],
        'page_title': f"Topic {topic.topic_number}: {topic.title}",
    }
    return render(request, 'learning/topic_detail.html', context)
