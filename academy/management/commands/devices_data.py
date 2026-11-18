# devices_data.py
# Comprehensive reference data for 27 networking devices covering 17 standard sections

def make_device(*args):
    if len(args) == 24:
        device_type, name, slug, category, icon, summary, \
        intro, purpose, apps, appearance, interfaces, \
        connections, cables, power, ip_config, settings, \
        commands, cmd_expl, verification, mistakes, \
        troubleshooting, security, project, order = args
    elif len(args) == 23:
        device_type, name, slug, category, icon, summary, \
        intro, apps, appearance, interfaces, \
        connections, cables, power, ip_config, settings, \
        commands, cmd_expl, verification, mistakes, \
        troubleshooting, security, project, order = args
        purpose = f"Provides dedicated operational functions and high-reliability networking capabilities for {name} across enterprise infrastructures."
    else:
        raise ValueError(f"make_device received unexpected {len(args)} arguments")
    return {
        'device_type': device_type,
        'name': name,
        'slug': slug,
        'category': category,
        'icon': icon,
        'summary': summary,
        'section_1_intro': intro,
        'section_2_purpose': purpose,
        'section_3_applications': apps,
        'section_4_appearance_ports': appearance,
        'section_5_interfaces': interfaces,
        'section_6_connection_methods': connections,
        'section_7_cables': cables,
        'section_8_power_requirements': power,
        'section_9_ip_configuration': ip_config,
        'section_10_device_settings': settings,
        'section_11_commands': commands,
        'section_12_command_explanations': cmd_expl,
        'section_13_verification': verification,
        'section_14_common_mistakes': mistakes,
        'section_15_troubleshooting': troubleshooting,
        'section_16_security_practices': security,
        'section_17_practical_project': project,
        'order': order
    }

