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


def subnet_calculator_view(request):
    """
    Dedicated high-traffic SEO landing page for IPv4 & IPv6 Subnet Calculator,
    CIDR prefix lookup, binary bit breakdown, and CCNA subnetting reference.
    """
    cidr_reference = [
        {'cidr': '/32', 'mask': '255.255.255.255', 'total': 1, 'usable': 1, 'desc': 'Host route / Loopback'},
        {'cidr': '/31', 'mask': '255.255.255.254', 'total': 2, 'usable': 2, 'desc': 'Point-to-point link (RFC 3021)'},
        {'cidr': '/30', 'mask': '255.255.255.252', 'total': 4, 'usable': 2, 'desc': 'Point-to-point WAN link'},
        {'cidr': '/29', 'mask': '255.255.255.248', 'total': 8, 'usable': 6, 'desc': 'Small branch / HA cluster'},
        {'cidr': '/28', 'mask': '255.255.255.240', 'total': 16, 'usable': 14, 'desc': 'Small office subnet'},
        {'cidr': '/27', 'mask': '255.255.255.224', 'total': 32, 'usable': 30, 'desc': 'Department / Server VLAN'},
        {'cidr': '/26', 'mask': '255.255.255.192', 'total': 64, 'usable': 62, 'desc': 'Medium enterprise VLAN'},
        {'cidr': '/25', 'mask': '255.255.255.128', 'total': 128, 'usable': 126, 'desc': 'Large departmental subnet'},
        {'cidr': '/24', 'mask': '255.255.255.0', 'total': 256, 'usable': 254, 'desc': 'Standard Class C LAN'},
        {'cidr': '/23', 'mask': '255.255.254.0', 'total': 512, 'usable': 510, 'desc': 'Expanded campus VLAN'},
        {'cidr': '/22', 'mask': '255.255.252.0', 'total': 1024, 'usable': 1022, 'desc': 'Dual-building access tier'},
        {'cidr': '/21', 'mask': '255.255.248.0', 'total': 2048, 'usable': 2046, 'desc': 'Large enterprise floor'},
        {'cidr': '/20', 'mask': '255.255.240.0', 'total': 4096, 'usable': 4094, 'desc': 'Campus aggregation block'},
        {'cidr': '/16', 'mask': '255.255.0.0', 'total': 65536, 'usable': 65534, 'desc': 'Standard Class B network'},
        {'cidr': '/8', 'mask': '255.0.0.0', 'total': 16777216, 'usable': 16777214, 'desc': 'Standard Class A network'},
    ]
    return render(request, 'networktools/subnet_calculator.html', {
        'page_title': 'Free Online Subnet Calculator & CIDR Cheat Sheet — Ramonet',
        'meta_description': 'Calculate IPv4 and IPv6 subnets instantly. Get network address, broadcast address, usable host IP range, 32-bit binary breakdown, and CCNA subnetting cheat sheet.',
        'meta_keywords': 'subnet calculator, cidr calculator, ip subnet calculator, free subnet calculator online, ccna subnetting, ipv4 subnetting, 32-bit binary subnet mask',
        'cidr_reference': cidr_reference
    })


def ports_cheatsheet_view(request):
    """
    Dedicated high-traffic SEO landing page for Common Network Ports Cheat Sheet,
    covering TCP/UDP protocols, default port assignments, security risks, and CCNA exam notes.
    """
    common_ports = [
        {'port': 20, 'proto': 'TCP', 'service': 'FTP Data', 'category': 'File Transfer', 'secure': False, 'desc': 'File Transfer Protocol data transfer channel'},
        {'port': 21, 'proto': 'TCP', 'service': 'FTP Control', 'category': 'File Transfer', 'secure': False, 'desc': 'File Transfer Protocol command control; cleartext credentials'},
        {'port': 22, 'proto': 'TCP', 'service': 'SSH / SFTP', 'category': 'Remote Access', 'secure': True, 'desc': 'Secure Shell encrypted remote administration and secure file copy'},
        {'port': 23, 'proto': 'TCP', 'service': 'Telnet', 'category': 'Remote Access', 'secure': False, 'desc': 'Legacy unencrypted terminal emulation; insecure and vulnerable to sniffing'},
        {'port': 25, 'proto': 'TCP', 'service': 'SMTP', 'category': 'Email', 'secure': False, 'desc': 'Simple Mail Transfer Protocol for inter-server mail relaying'},
        {'port': 53, 'proto': 'TCP/UDP', 'service': 'DNS', 'category': 'Core Infrastructure', 'secure': False, 'desc': 'Domain Name System name resolution (UDP for queries, TCP for zone transfers)'},
        {'port': 67, 'proto': 'UDP', 'service': 'DHCP Server', 'category': 'Core Infrastructure', 'secure': False, 'desc': 'Dynamic Host Configuration Protocol server broadcast listen port'},
        {'port': 68, 'proto': 'UDP', 'service': 'DHCP Client', 'category': 'Core Infrastructure', 'secure': False, 'desc': 'DHCP client listen port for DORA offer & ack responses'},
        {'port': 69, 'proto': 'UDP', 'service': 'TFTP', 'category': 'File Transfer', 'secure': False, 'desc': 'Trivial FTP used by routers/switches for fast IOS firmware loading'},
        {'port': 80, 'proto': 'TCP', 'service': 'HTTP', 'category': 'Web', 'secure': False, 'desc': 'Hypertext Transfer Protocol standard unencrypted web traffic'},
        {'port': 88, 'proto': 'TCP/UDP', 'service': 'Kerberos', 'category': 'Authentication', 'secure': True, 'desc': 'Windows Active Directory authentication ticket granting service'},
        {'port': 110, 'proto': 'TCP', 'service': 'POP3', 'category': 'Email', 'secure': False, 'desc': 'Post Office Protocol v3 client mailbox retrieval'},
        {'port': 123, 'proto': 'UDP', 'service': 'NTP', 'category': 'Core Infrastructure', 'secure': False, 'desc': 'Network Time Protocol clock synchronization for syslog & audit'},
        {'port': 143, 'proto': 'TCP', 'service': 'IMAP', 'category': 'Email', 'secure': False, 'desc': 'Internet Message Access Protocol client mailbox synchronization'},
        {'port': 161, 'proto': 'UDP', 'service': 'SNMP Agent', 'category': 'Monitoring', 'secure': False, 'desc': 'Simple Network Management Protocol agent query polling (v1, v2c, v3)'},
        {'port': 162, 'proto': 'UDP', 'service': 'SNMP Trap', 'category': 'Monitoring', 'secure': False, 'desc': 'SNMP asynchronous alert trap notification receiver'},
        {'port': 179, 'proto': 'TCP', 'service': 'BGP', 'category': 'Routing', 'secure': False, 'desc': 'Border Gateway Protocol peering session establishment'},
        {'port': 389, 'proto': 'TCP/UDP', 'service': 'LDAP', 'category': 'Authentication', 'secure': False, 'desc': 'Lightweight Directory Access Protocol query lookup'},
        {'port': 443, 'proto': 'TCP', 'service': 'HTTPS / TLS', 'category': 'Web', 'secure': True, 'desc': 'HTTP over TLS/SSL authenticated secure encrypted web traffic'},
        {'port': 445, 'proto': 'TCP', 'service': 'SMB / CIFS', 'category': 'File Sharing', 'secure': False, 'desc': 'Server Message Block Windows file and printer sharing'},
        {'port': 514, 'proto': 'UDP', 'service': 'Syslog', 'category': 'Monitoring', 'secure': False, 'desc': 'System logging daemon event notification stream'},
        {'port': 636, 'proto': 'TCP', 'service': 'LDAPS', 'category': 'Authentication', 'secure': True, 'desc': 'LDAP over TLS/SSL directory service connection'},
        {'port': 993, 'proto': 'TCP', 'service': 'IMAPS', 'category': 'Email', 'secure': True, 'desc': 'Encrypted IMAP over TLS/SSL'},
        {'port': 995, 'proto': 'TCP', 'service': 'POP3S', 'category': 'Email', 'secure': True, 'desc': 'Encrypted POP3 over TLS/SSL'},
        {'port': 1433, 'proto': 'TCP', 'service': 'MS SQL Server', 'category': 'Database', 'secure': False, 'desc': 'Microsoft SQL Server default listening port'},
        {'port': 1521, 'proto': 'TCP', 'service': 'Oracle DB', 'category': 'Database', 'secure': False, 'desc': 'Oracle Database listener'},
        {'port': 3306, 'proto': 'TCP', 'service': 'MySQL', 'category': 'Database', 'secure': False, 'desc': 'MySQL / MariaDB database server engine'},
        {'port': 3389, 'proto': 'TCP/UDP', 'service': 'RDP', 'category': 'Remote Access', 'secure': True, 'desc': 'Microsoft Remote Desktop Protocol GUI console access'},
        {'port': 5060, 'proto': 'TCP/UDP', 'service': 'SIP (VoIP)', 'category': 'Voice & Video', 'secure': False, 'desc': 'Session Initiation Protocol for VoIP call signaling'},
        {'port': 5432, 'proto': 'TCP', 'service': 'PostgreSQL', 'category': 'Database', 'secure': False, 'desc': 'PostgreSQL relational database server'},
        {'port': 8080, 'proto': 'TCP', 'service': 'HTTP Alternate', 'category': 'Web', 'secure': False, 'desc': 'Common proxy, application server, and dev server port'},
        {'port': 8443, 'proto': 'TCP', 'service': 'HTTPS Alternate', 'category': 'Web', 'secure': True, 'desc': 'Secure application portal or web management GUI'},
    ]
    return render(request, 'networktools/ports_cheatsheet.html', {
        'page_title': 'Common Network Ports Cheat Sheet (TCP/UDP) — Ramonet',
        'meta_description': 'Comprehensive reference guide and searchable cheat sheet of common TCP and UDP network ports, protocols, default services, security risks, and CCNA exam definitions.',
        'meta_keywords': 'common network ports, tcp udp ports cheat sheet, ccna ports reference, port 80 443 22 53, network port list, networking cheat sheet',
        'common_ports': common_ports
    })