DEVICES_DATA = [
    make_device(
        'router', 'Enterprise Core & Edge Router', 'router', 'Routers', 'fa-route',
        'Layer 3 path determination, inter-network forwarding, NAT/PAT, and dynamic routing protocol convergence.',
        'A router is a specialized Layer 3 network hardware appliance designed to interconnect multiple logically and physically separate computer networks.',
        'Determines optimal forwarding paths for IP datagrams using Routing Information Bases (RIB) and Hardware Forwarding Information Bases (FIB).',
        'Branch office WAN connectivity, ISP border peering, campus core interconnection, MPLS/VPN termination.',
        '1U-3U rack-mount chassis with redundant power supplies, RJ45 Gigabit ports, SFP/SFP+ optical cages, auxiliary and RJ45/USB console ports.',
        'GigabitEthernet, 10GbE SFP+, Serial WAN interfaces, Loopback logical interfaces, 802.1Q sub-interfaces.',
        'Straight-through copper to switch uplinks, crossover/straight copper or optical fiber to peer routers, serial V.35 to legacy WAN.',
        'Cat6/6a UTP/STP for copper interfaces up to 100m; Single-Mode Fiber (SMF 9/125um) for long-haul WAN; Multi-Mode Fiber (MMF 50/125um) for datacenter interconnects.',
        'Dual redundant 100-240V AC or -48V DC power supplies, typically 60W to 350W depending on installed modules.',
        'Static IP or dynamic DHCP WAN assignment on physical interfaces; secondary IP addresses; sub-interface 802.1Q IP tagging.',
        'Hostnames, banners, domain names, SSH key generation, static routes, OSPF/BGP process IDs, NAT pools, access-lists.',
        [
            {'cmd': 'show ip interface brief', 'desc': 'Check interface IP and UP/UP state'},
            {'cmd': 'show ip route', 'desc': 'Display active routing table'},
            {'cmd': 'ip route <prefix> <mask> <next-hop>', 'desc': 'Define static route'},
            {'cmd': 'interface <name>\n ip address <ip> <mask>\n no shutdown', 'desc': 'Configure and enable interface'}
        ],
        [
            {'cmd': 'show ip route', 'explanation': 'Inspects the routing table to see connected (C), static (S), and dynamic OSPF (O) routes.'},
            {'cmd': 'no shutdown', 'explanation': 'Changes administrative interface state from shutdown to UP.'}
        ],
        'Verify interface state with "show ip interface brief", test reachability with "ping" and "traceroute", and verify route presence with "show ip route".',
        ['Leaving interfaces administratively down (forgetting no shutdown)', 'Incorrect subnet masks on point-to-point links', 'Missing return routes on remote routers'],
        [{'issue': 'Unreachable next hop', 'fix': 'Verify physical link is up and subnet matches next hop IP.'}],
        ['Disable unused interfaces', 'Enforce SSH v2 with 2048-bit RSA keys', 'Set strong secret passwords with service password-encryption'],
        {'title': 'Branch to HQ Routed Interconnect', 'summary': 'Configure dual routers with static routing and verify bidirectional ping across subnets.'},
        1
    ),
    make_device(
        'layer2_switch', 'Layer 2 Managed Access Switch', 'layer2-switch', 'Switches', 'fa-network-wired',
        'High-density Ethernet frame forwarding, MAC address learning, and 802.1Q VLAN broadcast domain segmentation.',
        'A Layer 2 switch forwards frames within a local area network based on destination MAC addresses stored in its Content Addressable Memory (CAM) table.',
        'Isolates collision domains, enforces VLAN membership, connects end-user devices, and runs Spanning Tree Protocol (STP) to prevent switching loops.',
        'Enterprise access closets, desktop aggregation, VoIP phone connections, wireless AP connections.',
        '1U 24-port or 48-port RJ45 faceplate with 2-4 SFP/SFP+ optical uplink ports and status LED matrix.',
        '10/100/1000BASE-T RJ45 ports, SFP/SFP+ 1G/10G uplink cages, RJ45 console port.',
        'Cat5e/Cat6 straight-through copper to PCs and printers; optical fiber or DAC copper twinax to distribution switches.',
        'Cat5e/6 UTP for access ports; Cat6a or OM3/OM4 fiber for 10Gb uplinks.',
        'Single or dual internal AC power supply (30W-150W non-PoE).',
        'Management SVI (Switch Virtual Interface) assigned on management VLAN (e.g. interface vlan 1 or vlan 99).',
        'VLAN creation, port access/trunk mode, STP PortFast, BPDU Guard, storm control, port security.',
        [
            {'cmd': 'show vlan brief', 'desc': 'Display active VLANs and assigned ports'},
            {'cmd': 'show mac address-table', 'desc': 'Display dynamically learned MAC addresses'},
            {'cmd': 'switchport mode access\n switchport access vlan <id>', 'desc': 'Assign access port VLAN'},
            {'cmd': 'switchport mode trunk', 'desc': 'Configure 802.1Q trunk port'}
        ],
        [
            {'cmd': 'show vlan brief', 'explanation': 'Lists all VLAN IDs, names, and which physical interfaces belong to each VLAN.'}
        ],
        'Run "show vlan brief" and "show interfaces switchport" to confirm port VLAN assignments.',
        ['Placing ports in the wrong VLAN', 'Native VLAN mismatch on trunk ports', 'Leaving unused ports open in default VLAN 1'],
        [{'issue': 'Traffic flooding', 'fix': 'Check for STP loop or CAM table exhaustion.'}],
        ['Enable BPDU guard on access ports', 'Configure Port Security with max MAC limits', 'Assign unused ports to an isolated blackhole VLAN'],
        {'title': 'VLAN Segmentation Lab', 'summary': 'Segment a 24-port switch into Sales (VLAN 10) and Engineering (VLAN 20).'},
        2
    ),
    make_device(
        'layer3_switch', 'Layer 3 Multilayer Core/Distribution Switch', 'layer3-switch', 'Switches', 'fa-diagram-project',
        'Wirespeed hardware routing via ASICs, Switch Virtual Interfaces (SVI), and routed switchports.',
        'A Layer 3 switch combines high-density Layer 2 switching with hardware-based Layer 3 IP routing powered by specialized ASICs.',
        'Performs inter-VLAN routing at line rate without bottlenecking through an external router ("router-on-a-stick").',
        'Enterprise campus distribution and core layers, server farm aggregation, high-throughput datacenter leaves.',
        '1U/2U rack unit with 24-48 multi-gigabit ports (1G/2.5G/10G) and 40G/100G QSFP uplinks.',
        '10G SFP+, 40G/100G QSFP28, routed physical interfaces ("no switchport"), Switch Virtual Interfaces (SVI).',
        'Fiber optic OM4/OS2 cables to access switches; DAC twinax cables to datacenter servers.',
        'Cat6a/Cat7 for copper; OM4 multimode or OS2 singlemode optical fiber.',
        'Dual hot-swappable AC power supplies, 250W-650W.',
        'IP addresses assigned to Switch Virtual Interfaces (interface Vlan 10) and routed switchports (no switchport).',
        '"ip routing" global command, OSPF/EIGRP/BGP dynamic routing, DHCP relay agents (ip helper-address).',
        [
            {'cmd': 'ip routing', 'desc': 'Enable Layer 3 IP routing engine'},
            {'cmd': 'interface Vlan 10\n ip address 192.168.10.1 255.255.255.0', 'desc': 'Configure SVI gateway'},
            {'cmd': 'no switchport\n ip address <ip> <mask>', 'desc': 'Convert switchport to routed port'}
        ],
        [
            {'cmd': 'ip routing', 'explanation': 'Crucial global command that activates the L3 packet forwarding ASIC.'}
        ],
        'Execute "show ip route" and ping endpoints across different VLAN SVIs.',
        ['Forgetting to issue "ip routing" globally', 'Creating SVI without activating corresponding VLAN in database'],
        [{'issue': 'No inter-VLAN routing', 'fix': 'Ensure "ip routing" is enabled and SVIs are up.'}],
        ['Disable unused SVIs', 'Apply ACLs at SVI ingress', 'Secure control plane with CoPP'],
        {'title': 'Inter-VLAN Core Routing', 'summary': 'Configure SVIs for VLAN 10 and 20 and route between them at wirespeed.'},
        3
    ),
    make_device(
        'managed_switch', 'Enterprise Managed Workgroup Switch', 'managed-switch', 'Switches', 'fa-sliders',
        'Configurable enterprise switch offering SNMP, SSH management, QoS traffic prioritization, and 802.1X authentication.',
        'A managed switch gives administrators complete granular control over traffic flow, security policies, and bandwidth management.',
        'Allows network visibility, remote troubleshooting, VLAN tagging, and prioritization of real-time voice and video packets.',
        'Mid-size offices, branch networks, financial branches, broadcast studios.',
        '1U chassis with 16 to 48 ports, status LEDs, and dedicated console port.',
        'RJ45 Fast/Gigabit ports, SFP combo ports, USB/RJ45 management console.',
        'Cat6 straight-through to workstations; SFP fiber to building backbone.',
        'Cat6 UTP solid copper.',
        'Internal AC supply, 50W-120W.',
        'Static management IP on dedicated admin VLAN.',
        'SNMP v3 community strings, Syslog server IP, NTP synchronization, QoS DSCP mapping.',
        [
            {'cmd': 'snmp-server community <string> RO', 'desc': 'Configure SNMP monitoring'},
            {'cmd': 'logging host <ip>', 'desc': 'Set remote Syslog server'}
        ],
        [
            {'cmd': 'logging host', 'explanation': 'Directs system log messages to a centralized monitoring server.'}
        ],
        'Verify SNMP polling with "show snmp" and verify remote management via SSH.',
        ['Leaving default management password active', 'Using insecure SNMPv1 with public community string'],
        [{'issue': 'Loss of management access', 'fix': 'Connect via physical console cable and verify management IP.'}],
        ['Enforce SSH only (disable Telnet and HTTP)', 'Implement 802.1X port authentication'],
        {'title': 'Managed Switch Provisioning', 'summary': 'Configure SSH, management VLAN, and SNMP monitoring.'},
        4
    ),
    make_device(
        'unmanaged_switch', 'Plug-and-Play Unmanaged Switch', 'unmanaged-switch', 'Switches', 'fa-cube',
        'Zero-configuration Layer 2 packet multiplier designed for simple desktop expansion without software management.',
        'An unmanaged switch is a fixed-configuration plug-and-play device that automatically forwards frames without any software UI.',
        'Expands network port count in small home offices, conference rooms, or temporary kiosks.',
        'Home offices, retail POS terminals, classrooms, temporary trade booths.',
        'Compact desktop metal or plastic housing with 5, 8, or 16 RJ45 ports and simple link/activity LEDs.',
        '5-16 10/100/1000 Mbps Auto-MDIX RJ45 ports.',
        'Direct connection to wall jacks, PCs, printers, and smart TVs.',
        'Cat5e or Cat6 straight-through or crossover (Auto-MDIX handles polarity).',
        'External 12V/5V DC wall power adapter, typically 5W-15W.',
        'None. Unmanaged switches have no IP address, no MAC address, and no management interface.',
        'None. Operates autonomously using hardware switching chips.',
        [],
        [],
        'Verify green link/activity LEDs illuminate when devices are connected.',
        ['Attempting to configure VLANs or STP (unsupported)', 'Creating network loops (causes catastrophic broadcast storms)'],
        [{'issue': 'Network lockup / storm', 'fix': 'Check for looped cables plugged into the same switch.'}],
        ['Physically secure device in locked enclosure to prevent unauthorized cable taps.'],
        {'title': 'Small Office Expansion', 'summary': 'Connect 4 workstations to an unmanaged switch linked to a router.'},
        5
    ),
    make_device(
        'firewall', 'Next-Generation Stateful Perimeter Firewall', 'firewall', 'Firewalls', 'fa-shield-halved',
        'Stateful packet inspection, deep packet inspection (DPI), IPS/IDS, NAT, and security zone enforcement.',
        'A firewall acts as a security gateway between trusted internal networks and untrusted external networks.',
        'Inspects stateful TCP/UDP sessions, blocks malicious payloads, enforces perimeter access control, and terminates remote VPN tunnels.',
        'Enterprise perimeter borders, cloud VPC gateways, datacenter DMZ perimeters.',
        '1U-2U rack appliance with dedicated management, WAN, LAN, and DMZ interfaces, plus crypto accelerator cards.',
        'Gigabit RJ45 interfaces, 10G SFP+ optical ports, dedicated out-of-band management port.',
        'WAN port to ISP modem/ONT; LAN port to core switch; DMZ port to public-facing servers.',
        'Cat6a shielded copper to WAN; fiber optic to core switch.',
        'Dual redundant AC power supplies, 100W-350W.',
        'Static public IP on Outside interface; private gateway IPs on Inside and DMZ interfaces.',
        'Security zones (Inside, Outside, DMZ), stateful inspection policies, NAT/PAT rules, IPS signatures.',
        [
            {'cmd': 'firewall rule add chain=FORWARD action=accept src=192.168.1.0/24 dst=0.0.0.0/0', 'desc': 'Permit outbound LAN traffic'},
            {'cmd': 'show firewall conntrack', 'desc': 'View active stateful connection table'}
        ],
        [
            {'cmd': 'show firewall conntrack', 'explanation': 'Displays active tracked sessions including protocol, IPs, ports, and state.'}
        ],
        'Verify rule hits in firewall logs and execute connection tests through zones.',
        ['Implicit deny dropping wanted traffic without a permit rule', 'Placing permit rules below catch-all drops'],
        [{'issue': 'Outbound connections failing', 'fix': 'Check NAT configuration and verify DNS inspection permits port 53.'}],
        ['Default deny all inbound unsolicited traffic', 'Keep IPS and antivirus signatures updated automatically'],
        {'title': 'Perimeter Firewall & DMZ Lab', 'summary': 'Configure security zones and inspect stateful TCP handshakes.'},
        6
    ),
    make_device(
        'wireless_ap', 'Enterprise Wi-Fi 6 Wireless Access Point', 'wireless-ap', 'Wireless Devices', 'fa-wifi',
        'Radio frequency 802.11ax transceiver bridging wireless mobile clients into the wired Ethernet infrastructure.',
        'Translates wireless 802.11 radio frames into 802.3 Ethernet frames across dual/tri-band frequencies.',
        'Provides seamless high-speed Wi-Fi roaming for laptops, tablets, smartphones, and IoT devices.',
        'Corporate office ceilings, university lecture halls, hotel corridors, warehouse logistics.',
        'Sleek white or grey low-profile ceiling/wall-mount saucer with internal MIMO antenna array and single/dual RJ45 PoE ports.',
        '1x or 2x 2.5GbE / 1GbE RJ45 PoE ports, Bluetooth Low Energy (BLE) beacon radio.',
        'Cat6/6a UTP cable to a PoE+ switch port (802.3at) configured as an 802.1Q trunk.',
        'Cat6/6a solid copper (supports both Gigabit data and 30W PoE power).',
        '802.3at PoE+ (15W-25W power draw). No separate power brick needed.',
        'Static management IP or DHCP reservation on native management VLAN.',
        'SSID names, VLAN tags, security (WPA2/WPA3 Enterprise), channel widths (20/40/80 MHz), transmit power levels.',
        [
            {'cmd': 'show wireless ap status', 'desc': 'Display radio and client association count'},
            {'cmd': 'wireless ssid add name="Corp" vlan=10', 'desc': 'Create mapped SSID'}
        ],
        [
            {'cmd': 'wireless ssid add', 'explanation': 'Binds an SSID to an 802.1Q VLAN so wireless clients drop onto the correct subnet.'}
        ],
        'Verify client association in AP table and ping wireless client from wired LAN.',
        ['Connecting AP to an access port instead of an 802.1Q trunk port', 'Overlapping 2.4GHz channels causing severe co-channel interference'],
        [{'issue': 'AP will not power on', 'fix': 'Ensure switch port has PoE enabled and switch budget is not exceeded.'}],
        ['Use WPA3-Enterprise with 802.1X RADIUS authentication', 'Enable Client Isolation on Guest networks'],
        {'title': 'Enterprise Dual-SSID Wi-Fi Deployment', 'summary': 'Deploy AP with Corporate (VLAN 10) and Guest (VLAN 30) SSIDs.'},
        7
    ),
    make_device(
        'wireless_controller', 'Centralized Wireless LAN Controller (WLC)', 'wireless-controller', 'Wireless Devices', 'fa-tower-broadcast',
        'Centralized management, CAPWAP tunneling, RF optimization, and seamless L2/L3 roaming for lightweight APs.',
        'A WLC provides centralized configuration, automated radio frequency (RF) management, and client roaming coordination.',
        'Manages hundreds of lightweight access points (LAP) from a single dashboard, eliminating per-AP configuration.',
        'University campuses, hospital health systems, large multi-building enterprise headquarters.',
        '1U rack appliance with redundant power supplies, multiple 10G SFP+ ports, and dedicated service management port.',
        'Dual 10GbE SFP+ distribution ports, 1GbE service port, console port.',
        'Redundant 10G optical fiber uplinks to campus core switches.',
        'OM4 multimode fiber (LC to LC).',
        'Dual hot-swappable AC power supplies, 150W-300W.',
        'Static IP on management interface; Dynamic interfaces mapped to user VLANs.',
        'WLAN profiles, CAPWAP discovery IP, RADIUS authentication servers, RRM (Radio Resource Management).',
        [
            {'cmd': 'show wlan summary', 'desc': 'List all configured wireless networks'},
            {'cmd': 'show ap summary', 'desc': 'Display all registered lightweight APs'}
        ],
        [
            {'cmd': 'show ap summary', 'explanation': 'Verifies all lightweight APs have joined the controller via CAPWAP tunnels.'}
        ],
        'Check that APs transition to Registered state and broadcast provisioned WLANs.',
        ['AP and WLC software version incompatibility', 'CAPWAP UDP ports 5246/5247 blocked by intermediate firewalls'],
        [{'issue': 'APs fail to join WLC', 'fix': 'Verify DHCP Option 43 is configured with the WLC IP address.'}],
        ['Enforce DTLS encryption on CAPWAP data tunnels', 'Implement rogue AP detection and containment'],
        {'title': 'WLC Centralized Campus Lab', 'summary': 'Provision lightweight APs via central controller and verify client roaming.'},
        8
    ),
    make_device(
        'pc_workstation', 'Desktop PC Workstation', 'pc-workstation', 'Computers & Endpoints', 'fa-desktop',
        'End-user desktop computer executing business applications, network productivity tools, and browser workloads.',
        'Acts as a client endpoint in client-server architecture, initiating TCP/IP communication and processing user workflows.',
        'Corporate office workstations, engineering CAD stations, call center desktops.',
        'Tower or Small Form Factor (SFF) chassis with rear RJ45 Ethernet port and optional Wi-Fi antennas.',
        'Integrated 1GbE / 2.5GbE RJ45 NIC, USB ports.',
        'Cat6 patch cable to office wall jack leading to floor patch panel.',
        'Cat5e or Cat6 UTP copper (up to 100m total run).',
        'Standard 110V/220V AC power supply, 200W-500W.',
        'Dynamic IP via DHCP or static IP (IP, subnet mask, default gateway, primary and secondary DNS).',
        'Computer name, workgroup/domain membership, DNS search suffix, host firewall profiles.',
        [
            {'cmd': 'ipconfig /all', 'desc': 'Display full TCP/IP and MAC configuration'},
            {'cmd': 'ping <target>', 'desc': 'Test Layer 3 ICMP reachability'},
            {'cmd': 'tracert <target>', 'desc': 'Trace route hops to remote destination'},
            {'cmd': 'nslookup <domain>', 'desc': 'Query DNS nameserver'}
        ],
        [
            {'cmd': 'ipconfig /renew', 'explanation': 'Re-sends DHCP Request to refresh lease from the DHCP server.'}
        ],
        'Verify valid IP address (not 169.254.x.x) and confirm ping to default gateway succeeds.',
        ['Leaving wrong default gateway configured', 'Static IP conflicting with an existing active host on the network'],
        [{'issue': 'No Internet access', 'fix': 'Check if IP starts with 169.254 (APIPA indicates DHCP failure).'}],
        ['Enable host-based firewall', 'Keep endpoint antivirus and security patches current', 'Disable file sharing on public profiles'],
        {'title': 'Endpoint Network Integration', 'summary': 'Configure static IP, verify gateway ping, and resolve DNS queries.'},
        9
    ),
    make_device(
        'laptop', 'Mobile Laptop Client', 'laptop', 'Computers & Endpoints', 'fa-laptop',
        'Portable computing endpoint with dual wired Ethernet and integrated 802.11ax Wi-Fi wireless interfaces.',
        'Provides mobile corporate computing with automatic switching between wired docking stations and Wi-Fi access points.',
        'Mobile professionals, executive meetings, field technicians, hot-desking offices.',
        'Compact clamshell laptop with internal Wi-Fi antennas and RJ45 or USB-C Ethernet adapter.',
        'Wi-Fi 6 (802.11ax) 2x2 MIMO, Gigabit RJ45 or USB-C Gigabit NIC.',
        'Wireless association to corporate APs or wired connection via docking station.',
        'Cat6 stranded patch cord or 2.4/5GHz RF radio waves.',
        'Rechargeable Lithium-ion battery (45W-100W USB-C PD charger).',
        'DHCP assigned IP across changing subnets as user roams.',
        'Preferred Wi-Fi profiles, 802.1X user certificate credentials, VPN client software.',
        [
            {'cmd': 'ipconfig /all', 'desc': 'Display active adapter IP settings'},
            {'cmd': 'netsh wlan show interfaces', 'desc': 'Show Wi-Fi SSID, BSSID, and signal strength'}
        ],
        [
            {'cmd': 'netsh wlan show interfaces', 'explanation': 'Inspects wireless link parameters including channel, cipher, and receive rate.'}
        ],
        'Confirm active Wi-Fi connection and ping default gateway.',
        ['Typing incorrect WPA passphrase', 'Docking station adapter taking wrong static IP'],
        [{'issue': 'Wi-Fi drops when moving', 'fix': 'Check Fast Roaming 802.11r support on the wireless network.'}],
        ['Enforce full-disk BitLocker encryption', 'Require always-on VPN when off corporate network'],
        {'title': 'Mobile Roaming Lab', 'summary': 'Roam between two access points and observe session continuity.'},
        10
    ),
    make_device(
        'network_printer', 'Enterprise Multifunction Network Printer', 'network-printer', 'Printers', 'fa-print',
        'Dedicated network printing appliance supporting RAW 9100, IPP, and centralized driver spooling.',
        'Processes print, scan, and copy jobs received across the network from workstations and print servers.',
        'Departmental printing hubs, hospital record stations, legal document production.',
        'Floor-standing or heavy desktop unit with front LCD touch screen, paper trays, and rear Ethernet jack.',
        '10/100/1000Base-TX Ethernet port, USB type B port.',
        'Cat6 patch cable to dedicated printer wall jack.',
        'Cat6 UTP copper cable.',
        'Dedicated 110V/220V 15A wall power. Draws up to 1000W during fuser heating.',
        'Static IP or DHCP MAC reservation outside user dynamic pool (e.g. 192.168.10.200).',
        'Printer name, RAW port 9100, LPR queue name, SNMP community, web management password.',
        [
            {'cmd': 'ping <printer_ip>', 'desc': 'Verify network reachability to printer'},
            {'cmd': 'telnet <printer_ip> 9100', 'desc': 'Test if RAW print port 9100 is accepting connections'}
        ],
        [
            {'cmd': 'telnet <printer_ip> 9100', 'explanation': 'Opens a TCP socket to port 9100 to verify the print daemon is listening.'}
        ],
        'Ping printer IP address and submit a test print page from a workstation.',
        ['Allowing printer to take dynamic DHCP without reservation (IP changes break queues)', 'Placing printer on uninsulated UPS battery'],
        [{'issue': 'Printer offline in Windows', 'fix': 'Verify printer IP hasn\'t changed and test ping reachability.'}],
        ['Change default web admin password', 'Disable obsolete protocols (Telnet, FTP, HTTP)', 'Place printers on isolated Printer VLAN'],
        {'title': 'Department Print Server Setup', 'summary': 'Configure static IP on printer and test RAW 9100 socket communication.'},
        11
    ),
    make_device(
        'nas_storage', 'Network Attached Storage (NAS) System', 'nas-storage', 'NAS & Network Storage', 'fa-hard-drive',
        'Dedicated file-level storage server providing RAID-protected shares via SMB/CIFS and NFS.',
        'Centralizes enterprise file sharing, automated system backups, and video surveillance archives with multi-disk redundancy.',
        'Office shared drives, virtualization backup repositories, media streaming servers.',
        'Tower or 2U rack enclosure with 4 to 24 hot-swappable hard drive caddies and status display.',
        'Dual/Quad 1GbE / 10GbE RJ45 or SFP+ ports with link aggregation (LACP) support.',
        'Dual Cat6a copper or SFP+ DAC cables connected to distribution switch in a Port-Channel.',
        'Cat6a shielded copper or 10G SFP+ Twinax DAC cables.',
        'Dual redundant AC power supplies connected to battery backup UPS.',
        'Static IP on isolated Storage VLAN (e.g. 192.168.40.10/24).',
        'RAID type (RAID 5/6/10), shared folder names, SMB/NFS permissions, active directory integration.',
        [
            {'cmd': 'storage share create name=docs path=/vol1/docs', 'desc': 'Create network file share'},
            {'cmd': 'show storage raid status', 'desc': 'Verify health of disk array'}
        ],
        [
            {'cmd': 'show storage raid status', 'explanation': 'Inspects health of all disk members and reports Normal, Degraded, or Rebuilding.'}
        ],
        'Mount SMB share (\\\\192.168.40.10\\docs) from client PC and verify read/write access.',
        ['Using RAID 0 in production (zero fault tolerance; 1 drive failure destroys all data)', 'Exposing unauthenticated SMB shares'],
        [{'issue': 'Slow file transfers', 'fix': 'Enable Jumbo Frames (MTU 9000) end-to-end and configure LACP link bonding.'}],
        ['Enforce SMB 3.1.1 encryption', 'Implement snapshot replication for ransomware defense'],
        {'title': 'RAID 5 Storage Deployment', 'summary': 'Deploy 4-disk RAID 5 NAS on storage VLAN and mount SMB share.'},
        12
    ),
    make_device(
        'nvr_recorder', 'Network Video Recorder (NVR)', 'nvr-recorder', 'NVR & CCTV Devices', 'fa-video',
        'Centralized surveillance appliance capturing, recording, and analyzing digital RTSP video streams from IP cameras.',
        'Provides 24/7 video recording, motion event indexing, multi-camera live viewing, and long-term hard drive archiving.',
        'Commercial building surveillance, municipal traffic monitoring, retail theft prevention.',
        '1U-3U rack appliance with front drive bays, rear HDMI/VGA monitor outputs, and independent PoE camera switch ports.',
        'Independent PoE camera ports (often on isolated 172.16.x.x network) plus separate Gigabit LAN uplink port.',
        'Camera ports connect directly to IP cameras; LAN uplink connects to corporate management switch.',
        'Cat6 solid copper UTP/STP cables.',
        'Internal AC power supply with high wattage for integrated PoE camera budget (150W-350W).',
        'Static IP on surveillance management VLAN (e.g. 192.168.50.2/24).',
        'Recording schedule (Continuous vs Motion), H.265 bitrate, camera retention policy (30 days), ONVIF credentials.',
        [
            {'cmd': 'show cctv cameras', 'desc': 'List all connected IP cameras and streaming bitrates'},
            {'cmd': 'show cctv storage status', 'desc': 'Display surveillance HDD capacity and days retained'}
        ],
        [
            {'cmd': 'show cctv cameras', 'explanation': 'Verifies RTSP stream state, resolution (4K/1080p), and FPS for each channel.'}
        ],
        'Check live video grid on connected monitor or web viewer and verify storage recording indicator.',
        ['Using desktop HDDs instead of surveillance-rated drives (e.g. WD Purple / Seagate SkyHawk)', 'Placing cameras on same subnet as general office traffic'],
        [{'issue': 'Video dropping frames', 'fix': 'Reduce camera resolution or upgrade PoE switch bandwidth to prevent saturation.'}],
        ['Completely block NVR surveillance subnet from accessing the public Internet', 'Disable UPnP on NVR'],
        {'title': 'Surveillance Network Architecture', 'summary': 'Connect 4 IP cameras to an NVR on isolated VLAN 50.'},
        13
    ),
    make_device(
        'ip_camera', 'High-Definition PoE IP Surveillance Camera', 'ip-camera', 'NVR & CCTV Devices', 'fa-camera',
        'Networked digital video camera with integrated CMOS sensor, H.265 hardware encoder, and PoE power receiver.',
        'Captures surveillance video, compresses it in real time, and streams it via RTSP/ONVIF over Ethernet to the NVR.',
        'Indoor hallways, outdoor parking lots, entry gates, warehouse loading docks.',
        'Weatherproof bullet, dome, or motorized PTZ metal housing with IR night-vision LEDs and single RJ45 pigtail.',
        'Single 10/100 Mbps RJ45 PoE port (802.3af Class 2/3).',
        'Direct Cat6 cable run from camera location to PoE switch or NVR PoE port.',
        'Cat6 outdoor UV-resistant solid copper cable.',
        'Power over Ethernet (PoE 802.3af 15.4W or 802.3at 30W for heated PTZs).',
        'Static IP on Surveillance VLAN (e.g. 192.168.50.11/24) matching NVR subnet.',
        'Video resolution (4K/1080p), frame rate (15-30 fps), RTSP port (554), ONVIF user account.',
        [
            {'cmd': 'ping <camera_ip>', 'desc': 'Verify network link and power to camera'}
        ],
        [
            {'cmd': 'ping <camera_ip>', 'explanation': 'Verifies camera network stack is booted and responding.'}
        ],
        'Verify camera feed renders in NVR channel viewer.',
        ['Exceeding 100m Ethernet cable limit without PoE extender', 'Forgetting to waterproof outdoor RJ45 grommet'],
        [{'issue': 'Camera shuts down at night', 'fix': 'Switch port PoE budget insufficient when IR night vision LEDs activate.'}],
        ['Change default admin/admin factory credentials immediately', 'Disable P2P cloud relay features'],
        {'title': 'IP Camera Integration', 'summary': 'Power up camera via PoE switch and stream RTSP to NVR.'},
        14
    ),
    make_device(
        'poe_switch', 'Power over Ethernet (PoE/PoE+) Access Switch', 'poe-switch', 'Switches', 'fa-bolt',
        'Ethernet switch delivering both DC electrical power and high-speed data over a single twisted-pair copper cable.',
        'Powers IP phones, wireless access points, and surveillance cameras directly through standard network cabling.',
        'Security camera distribution closets, VoIP phone deployments, wireless infrastructure backbones.',
        '1U rack chassis with 8 to 48 yellow/green PoE status LEDs and high-output cooling fans.',
        '802.3af (PoE 15.4W), 802.3at (PoE+ 30W), 802.3bt (PoE++ 60W/90W) RJ45 ports.',
        'Cat6 cables to powered devices (PD) like cameras and APs.',
        'Cat6 solid pure copper (avoid cheap copper-clad aluminum CCA which overheats).',
        'High-capacity AC power supply with total PoE power budget from 120W to 740W.',
        'Management SVI IP on network management VLAN.',
        'PoE power priority (Critical/High/Low), per-port power budget limits, PoE scheduling.',
        [
            {'cmd': 'show power inline', 'desc': 'Display real-time PoE wattage consumed per port'},
            {'cmd': 'power inline auto', 'desc': 'Enable automatic 802.3af/at power sensing'}
        ],
        [
            {'cmd': 'show power inline', 'explanation': 'Shows total available budget, consumed wattage, and per-port device class.'}
        ],
        'Check that connected camera or AP powers up and link LED turns amber/green.',
        ['Exceeding total switch power budget', 'Using CCA (copper clad aluminum) cables causing dangerous heating'],
        [{'issue': 'Port PoE fault LED blinking', 'fix': 'Disconnect shorted cable and verify device does not exceed 30W.'}],
        ['Configure PoE port shutdown schedules after office hours for energy conservation and security.'],
        {'title': 'PoE Power Budget Management', 'summary': 'Monitor power allocation across 4 IP cameras and 2 APs.'},
        15
    ),
    make_device(
        'windows_server', 'Enterprise Windows Server Host', 'windows-server', 'Servers', 'fa-server',
        'Enterprise operating system host running Active Directory Domain Services (AD DS), DNS, DHCP, and IIS web services.',
        'Provides centralized identity management, Kerberos authentication, domain group policies, and enterprise file/print services.',
        'Corporate domain controllers, Hyper-V virtualization hosts, enterprise SQL databases.',
        '1U/2U rack server with redundant power supplies, multi-port NICs, and front SAS disk arrays.',
        'Dual/Quad 1GbE / 10GbE RJ45 or SFP+ NICs configured in NIC Teaming (LACP).',
        'Direct connection to datacenter distribution switches in an aggregated link team.',
        'Cat6a shielded copper or SFP+ fiber.',
        'Dual redundant hot-swappable 500W-1100W AC power supplies.',
        'Static IP, subnet mask, default gateway, and loopback (127.0.0.1) or DC IP for DNS.',
        'Computer name, domain join, static IP, DNS forwarders, Windows Firewall domain profile.',
        [
            {'cmd': 'ipconfig /all', 'desc': 'Show detailed Windows network configuration'},
            {'cmd': 'netstat -ano', 'desc': 'Display active listening TCP/UDP ports and process IDs'},
            {'cmd': 'Get-NetIPAddress', 'desc': 'PowerShell command to list interface configurations'}
        ],
        [
            {'cmd': 'netstat -ano', 'explanation': 'Shows which network services are listening on which ports (e.g. 53 for DNS, 389 for LDAP).'}
        ],
        'Ping default gateway and test Active Directory domain join from a client PC.',
        ['Setting DNS to 8.8.8.8 on a Domain Controller instead of pointing to itself or internal DNS', 'Duplicate SID on cloned VMs'],
        [{'issue': 'Domain join fails', 'fix': 'Ensure client DNS points to Windows Server IP and port 53/389 are reachable.'}],
        ['Enable Windows Defender Firewall with Advanced Security', 'Disable SMBv1', 'Enforce Kerberos and NTLMv2 only'],
        {'title': 'Windows Server Domain Infrastructure', 'summary': 'Configure static IP, DNS role, and test domain workstation join.'},
        16
    ),
    make_device(
        'linux_server', 'Enterprise Linux Infrastructure Server', 'linux-server', 'Servers', 'fa-terminal',
        'Open-source server host running Ubuntu/RHEL/Debian, powering web services, databases, Docker containers, and DNS/DHCP.',
        'Delivers high-reliability, low-overhead network infrastructure services using Linux kernel networking and systemd.',
        'Apache/Nginx web servers, PostgreSQL/MySQL databases, Kubernetes clusters, BIND9 DNS servers.',
        'Rack server chassis or virtual machine instance with high-speed virtual/physical network interfaces.',
        'Physical 10G/25G NICs or virtio virtual network interfaces (eth0, ens192).',
        'Connected to datacenter switch or hypervisor virtual switch (vSwitch).',
        'Cat6a copper or DAC SFP+ twinax cables.',
        'Dual redundant enterprise power supplies.',
        'Static IP configured via Netplan (/etc/netplan/*.yaml) or NetworkManager (nmcli).',
        'Hostname (/etc/hostname), resolver (/etc/resolv.conf), iptables/nftables firewall rules, SSH keys.',
        [
            {'cmd': 'ip addr show', 'desc': 'Display IP addresses and interface states'},
            {'cmd': 'ip route show', 'desc': 'Display Linux kernel routing table'},
            {'cmd': 'ss -tulnp', 'desc': 'Show active listening TCP/UDP sockets and process names'},
            {'cmd': 'systemctl status <service>', 'desc': 'Check daemon operational status'}
        ],
        [
            {'cmd': 'ip addr show', 'explanation': 'Modern iproute2 replacement for ifconfig, showing IPv4/IPv6 addresses and flags.'}
        ],
        'Run "ip addr show" and verify end-to-end ping and SSH access.',
        ['Syntax errors in YAML Netplan file (incorrect indentation causes boot network failure)', 'UFW firewall blocking incoming SSH port 22'],
        [{'issue': 'Cannot reach Internet', 'fix': 'Check "ip route show" for default via <gateway> and verify /etc/resolv.conf.'}],
        ['Disable root SSH login; enforce public key authentication', 'Configure UFW or nftables firewall to permit only required ports'],
        {'title': 'Linux Infrastructure Deployment', 'summary': 'Configure static IP using Netplan and verify web server listener.'},
        17
    ),
    make_device(
        'dhcp_server', 'Enterprise Dynamic Host Configuration Protocol (DHCP) Server', 'dhcp-server', 'Servers', 'fa-network-wired',
        'Network infrastructure service automatically leasing IP addresses, subnet masks, gateways, and options to client endpoints.',
        'Automates client network provisioning via DORA (Discover, Offer, Request, Acknowledge) handshake.',
        'Corporate campus subnets, guest Wi-Fi networks, VoIP phone provisioning, PXE boot environments.',
        'Dedicated appliance, Linux Kea daemon, or Windows Server DHCP role.',
        'Gigabit Ethernet interface connected to core/distribution network.',
        'Direct connection to switch port in server management VLAN.',
        'Cat6 UTP copper cable.',
        'AC mains power with UPS protection.',
        'Permanent static IP address (never dynamic).',
        'Scope range, lease duration (e.g. 8 days corporate, 2 hours guest), gateway (Option 3), DNS (Option 6), domain name (Option 15).',
        [
            {'cmd': 'show ip dhcp binding', 'desc': 'List all currently active leased client MAC-to-IP bindings'},
            {'cmd': 'show ip dhcp pool', 'desc': 'Check pool utilization and free addresses'}
        ],
        [
            {'cmd': 'show ip dhcp binding', 'explanation': 'Shows client hardware MAC, leased IP address, and lease expiration timestamp.'}
        ],
        'Release and renew IP on client PC; check that lease appears in DHCP binding table.',
        ['Exhausting the DHCP scope pool', 'Forgetting to exclude default gateway IP resulting in address conflict'],
        [{'issue': 'Clients receive 169.254.x.x', 'fix': 'Ensure DHCP service is running and configure "ip helper-address" on router.'}],
        ['Enable DHCP Snooping on switches to block unauthorized rogue DHCP servers', 'Authorize DHCP server in Active Directory'],
        {'title': 'DHCP Scope Deployment Lab', 'summary': 'Create DHCP scope 192.168.1.100-200 and verify client auto-configuration.'},
        18
    ),
    make_device(
        'dns_server', 'Domain Name System (DNS) Resolver & Nameserver', 'dns-server', 'Servers', 'fa-book-atlas',
        'Hierarchical, decentralized naming system translating human-readable hostnames into numerical IP addresses.',
        'Resolves Fully Qualified Domain Names (FQDNs like www.example.com) to IPv4 addresses (A records) and IPv6 addresses (AAAA records).',
        'Active Directory domain resolution, web browsing, email MX routing, internal microservice discovery.',
        'Dedicated server, BIND9 Linux daemon, or Windows Server DNS role.',
        'Gigabit Ethernet NIC listening on UDP and TCP port 53.',
        'Connected to server farm core switch.',
        'Cat6 copper patch cord.',
        'AC power with UPS.',
        'Permanent static IP address (e.g. 192.168.1.5 or 10.0.0.5).',
        'Forward lookup zones, reverse lookup zones (PTR), root hints, forwarders (e.g. 1.1.1.1, 8.8.8.8), conditional forwarders.',
        [
            {'cmd': 'nslookup <hostname> <dns_server_ip>', 'desc': 'Query specific DNS server for name resolution'},
            {'cmd': 'dig @<dns_ip> <domain> A', 'desc': 'Comprehensive DNS query and response header inspection'}
        ],
        [
            {'cmd': 'nslookup', 'explanation': 'Sends a DNS query to verify that the server returns the correct IP record for a hostname.'}
        ],
        'Execute nslookup from endpoint targeting the DNS server IP and verify correct resolution.',
        ['Missing reverse lookup zone causing Kerberos authentication delays', 'Circular forwarder configuration causing DNS loops'],
        [{'issue': 'Cannot resolve internet domains', 'fix': 'Check DNS forwarders and verify firewall allows outbound UDP port 53.'}],
        ['Enable DNSSEC (DNS Security Extensions) to prevent cache poisoning', 'Restrict zone transfers (AXFR) to authorized secondary servers'],
        {'title': 'Internal DNS Infrastructure', 'summary': 'Configure forward lookup zone "corp.local" and resolve internal server hostnames.'},
        19
    ),
    make_device(
        'web_server', 'High-Performance HTTP/HTTPS Web Server', 'web-server', 'Servers', 'fa-globe',
        'Web application host serving static HTML, CSS, JavaScript, dynamic web applications, and REST APIs over HTTP/HTTPS.',
        'Listens for HTTP/HTTPS requests from web browsers and reverse proxies, executing backend code and serving responses.',
        'Corporate public websites, customer portals, internal intranet wikis, REST API backends.',
        'Datacenter rack server, cloud VM, or containerized Docker host running Nginx or Apache.',
        '10GbE network interface listening on TCP port 80 (HTTP) and TCP port 443 (HTTPS).',
        'Connected to DMZ switch behind firewall, or datacenter application tier.',
        'Cat6a shielded copper or SFP+ fiber.',
        'Dual AC power supplies.',
        'Static IP on DMZ subnet (e.g. 203.0.113.100 or internal DMZ 172.16.1.10).',
        'Server block/virtual host configuration, SSL/TLS certificate paths, document root (/var/www/html), HTTP/2 support.',
        [
            {'cmd': 'curl -I http://<server_ip>', 'desc': 'Fetch HTTP response headers to test web service'},
            {'cmd': 'systemctl status nginx', 'desc': 'Check web server process status'}
        ],
        [
            {'cmd': 'curl -I', 'explanation': 'Returns HTTP status code (200 OK, 301 Redirect, 404 Not Found) without downloading page body.'}
        ],
        'Navigate to http://<server_ip> in browser and confirm HTTP 200 OK response.',
        ['Binding web server to 127.0.0.1 instead of 0.0.0.0 (prevents remote connections)', 'Expired SSL/TLS certificate'],
        [{'issue': 'Connection refused on port 80', 'fix': 'Ensure web server service (nginx/apache) is started and firewall permits port 80.'}],
        ['Enforce HTTPS redirect (HTTP 301)', 'Deploy TLS 1.3 only; disable SSLv3 and TLS 1.0/1.1', 'Enable HSTS security headers'],
        {'title': 'DMZ Web Server Publishing', 'summary': 'Configure web server on DMZ and permit inbound HTTP via firewall rule.'},
        20
    ),
    make_device(
        'file_server', 'Centralized Enterprise File Server', 'file-server', 'Servers', 'fa-folder-open',
        'High-capacity server managing centralized file storage, user quotas, Windows NTFS/Linux ACL permissions, and SMB shares.',
        'Provides collaborative file storage, team document directories, automated versioning, and access auditing.',
        'Corporate department shares (Finance, Legal, HR), user home folders, project archives.',
        '2U-4U rack server with large SAS/SATA drive array and hardware RAID controller.',
        'Dual 10GbE NICs configured in failover/load-balancing team.',
        'Connected to datacenter core/distribution switch.',
        'Cat6a copper or SFP+ optical fiber.',
        'Dual redundant AC power supplies.',
        'Static IP address on enterprise server VLAN.',
        'Share permissions, NTFS/POSIX security descriptors, disk quotas, Volume Shadow Copy (VSS) snapshots.',
        [
            {'cmd': 'net share', 'desc': 'Display active SMB shares on Windows file server'},
            {'cmd': 'showmount -e <server_ip>', 'desc': 'List NFS exported shares'}
        ],
        [
            {'cmd': 'net share', 'explanation': 'Lists all shared folder names, local directory paths, and remark descriptions.'}
        ],
        'Connect from client PC via \\\\<server_ip>\\share and create a test document.',
        ['Granting "Everyone: Full Control" on root share', 'Disabling Volume Shadow Copies eliminating accidental file deletion recovery'],
        [{'issue': 'Access denied to share', 'fix': 'Verify both Share permissions AND NTFS file system security permissions permit the user.'}],
        ['Enable SMB encryption on transit', 'Implement Access-Based Enumeration (ABE) so users only see folders they have permission to access'],
        {'title': 'Department File Share Setup', 'summary': 'Provision SMB share on file server and test authenticated client access.'},
        21
    ),
    make_device(
        'ups_power', 'Smart Rack-Mount Uninterruptible Power Supply (UPS)', 'ups-power', 'Infrastructure & Cables', 'fa-car-battery',
        'Power protection and battery backup system providing continuous clean AC power during electrical outages and surges.',
        'Prevents catastrophic sudden power loss to switches, routers, and servers, providing battery runtime and graceful automated shutdowns.',
        'Server room equipment racks, network closets (IDF/MDF), telecom huts, hospital medical equipment racks.',
        '1U-3U rack-mount chassis with front battery bay, LCD status display, and rear battery-backed IEC/NEMA receptacles.',
        'Integrated SNMP/Network Management Card (NMC) with RJ45 10/100 Ethernet port for remote monitoring.',
        'Ethernet port connects to network management switch; power cords connect to equipment power supplies.',
        'Cat6 copper for network monitoring card.',
        'Connects to 120V/208V/240V utility AC mains; contains sealed lead-acid (SLA) or Lithium-ion battery packs (1000VA to 5000VA).',
        'Static IP on dedicated out-of-band management VLAN (e.g. 192.168.99.50).',
        'High/low voltage transfer thresholds, battery self-test schedule, SNMP trap recipients, automated shutdown delays.',
        [
            {'cmd': 'show power ups status', 'desc': 'Display battery charge percentage, runtime remaining, and load wattage'}
        ],
        [
            {'cmd': 'show power ups status', 'explanation': 'Monitors remaining battery run-time in minutes, input voltage, and output load percent.'}
        ],
        'Access UPS web interface or SNMP card to verify 100% battery charge and normal utility line voltage.',
        ['Overloading UPS by plugging laser printers or space heaters into battery outlets', 'Failing to replace aging batteries every 3-5 years'],
        [{'issue': 'UPS beeping continuously', 'fix': 'Indicates power outage, overload, or battery self-test failure. Check LCD error code.'}],
        ['Change default NMC admin password', 'Isolate UPS network card on an untrusted out-of-band management VLAN with no internet access'],
        {'title': 'Critical Rack Power Protection', 'summary': 'Monitor UPS battery runtime and configure automated shutdown signaling.'},
        22
    ),
    make_device(
        'modem', 'Broadband Cable / DSL Data Modem', 'modem', 'Infrastructure & Cables', 'fa-satellite-dish',
        'Modulator-demodulator converting analog ISP signals (coaxial RF or twisted-pair copper) into digital Ethernet frames.',
        'Establishes physical and data link layer connectivity to the Internet Service Provider (ISP) network.',
        'Small office WAN ingress, residential broadband, backup cellular LTE/5G failover.',
        'Desktop plastic chassis with front status LEDs (Power, Downstream, Upstream, Online) and rear coax/DSL port plus RJ45 LAN port.',
        'F-type coaxial connector (DOCSIS) or RJ11 jack (DSL/VDSL), plus 1x or 2x Gigabit RJ45 LAN ports.',
        'WAN port to ISP wall outlet; LAN port to router WAN GigabitEthernet port.',
        'RG-6 coaxial cable for cable broadband; Cat6 patch cord to router WAN interface.',
        'External 12V DC wall transformer, 10W-25W.',
        'Pass-through bridge mode (modem transparently bridges public IP to connected router). Internal diagnostic IP usually 192.168.100.1.',
        'DOCSIS channel bonding, upstream/downstream power levels, bridge mode vs router mode.',
        [
            {'cmd': 'show modem signal', 'desc': 'Inspect downstream and upstream signal-to-noise ratio (SNR)'}
        ],
        [
            {'cmd': 'show modem signal', 'explanation': 'Verifies physical RF signal levels are within acceptable dBmV and SNR limits.'}
        ],
        'Check that Online LED is solid green and router receives public IP on its WAN interface via DHCP.',
        ['Leaving modem in router mode when connected to a second router (causes Double-NAT)', 'Loose coaxial connectors causing high packet loss'],
        [{'issue': 'Online LED blinking', 'fix': 'Modem cannot lock onto downstream ISP frequency. Check cable physical connections.'}],
        ['Change default web diagnostic password', 'Ensure modem is set to pure Bridge Mode to hand public IP directly to the firewall'],
        {'title': 'ISP WAN Provisioning Lab', 'summary': 'Connect modem to router WAN interface and verify DHCP public IP acquisition.'},
        23
    ),
    make_device(
        'ont_terminal', 'Optical Network Terminal (ONT / GPON Fiber Gateway)', 'ont-terminal', 'Infrastructure & Cables', 'fa-diagram-successor',
        'Gigabit Passive Optical Network (GPON) subscriber terminal converting fiber optic laser pulses into standard Ethernet.',
        'Acts as the optical demarcation point connecting customer premises to the ISP optical distribution network (ODN).',
        'Fiber-to-the-Home (FTTH) and Fiber-to-the-Business (FTTB) gigabit and multi-gigabit Internet connections.',
        'Wall-mount or desktop unit with optical SC/APC green fiber port, status LEDs (PON, LOS, LAN), and Gigabit/10G RJ45 ports.',
        '1x SC/APC optical receptacle (1490nm downstream / 1310nm upstream), 1x-4x Gigabit / 10G RJ45 LAN ports.',
        'Single-mode fiber cable from street fiber drop; Cat6a copper cable to customer firewall WAN port.',
        'Single-Mode Fiber (OS2 with green angled SC/APC connector); Cat6a UTP copper.',
        '12V DC power adapter, often connected to a dedicated battery backup unit (BBU) for telephone lifeline service.',
        'Bridged mode passing public IP or PPPoE session directly to customer firewall.',
        'GPON serial number, PLOAM password, optical power budget, VLAN ID tagging (e.g. VLAN 201 for Internet).',
        [
            {'cmd': 'show optical power', 'desc': 'Check received optical signal strength in dBm'}
        ],
        [
            {'cmd': 'show optical power', 'explanation': 'Acceptable GPON receive power typically ranges from -8 dBm to -27 dBm. Below -28 dBm drops link.'}
        ],
        'Confirm PON status LED is solid green and LOS (Loss of Signal) red LED is completely OFF.',
        ['Plugging blue UPC connector into green APC receptacle (destroys fiber ferrule and causes massive signal loss)', 'Bending optical fiber past minimum bend radius'],
        [{'issue': 'Red LOS light flashing', 'fix': 'Loss of optical signal. Inspect fiber patch cord for kinks, breaks, or contamination.'}],
        ['Keep protective dust caps on optical connectors until the exact moment of connection.'],
        {'title': 'Fiber GPON WAN Demarcation', 'summary': 'Connect ONT via optical fiber and configure router WAN with ISP 802.1Q tag.'},
        24
    ),
    make_device(
        'patch_panel', 'Structured Cabling Copper & Fiber Patch Panel', 'patch-panel', 'Infrastructure & Cables', 'fa-bars-staggered',
        'Passive rack-mounted termination hardware organizing, labeling, and connecting permanent horizontal cabling runs to switches.',
        'Provides a clean, durable, flexible demarcation interface between permanent in-wall cables and active switch ports.',
        'Network racks in Main Distribution Frames (MDF) and Intermediate Distribution Frames (IDF).',
        '1U/2U 19-inch steel rack panel with 24 or 48 numbered front RJ45 jacks and rear 110/Krone punch-down blocks.',
        '24 or 48 RJ45 Cat6/Cat6a keystone jacks or LC optical fiber duplex couplers.',
        'Permanent solid core horizontal cables punched down in rear; short stranded patch cords connect front jacks to switch ports.',
        'Solid copper Cat6 for permanent runs; flexible stranded Cat6 patch cords for front jumpers.',
        'Completely passive physical hardware. Requires ZERO electrical power.',
        'None. Operates strictly at Layer 1 Physical.',
        'None. Follows T568A or T568B structured cabling color coding.',
        [],
        [],
        'Use wiremap cable certifier to test continuity, pinout correctness, and wire attenuation.',
        ['Untwisting pairs more than 0.5 inches during punch-down (destroys Cat6 crosstalk performance)', 'Mixing T568A on one end and T568B on other without intention'],
        [{'issue': 'Cable tester reports split pair', 'fix': 'Re-punch conductor pairs following exact T568B color sequence.'}],
        ['Properly ground shielded patch panels to rack grounding busbar to prevent ESD buildup.'],
        {'title': 'Structured Cabling Rack Dressing', 'summary': 'Patch 24 workstation drops cleanly from patch panel to access switch.'},
        25
    ),
    make_device(
        'vpn_gateway', 'Enterprise Site-to-Site & Remote-Access VPN Gateway', 'vpn-gateway', 'Firewalls', 'fa-lock',
        'Cryptographic gateway establishing encrypted IPsec and SSL/TLS tunnels across the public Internet.',
        'Connects remote branch offices and mobile work-from-home users securely into the corporate intranet.',
        'Multi-site corporate WAN interconnection, teleworker secure remote access, cloud VPC interconnection.',
        '1U rack appliance with dedicated hardware cryptographic acceleration cards (AES-NI / QAT).',
        'Dual Gigabit/10G RJ45/SFP+ interfaces (Public WAN and Private Intranet LAN).',
        'Public port to Internet gateway; private port to internal distribution switch.',
        'Cat6a shielded copper or optical fiber.',
        'Dual redundant AC power supplies, 80W-250W.',
        'Public static IP on outside interface; private static IP on inside corporate interface.',
        'IKEv2 Phase 1 policies (AES-256, SHA-384, DH Group 19/21), IPsec Phase 2 Transform Sets, VPN client IP pools.',
        [
            {'cmd': 'show crypto isakmp sa', 'desc': 'Display active IKEv1/IKEv2 Phase 1 security associations'},
            {'cmd': 'show crypto ipsec sa', 'desc': 'Display active Phase 2 IPsec encrypted tunnel traffic and packet counters'}
        ],
        [
            {'cmd': 'show crypto ipsec sa', 'explanation': 'Verifies encrypted (#pkts encaps) and decrypted (#pkts decaps) byte counters.'}
        ],
        'Run "show crypto ipsec sa" and verify ping flows across encrypted tunnel between branch and HQ.',
        ['Mismatched pre-shared keys (PSK)', 'Mismatched Phase 1 or Phase 2 crypto proposal parameters (cipher/hash/lifetime)'],
        [{'issue': 'Tunnel fails to establish', 'fix': 'Check firewall permits UDP port 500 (IKE), UDP 4500 (NAT-T), and IP Protocol 50 (ESP).'}],
        ['Enforce multi-factor authentication (MFA) on all remote-access SSL VPNs', 'Decommission weak 3DES and SHA-1 algorithms'],
        {'title': 'Site-to-Site IPsec VPN Tunnel', 'summary': 'Build encrypted IPsec tunnel between Branch and HQ routers and route traffic.'},
        26
    ),
    make_device(
        'load_balancer', 'Application Delivery Controller & Load Balancer', 'load-balancer', 'Servers', 'fa-scale-balanced',
        'Hardware or virtual traffic director distributing incoming network connections across multiple backend servers.',
        'Eliminates server bottlenecks, provides high availability, offloads SSL/TLS decryption, and performs health checks.',
        'E-commerce websites, cloud web applications, high-volume database clusters, enterprise email farms.',
        '1U rack appliance with hardware SSL offloading chips or virtual software appliance (HAProxy/F5 BIG-IP).',
        'Dual 10GbE / 25GbE optical interfaces (Client-side VIP and Server-side pool).',
        'Connected to DMZ and internal application server farm switches.',
        'Cat6a copper or SFP+ fiber.',
        'Dual redundant AC power supplies.',
        'Virtual IP (VIP) facing clients; backend pool member private IP addresses.',
        'Balancing algorithm (Round Robin, Least Connections, Source IP Hash), Health check monitors, SSL termination, cookie persistence.',
        [
            {'cmd': 'show loadbalancer pool status', 'desc': 'Display health state of backend server pool members'},
            {'cmd': 'show loadbalancer statistics', 'desc': 'Display active connection counts and traffic distribution'}
        ],
        [
            {'cmd': 'show loadbalancer pool status', 'explanation': 'Indicates which backend web servers are answering HTTP health probes (UP) or failed (DOWN).'}
        ],
        'Send repeated HTTP requests to the Virtual IP and verify requests are distributed across backend servers.',
        ['Misconfiguring health check URL resulting in all backend servers marked DOWN', 'Lacking session persistence for shopping carts'],
        [{'issue': '503 Service Unavailable', 'fix': 'Check backend server health probes; verify backend web services are listening.'}],
        ['Terminate SSL/TLS at the load balancer with modern cipher suites', 'Implement Web Application Firewall (WAF) inspection'],
        {'title': 'High-Availability Web Server Pool', 'summary': 'Deploy load balancer distributing HTTP requests across two web servers.'},
        27
    )
]