def osi_model_view(request):
    """
    Dedicated high-traffic SEO landing page for OSI 7-Layer Model vs TCP/IP Protocol Suite,
    interactive protocol explorer, encapsulation visualizer, and exam study guide.
    """
    osi_layers = [
        {
            'number': 7,
            'name': 'Application Layer',
            'pdu': 'Data',
            'desc': 'Provides human-computer interaction, network services to end-user applications, and API interfaces.',
            'protocols': ['HTTP', 'HTTPS', 'DNS', 'DHCP', 'FTP', 'SSH', 'Telnet', 'SMTP', 'SNMP', 'BGP'],
            'devices': ['Endpoints, Firewalls (WAF), Proxies, Web Browsers'],
            'troubleshooting': 'Check DNS resolution, browser cache, authentication credentials, SSL/TLS certificates, API payloads.'
        },
        {
            'number': 6,
            'name': 'Presentation Layer',
            'pdu': 'Data',
            'desc': 'Formats, compresses, serializes, and encrypts/decrypts data so the application layer can interpret it.',
            'protocols': ['TLS / SSL', 'SSH encryption', 'ASCII', 'UTF-8', 'JPEG', 'MPEG', 'JSON', 'XML'],
            'devices': ['Encryption gateways, Operating System cryptographic submodules'],
            'troubleshooting': 'Check TLS cipher suite mismatch, certificate expiration, encoding format incompatibilities.'
        },
        {
            'number': 5,
            'name': 'Session Layer',
            'pdu': 'Data',
            'desc': 'Establishes, maintains, synchronizes, and terminates interactive sessions and dialogues between applications.',
            'protocols': ['NetBIOS', 'RPC', 'PPTP', 'NFS', 'SIP', 'SMB sessions'],
            'devices': ['Operating system session managers, Application servers'],
            'troubleshooting': 'Check session timeouts, state synchronization drops, keepalive disconnects.'
        },
        {
            'number': 4,
            'name': 'Transport Layer',
            'pdu': 'Segment (TCP) / Datagram (UDP)',
            'desc': 'Provides end-to-end communication, segmentation, port addressing, flow control (windowing), and error recovery (ACKs).',
            'protocols': ['TCP (Transmission Control Protocol)', 'UDP (User Datagram Protocol)', 'SCTP'],
            'devices': ['Layer 4 Firewalls, Load Balancers, Transport Sockets'],
            'troubleshooting': 'Check TCP SYN handshakes, RST resets, listening socket ports, window size exhaustion, UDP drops.'
        },
        {
            'number': 3,
            'name': 'Network Layer',
            'pdu': 'Packet',
            'desc': 'Provides logical addressing (IPv4/IPv6), path selection, routing decisions, and packet fragmentation.',
            'protocols': ['IPv4', 'IPv6', 'ICMP', 'IPsec', 'OSPF', 'EIGRP', 'RIP', 'NAT / PAT'],
            'devices': ['Routers, Layer 3 Switches, Gateways'],
            'troubleshooting': 'Check IP address/subnet mask misconfigurations, missing default gateway, routing table prefix routes, ICMP ping unreachable.'
        },
        {
            'number': 2,
            'name': 'Data Link Layer',
            'pdu': 'Frame',
            'desc': 'Provides node-to-node framing, physical MAC addressing, collision management, and error detection (FCS/CRC).',
            'protocols': ['Ethernet (IEEE 802.3)', 'Wi-Fi (802.11)', 'ARP', 'STP (802.1D/w)', 'VLAN (802.1Q)', 'PPP', 'LACP'],
            'devices': ['Layer 2 Switches, Bridges, Wireless Access Points, NICs'],
            'troubleshooting': 'Check VLAN port allocation, trunk native VLAN mismatch, MAC address flapping, STP loop blocking, duplex/speed mismatch.'
        },
        {
            'number': 1,
            'name': 'Physical Layer',
            'pdu': 'Bit',
            'desc': 'Transmits raw unstructured binary bitstreams over physical transmission mediums (copper, fiber optics, radio frequencies).',
            'protocols': ['1000BASE-T', '10GBASE-SR', 'RS-232', 'RJ-45', 'SFP / SFP+', 'Radio Waves', 'Fiber Optic light pulses'],
            'devices': ['Network cables (Cat6, Single-mode/Multi-mode fiber), Transceivers, Hubs, Repeaters, Patch Panels'],
            'troubleshooting': 'Check loose/damaged cables, link status LED lights, pinout crimping (T568A vs T568B), optical dB loss, power source.'
        },
    ]
    return render(request, 'networktools/osi_model.html', {
        'page_title': 'OSI 7 Layer Model vs TCP/IP Protocol Suite Guide — Ramonet',
        'meta_description': 'Interactive reference guide to the 7 layers of the OSI model and TCP/IP stack. Learn protocol data units (PDUs), protocols, hardware devices, and systematic troubleshooting.',
        'meta_keywords': 'osi model, 7 layers of osi model, osi vs tcp ip, networking layers, application transport network physical data link, ccna osi model',
        'osi_layers': osi_layers
    })


