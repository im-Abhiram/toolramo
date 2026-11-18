# courses_data.py
# Comprehensive course, lesson, lab, and quiz definitions for Ramonet Academy

COURSES_DATA = [
    {
        'title': 'Introduction to Computer Networking',
        'slug': 'intro-to-networking',
        'description': 'Master the foundations of modern data networking: the OSI 7-layer reference model, TCP/IP protocol suite, IPv4 addressing, subnet masks, and core network topologies.',
        'level': 'beginner',
        'category': 'foundations',
        'estimated_hours': 4.5,
        'icon': 'fa-network-wired',
        'badge_name': 'Certified Networking Associate',
        'order': 1,
        'lessons': [
            {
                'title': 'The OSI 7-Layer Model & TCP/IP Architecture',
                'slug': 'osi-model-tcp-ip',
                'lesson_number': 1,
                'difficulty': 'beginner',
                'estimated_minutes': 25,
                'summary': 'Understand the conceptual framework of data communication from physical bits to application protocols.',
                'section_a_intro': {
                    'definition': 'The OSI (Open Systems Interconnection) reference model is a conceptual 7-layer framework developed by ISO to standardize telecommunications and networking protocols regardless of underlying internal structure and hardware.',
                    'purpose': 'Provides a standardized reference model to understand how data moves from software applications across physical transmission media to another application.',
                    'why_needed': 'Without standardization, proprietary vendor equipment could not interoperate. It breaks down complex communication into manageable modular layers.',
                    'where_used': 'Every modern digital telecommunications network, enterprise LAN/WAN, internet protocol stack, and network certification.',
                    'real_world_examples': 'Web browsers sending HTTP GET requests over TCP connections, encapsulated in IP packets, framed onto Ethernet cables.',
                    'advantages': ['Vendor interoperability', 'Modular protocol development', 'Simplified troubleshooting by layer', 'Clear demarcation of networking roles'],
                    'limitations': ['Theoretical model—real-world Internet uses the 4-layer TCP/IP stack', 'Some protocols span multiple layers', 'Slight protocol encapsulation overhead']
                },
                'section_b_how_it_works': {
                    'architecture': 'Data encapsulation flows downwards from Layer 7 (Application) to Layer 1 (Physical) on transmission, and decapsulation flows upwards on reception.',
                    'protocols': ['Layer 7: HTTP, DNS, SSH, FTP', 'Layer 4: TCP, UDP', 'Layer 3: IPv4, IPv6, ICMP', 'Layer 2: Ethernet, 802.11 Wi-Fi, ARP', 'Layer 1: Copper 1000BASE-T, Optical Fiber'],
                    'interfaces': ['Physical RJ45 ports', 'SFP optical transceivers', 'Virtual loopbacks', 'Network Interface Cards (NICs)'],
                    'data_flow': 'Data (L7) -> Segments (L4) -> Packets (L3) -> Frames (L2) -> Bits/Voltages (L1)',
                    'device_interactions': 'L1 Hubs/Repeaters -> L2 Switches/Bridges (MAC) -> L3 Routers/Multilayer Switches (IP) -> L4-L7 Firewalls and Proxies',
                    'osi_layers': 'Layer 1: Physical, Layer 2: Data Link, Layer 3: Network, Layer 4: Transport, Layer 5: Session, Layer 6: Presentation, Layer 7: Application'
                },
                'section_c_connection': {
                    'required_devices': ['Workstation PC', 'Layer 2 Switch', 'Edge Router'],
                    'cable_types': ['Cat6 UTP Straight-Through copper cable'],
                    'port_selection': 'Connect PC Ethernet0 to Switch GigabitEthernet0/1; Switch GigabitEthernet0/24 to Router GigabitEthernet0/0',
                    'interface_compatibility': '10/100/1000 Mbps Auto-MDIX RJ45 interfaces',
                    'connection_diagram': '[PC-01: 192.168.1.10] <--- Cat6 ---> [SW-01: Fa0/1] <--- Trunk/Access ---> [RTR-01: 192.168.1.1]',
                    'ip_requirements': 'Subnet 192.168.1.0/24 (Subnet Mask 255.255.255.0)',
                    'power_poe': 'Standard AC 110V-240V power supplies; no PoE required for basic PC connection.'
                },
                'section_d_configuration': {
                    'device_setup': 'Assign static IP address, subnet mask, and default gateway to PC-01.',
                    'interface_config': 'Ensure switch port is in access mode and router interface is enabled with "no shutdown".',
                    'ip_config': 'PC-01 IP: 192.168.1.10/24, Default Gateway: 192.168.1.1. Router g0/0 IP: 192.168.1.1/24.',
                    'network_services': 'Enable ICMP echo on endpoints for reachability validation.',
                    'security_settings': 'Secure switch access ports against unauthorized spanning-tree topology modifications.',
                    'verification': 'Execute ping 192.168.1.1 from PC-01 and verify ARP table entry via arp -a.'
                },
                'section_e_commands': [
                    {
                        'command': 'ipconfig /all',
                        'syntax': 'ipconfig [/all]',
                        'purpose': 'Display full TCP/IP configuration including IP address, subnet mask, MAC address, and gateway.',
                        'params': '/all: verbose output including physical MAC and DHCP lease info',
                        'mode': 'Windows CMD / PC Endpoint',
                        'expected_output': 'IPv4 Address. . . : 192.168.1.10\nSubnet Mask . . . : 255.255.255.0\nDefault Gateway . : 192.168.1.1\nPhysical Address. : 00-1A-2B-3C-4D-5E',
                        'verification_commands': ['ping 127.0.0.1', 'ping 192.168.1.1'],
                        'common_errors': 'Missing default gateway causes inability to route outside the local subnet.'
                    },
                    {
                        'command': 'ping 192.168.1.1',
                        'syntax': 'ping <ip_address>',
                        'purpose': 'Test Layer 3 ICMP echo reachability to default gateway.',
                        'params': '<ip_address>: destination target IPv4 address',
                        'mode': 'PC / Router / Switch CLI',
                        'expected_output': 'Reply from 192.168.1.1: bytes=32 time=1ms TTL=64\nPackets: Sent = 4, Received = 4, Lost = 0 (0% loss)',
                        'verification_commands': ['arp -a', 'tracert 192.168.1.1'],
                        'common_errors': 'Request timed out indicates wrong IP, interface down, or firewall blocking ICMP.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'pc1', 'name': 'PC-01', 'type': 'pc_workstation', 'x': 140, 'y': 220, 'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                        {'id': 'sw1', 'name': 'SW-01', 'type': 'layer2_switch', 'x': 340, 'y': 220, 'interfaces': ['Fa0/1', 'Fa0/2', 'Fa0/24']},
                        {'id': 'rtr1', 'name': 'RTR-01', 'type': 'router', 'x': 540, 'y': 220, 'ip': '192.168.1.1', 'mask': '255.255.255.0', 'interfaces': ['g0/0']}
                    ],
                    'links': [
                        {'from': 'pc1', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/1', 'cable': 'copper_straight'},
                        {'from': 'sw1', 'from_port': 'Fa0/24', 'to': 'rtr1', 'to_port': 'g0/0', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Inspect PC-01 IP Configuration',
                        'instruction': 'Select PC-01, open terminal, and run ipconfig to verify IPv4 address and default gateway.',
                        'target_device': 'pc1',
                        'expected_config': {'ip': '192.168.1.10', 'gateway': '192.168.1.1'},
                        'hints': [
                            'Click on PC-01 to open the device configuration and CLI inspector.',
                            'Type "ipconfig" into the terminal prompt to view IP configuration.',
                            'Verify that IPv4 is 192.168.1.10 and default gateway is 192.168.1.1.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc1', 'action': 'select', 'explanation': 'Select PC-01 on canvas.'},
                            {'step': 2, 'device': 'pc1', 'action': 'cli_command', 'command': 'ipconfig', 'explanation': 'Execute ipconfig command.'}
                        ]
                    },
                    {
                        'task_id': 'task_2',
                        'title': 'Test ICMP Reachability to Gateway',
                        'instruction': 'From PC-01, execute ping 192.168.1.1 to confirm Layer 3 bidirectional packet flow.',
                        'target_device': 'pc1',
                        'expected_config': {'ping_success': '192.168.1.1'},
                        'hints': [
                            'Use the ping utility targeting the gateway IP.',
                            'Type "ping 192.168.1.1" in PC-01 terminal.',
                            'The ping must receive 4 successful echo replies (0% loss).'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc1', 'action': 'cli_command', 'command': 'ping 192.168.1.1', 'explanation': 'Send ICMP Echo Request to 192.168.1.1.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'devices': {
                        'pc1': {'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                        'rtr1': {'interfaces': {'g0/0': {'ip': '192.168.1.1', 'mask': '255.255.255.0', 'status': 'up'}}}
                    },
                    'ping_tests': [
                        {'from': 'pc1', 'to': '192.168.1.1', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Ping returns "Destination host unreachable"',
                        'cause': 'PC is trying to send packets to a different subnet with no default gateway or wrong subnet mask.',
                        'diagnosis': 'Check ipconfig output to verify PC IP and default gateway are on the same subnet.',
                        'fix': 'Set subnet mask to 255.255.255.0 and gateway to 192.168.1.1.'
                    },
                    {
                        'symptom': 'Ping returns "Request timed out"',
                        'cause': 'Physical link down, intermediate switch port shutdown, or target router interface disabled.',
                        'diagnosis': 'Verify physical link status indicator and router interface status with "show ip interface brief".',
                        'fix': 'Issue "no shutdown" on router GigabitEthernet0/0 interface.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'Which layer of the OSI model is responsible for logical IP addressing and path determination across networks?',
                        'options': [
                            {'id': 'A', 'text': 'Layer 2 - Data Link Layer'},
                            {'id': 'B', 'text': 'Layer 3 - Network Layer'},
                            {'id': 'C', 'text': 'Layer 4 - Transport Layer'},
                            {'id': 'D', 'text': 'Layer 7 - Application Layer'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'The Network Layer (Layer 3) handles logical IP addressing, routing protocols, and packet forwarding between disparate networks.'
                    },
                    {
                        'question_type': 'true_false',
                        'question_text': 'A Layer 2 switch inspects IP packets to make forwarding decisions.',
                        'options': [
                            {'id': 'True', 'text': 'True'},
                            {'id': 'False', 'text': 'False'}
                        ],
                        'correct_answer': 'False',
                        'explanation': 'Layer 2 switches make forwarding decisions based strictly on Layer 2 MAC addresses found in the Ethernet frame header, not Layer 3 IP addresses.'
                    },
                    {
                        'question_type': 'cli_identify',
                        'question_text': 'Which command on a Windows endpoint displays the full TCP/IP configuration including MAC address and gateway?',
                        'options': [
                            {'id': 'A', 'text': 'show ip interface brief'},
                            {'id': 'B', 'text': 'ipconfig /all'},
                            {'id': 'C', 'text': 'netstat -r'},
                            {'id': 'D', 'text': 'ping localhost'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'ipconfig /all outputs comprehensive configuration details including physical hardware address (MAC), IPv4/IPv6 addresses, subnet mask, and default gateway.'
                    }
                ]
            },
            {
                'title': 'IP Addressing (IPv4), Subnetting & MAC Addressing',
                'slug': 'ipv4-subnetting-mac',
                'lesson_number': 2,
                'difficulty': 'beginner',
                'estimated_minutes': 30,
                'summary': 'Master 32-bit IPv4 addresses, network vs host bits, CIDR notation, and 48-bit Layer 2 MAC hardware identifiers.',
                'section_a_intro': {
                    'definition': 'An IPv4 address is a 32-bit logical numerical identifier assigned to each network interface card. A MAC address is a 48-bit burned-in hardware address.',
                    'purpose': 'IPv4 addresses provide globally unique or private logical identities for routing across networks; MAC addresses provide hop-by-hop local link delivery.',
                    'why_needed': 'Enables computers worldwide to address and route data packets reliably to destination hosts across intermediate routers.',
                    'where_used': 'Every local area network, enterprise intranet, cloud VPC, and the public global Internet.',
                    'real_world_examples': 'Private address blocks: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 defined in RFC 1918.',
                    'advantages': ['Hierarchical routing structure', 'Variable Length Subnet Masking (VLSM) efficiency', 'Clear subnet boundaries'],
                    'limitations': ['IPv4 32-bit address exhaustion (~4.3 billion addresses)', 'Requires NAT for IPv4 conservation']
                },
                'section_b_how_it_works': {
                    'architecture': 'IPv4 addresses are divided by the subnet mask into two segments: Network prefix bits and Host identifier bits.',
                    'protocols': ['IPv4', 'ARP (Address Resolution Protocol)', 'ICMP'],
                    'interfaces': ['Ethernet interfaces', 'Virtual SVI', 'Loopback interfaces'],
                    'data_flow': 'Sender compares destination IP with local subnet mask. If in same subnet, resolves MAC via ARP and delivers directly. If remote, sends to default gateway MAC.',
                    'device_interactions': 'Endpoints broadcast ARP Requests ("Who has 192.168.1.1? Tell 192.168.1.10"). Target replies with unicast ARP Reply containing its MAC.',
                    'osi_layers': 'Layer 3 (IP) mapped to Layer 2 (MAC) via ARP.'
                },
                'section_c_connection': {
                    'required_devices': ['PC-A (192.168.1.10/24)', 'PC-B (192.168.1.20/24)', 'Layer 2 Switch'],
                    'cable_types': ['Cat6 Straight-Through cables'],
                    'port_selection': 'PC-A to Switch port Fa0/1, PC-B to Switch port Fa0/2',
                    'interface_compatibility': '100BASE-TX / 1000BASE-T',
                    'connection_diagram': '[PC-A: .10] ---> [Switch: Fa0/1] & [PC-B: .20] ---> [Switch: Fa0/2]',
                    'ip_requirements': 'Both hosts configured in 192.168.1.0/24 network.',
                    'power_poe': 'Standard mains power.'
                },
                'section_d_configuration': {
                    'device_setup': 'Assign IP 192.168.1.10 255.255.255.0 to PC-A and 192.168.1.20 255.255.255.0 to PC-B.',
                    'interface_config': 'Verify switch ports Fa0/1 and Fa0/2 are up/up.',
                    'ip_config': 'Verify neither host has an IP conflict.',
                    'network_services': 'ARP table cache operates automatically.',
                    'security_settings': 'Prevent rogue IP assignments with static DHCP reservations.',
                    'verification': 'Ping PC-B from PC-A and inspect the resulting ARP cache.'
                },
                'section_e_commands': [
                    {
                        'command': 'arp -a',
                        'syntax': 'arp -a',
                        'purpose': 'View local ARP resolution cache mapping IP addresses to physical MAC addresses.',
                        'params': '-a: displays all active cache entries',
                        'mode': 'Endpoint / Router CLI',
                        'expected_output': 'Internet Address      Physical Address      Type\n192.168.1.20          00-50-79-66-68-02     dynamic',
                        'verification_commands': ['arp -d *', 'ping 192.168.1.20'],
                        'common_errors': 'Empty ARP table indicates no recent Layer 2 communication has taken place.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'pca', 'name': 'PC-A', 'type': 'pc_workstation', 'x': 180, 'y': 220, 'ip': '192.168.1.10', 'mask': '255.255.255.0'},
                        {'id': 'pcb', 'name': 'PC-B', 'type': 'pc_workstation', 'x': 480, 'y': 220, 'ip': '192.168.1.20', 'mask': '255.255.255.0'},
                        {'id': 'sw1', 'name': 'SW-01', 'type': 'layer2_switch', 'x': 330, 'y': 220}
                    ],
                    'links': [
                        {'from': 'pca', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/1', 'cable': 'copper_straight'},
                        {'from': 'pcb', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/2', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Ping Peer Endpoint on Same Subnet',
                        'instruction': 'From PC-A, execute ping 192.168.1.20 to resolve PC-B MAC address and test connectivity.',
                        'target_device': 'pca',
                        'expected_config': {'ping_success': '192.168.1.20'},
                        'hints': [
                            'Open the CLI terminal on PC-A.',
                            'Type "ping 192.168.1.20".',
                            'Notice that the first ping triggers an ARP broadcast before echo replies arrive.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pca', 'action': 'cli_command', 'command': 'ping 192.168.1.20', 'explanation': 'Send ICMP to peer host.'}
                        ]
                    },
                    {
                        'task_id': 'task_2',
                        'title': 'Verify Resolved MAC Address in ARP Table',
                        'instruction': 'Run arp -a on PC-A to inspect the dynamically learned MAC address of PC-B.',
                        'target_device': 'pca',
                        'expected_config': {'arp_entry': '192.168.1.20'},
                        'hints': [
                            'Enter "arp -a" on PC-A.',
                            'Verify the entry for 192.168.1.20 is present.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pca', 'action': 'cli_command', 'command': 'arp -a', 'explanation': 'Display ARP cache table.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'ping_tests': [
                        {'from': 'pca', 'to': '192.168.1.20', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Duplicate IP address warning on endpoint',
                        'cause': 'Two devices assigned identical IP address on the same broadcast domain.',
                        'diagnosis': 'Run arp-scan or check DHCP lease table for conflicting static allocations.',
                        'fix': 'Change the conflicting endpoint to an unused IP address.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'How many usable host IP addresses are provided by a /24 subnet mask (255.255.255.0)?',
                        'options': [
                            {'id': 'A', 'text': '256'},
                            {'id': 'B', 'text': '254'},
                            {'id': 'C', 'text': '128'},
                            {'id': 'D', 'text': '512'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'A /24 subnet contains 2^8 = 256 total addresses. Subtracting the network address (.0) and the broadcast address (.255) leaves 254 usable host addresses.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Ethernet, Cabling & Network Devices',
        'slug': 'ethernet-cabling-devices',
        'description': 'Understand physical layer transmission, twisted-pair copper categories (Cat5e/6/6a), fiber optics, SFP modules, and the operational differences between hubs and switches.',
        'level': 'beginner',
        'category': 'foundations',
        'estimated_hours': 3.5,
        'icon': 'fa-plug',
        'badge_name': 'Certified Cabling Specialist',
        'order': 2,
        'lessons': [
            {
                'title': 'Ethernet Cabling: Cat5e/Cat6 Straight-Through vs Crossover',
                'slug': 'ethernet-cabling-types',
                'lesson_number': 1,
                'difficulty': 'beginner',
                'estimated_minutes': 25,
                'summary': 'T568A vs T568B pinouts, straight-through vs crossover cables, Auto-MDIX, and cable attenuation limits.',
                'section_a_intro': {
                    'definition': 'Twisted pair Ethernet cables utilize 4 pairs of copper conductors twisted at differing rates to cancel out electromagnetic interference (EMI) and crosstalk.',
                    'purpose': 'Provides reliable physical layer electrical signal transmission between networking equipment up to 100 meters.',
                    'why_needed': 'Physical layer transmission media is required to interconnect network devices.',
                    'where_used': 'LAN structured cabling, data center patch panels, desktop wall jacks.',
                    'real_world_examples': 'Connecting workstations to patch panels, PoE security cameras to switches.',
                    'advantages': ['Inexpensive', 'Flexible installation', 'Supports Power over Ethernet (PoE)'],
                    'limitations': ['Strict 100-meter distance limit', 'Susceptible to external high-voltage EMI']
                },
                'section_b_how_it_works': {
                    'architecture': '8 pins wired to ANSI/TIA-568-A or 568-B color-code specifications.',
                    'protocols': ['10BASE-T', '100BASE-TX', '1000BASE-T (Gigabit Ethernet)'],
                    'interfaces': ['RJ45 8P8C modular connectors', 'Keystone punch-down jacks'],
                    'data_flow': 'Pins 1&2 (Tx+/Tx-) transmit, Pins 3&6 (Rx+/Rx-) receive in Fast Ethernet; all 4 pairs used simultaneously in Gigabit.',
                    'device_interactions': 'Auto-MDIX automatically detects transmit/receive pairs and swaps them internally if the wrong cable type is used.',
                    'osi_layers': 'Layer 1 Physical.'
                },
                'section_c_connection': {
                    'required_devices': ['Switch SW-01', 'Switch SW-02'],
                    'cable_types': ['Cat6 Straight-Through with Auto-MDIX or Crossover cable'],
                    'port_selection': 'GigabitEthernet0/1 to GigabitEthernet0/1',
                    'interface_compatibility': '1000BASE-T Auto-negotiation',
                    'connection_diagram': '[SW-01: G0/1] <==== Cat6 Copper ====> [SW-02: G0/1]',
                    'ip_requirements': 'Management VLAN 1 IPs: SW-01 (192.168.1.2/24), SW-02 (192.168.1.3/24)',
                    'power_poe': 'AC Mains power.'
                },
                'section_d_configuration': {
                    'device_setup': 'Configure switch hostname and management IP.',
                    'interface_config': 'Verify duplex auto and speed auto on gigabit uplinks.',
                    'ip_config': 'Assign management SVI IP.',
                    'network_services': 'CDP/LLDP device discovery.',
                    'security_settings': 'Disable unused switchports.',
                    'verification': 'show interfaces status and show cdp neighbors.'
                },
                'section_e_commands': [
                    {
                        'command': 'show interfaces status',
                        'syntax': 'show interfaces status',
                        'purpose': 'Check physical port link state, speed, duplex, and VLAN assignment.',
                        'params': 'none',
                        'mode': 'Privileged EXEC',
                        'expected_output': 'Port      Name               Status       Vlan       Duplex  Speed Type\nGi0/1                        connected    trunk      a-full  a-1000 10/100/1000BaseTX',
                        'verification_commands': ['show interfaces GigabitEthernet 0/1'],
                        'common_errors': 'Status "notconnect" indicates disconnected cable or remote device powered off.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'sw1', 'name': 'SW-Access-01', 'type': 'layer2_switch', 'x': 200, 'y': 220},
                        {'id': 'sw2', 'name': 'SW-Access-02', 'type': 'layer2_switch', 'x': 460, 'y': 220}
                    ],
                    'links': [
                        {'from': 'sw1', 'from_port': 'Gi0/1', 'to': 'sw2', 'to_port': 'Gi0/1', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Verify Physical Uplink Link Status',
                        'instruction': 'Open SW-Access-01 CLI and execute "show interfaces status" to confirm Gi0/1 link is up.',
                        'target_device': 'sw1',
                        'expected_config': {'link_up': 'Gi0/1'},
                        'hints': [
                            'Open SW-Access-01 terminal.',
                            'Type "show interfaces status".',
                            'Check that Gi0/1 displays "connected".'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'sw1', 'action': 'cli_command', 'command': 'show interfaces status', 'explanation': 'Inspect port status.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'devices': {
                        'sw1': {'interfaces': {'Gi0/1': {'status': 'up'}}}
                    }
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Port shows err-disabled or collisions accumulating',
                        'cause': 'Duplex mismatch (one side Full, other side Half) or faulty cable.',
                        'diagnosis': 'Check show interfaces GigabitEthernet0/1 for CRC errors or run cable tester.',
                        'fix': 'Set both sides to duplex auto or replace defective Cat6 cable.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'What is the maximum certified length for a standard horizontal copper UTP Ethernet run?',
                        'options': [
                            {'id': 'A', 'text': '50 meters'},
                            {'id': 'B', 'text': '100 meters'},
                            {'id': 'C', 'text': '200 meters'},
                            {'id': 'D', 'text': '500 meters'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'The TIA/EIA 568 standard specifies a maximum total channel length of 100 meters (90m solid horizontal cable + 10m stranded patch cords).'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Switch Configuration & VLAN Administration',
        'slug': 'switch-config-vlan',
        'description': 'Configure Cisco Layer 2 switches, create IEEE 802.1Q Virtual LANs, isolate broadcast domains, configure trunk links, and implement Spanning Tree Protocol (STP).',
        'level': 'intermediate',
        'category': 'switching_routing',
        'estimated_hours': 5.0,
        'icon': 'fa-random',
        'badge_name': 'Certified Switching Administrator',
        'order': 3,
        'lessons': [
            {
                'title': 'Creating and Assigning 802.1Q Virtual LANs (VLANs)',
                'slug': 'vlan-configuration-ports',
                'lesson_number': 1,
                'difficulty': 'intermediate',
                'estimated_minutes': 30,
                'summary': 'Segment a single physical switch into multiple isolated broadcast domains using VLAN 10 (Sales) and VLAN 20 (Engineering).',
                'section_a_intro': {
                    'definition': 'A Virtual Local Area Network (VLAN) is a logical subnetwork that groups together a collection of devices from different physical LAN segments into independent broadcast domains.',
                    'purpose': 'Limits broadcast radiation, improves network security through logical segmentation, and optimizes bandwidth utilization.',
                    'why_needed': 'Without VLANs, every broadcast frame sent by any host flood to all ports on the switch, wasting CPU cycles and exposing sensitive traffic.',
                    'where_used': 'Every corporate, university, hospital, and enterprise network environment.',
                    'real_world_examples': 'Separating employee workstations, guest Wi-Fi, VoIP phones, and IP security cameras on isolated VLANs.',
                    'advantages': ['Enhanced security', 'Reduced broadcast domains', 'Simplified management', 'Cost reduction without extra physical switches'],
                    'limitations': ['Requires Layer 3 router or multilayer switch to communicate between VLANs']
                },
                'section_b_how_it_works': {
                    'architecture': 'Switch maintains separate MAC address tables or tags frames with 12-bit VLAN IDs (1 to 4094) per the IEEE 802.1Q standard.',
                    'protocols': ['IEEE 802.1Q', 'VTP (VLAN Trunking Protocol)', 'DTP'],
                    'interfaces': ['Access ports (untagged single VLAN)', 'Trunk ports (tagged multi-VLAN)'],
                    'data_flow': 'Ingress frame on access port is tagged internally with port VLAN ID. Switch only forwards the frame to egress ports belonging to the same VLAN.',
                    'device_interactions': 'Frames never cross VLAN boundaries without passing through an external Layer 3 routing engine.',
                    'osi_layers': 'Layer 2 Data Link.'
                },
                'section_c_connection': {
                    'required_devices': ['Cisco Switch SW-01', 'PC-Sales (Port Fa0/1)', 'PC-Eng (Port Fa0/2)'],
                    'cable_types': ['Cat6 Straight-Through'],
                    'port_selection': 'Fa0/1 assigned to VLAN 10; Fa0/2 assigned to VLAN 20',
                    'interface_compatibility': '10/100/1000Base-T',
                    'connection_diagram': '[PC-Sales: .10.5] ---> [SW-01: Fa0/1 (VLAN 10)] & [PC-Eng: .20.5] ---> [SW-01: Fa0/2 (VLAN 20)]',
                    'ip_requirements': 'VLAN 10: 192.168.10.0/24, VLAN 20: 192.168.20.0/24',
                    'power_poe': 'Switch standard AC power.'
                },
                'section_d_configuration': {
                    'device_setup': 'Enter global configuration mode: configure terminal',
                    'interface_config': 'Create VLANs 10 and 20 with descriptive names, then configure interface access modes.',
                    'ip_config': 'Hosts assigned respective subnet IP addresses.',
                    'network_services': 'Layer 2 isolation active.',
                    'security_settings': 'Assign unused ports to an unused dummy VLAN and shut them down.',
                    'verification': 'show vlan brief'
                },
                'section_e_commands': [
                    {
                        'command': 'vlan 10\n name SALES\nexit',
                        'syntax': 'vlan <vlan-id>\n name <name>',
                        'purpose': 'Create VLAN 10 in the switch VLAN database and give it the name SALES.',
                        'params': '<vlan-id>: 1-4094; <name>: alphanumeric string',
                        'mode': 'Global Configuration Mode',
                        'expected_output': 'SW-01(config-vlan)#',
                        'verification_commands': ['show vlan brief', 'show vlan id 10'],
                        'common_errors': 'Forgetting to exit or commit VLAN definition.'
                    },
                    {
                        'command': 'interface FastEthernet0/1\n switchport mode access\n switchport access vlan 10\n no shutdown',
                        'syntax': 'switchport mode access\nswitchport access vlan <vlan-id>',
                        'purpose': 'Assign physical port Fa0/1 to untagged membership in VLAN 10.',
                        'params': 'mode access: sets port to non-trunking end-device mode',
                        'mode': 'Interface Configuration Mode',
                        'expected_output': 'SW-01(config-if)#',
                        'verification_commands': ['show interfaces Fa0/1 switchport'],
                        'common_errors': 'Specifying a VLAN that has not been created yet (switch auto-creates it without custom name).'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'sw1', 'name': 'SW-01', 'type': 'layer2_switch', 'x': 320, 'y': 180, 'interfaces': ['Fa0/1', 'Fa0/2', 'Fa0/3', 'Gi0/1']},
                        {'id': 'pc1', 'name': 'PC-Sales-1', 'type': 'pc_workstation', 'x': 160, 'y': 280, 'ip': '192.168.10.10', 'mask': '255.255.255.0'},
                        {'id': 'pc2', 'name': 'PC-Sales-2', 'type': 'pc_workstation', 'x': 320, 'y': 280, 'ip': '192.168.10.11', 'mask': '255.255.255.0'},
                        {'id': 'pc3', 'name': 'PC-Eng-1', 'type': 'pc_workstation', 'x': 480, 'y': 280, 'ip': '192.168.20.10', 'mask': '255.255.255.0'}
                    ],
                    'links': [
                        {'from': 'pc1', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/1', 'cable': 'copper_straight'},
                        {'from': 'pc2', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/2', 'cable': 'copper_straight'},
                        {'from': 'pc3', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/3', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Create VLAN 10 and VLAN 20 on SW-01',
                        'instruction': 'Access SW-01 CLI, enter config mode, create "vlan 10" with name "SALES", and "vlan 20" with name "ENG".',
                        'target_device': 'sw1',
                        'expected_config': {'vlans': [10, 20]},
                        'hints': [
                            'Open SW-01 terminal and enter privileged EXEC mode: "enable", then "configure terminal".',
                            'Run "vlan 10", then "name SALES", then "vlan 20", then "name ENG".',
                            'Use "show vlan brief" to verify both VLANs exist in the switch database.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'sw1', 'action': 'cli_command', 'command': 'enable', 'explanation': 'Enter privileged mode.'},
                            {'step': 2, 'device': 'sw1', 'action': 'cli_command', 'command': 'configure terminal', 'explanation': 'Enter config mode.'},
                            {'step': 3, 'device': 'sw1', 'action': 'cli_command', 'command': 'vlan 10', 'explanation': 'Create VLAN 10.'},
                            {'step': 4, 'device': 'sw1', 'action': 'cli_command', 'command': 'name SALES', 'explanation': 'Name VLAN SALES.'},
                            {'step': 5, 'device': 'sw1', 'action': 'cli_command', 'command': 'vlan 20', 'explanation': 'Create VLAN 20.'},
                            {'step': 6, 'device': 'sw1', 'action': 'cli_command', 'command': 'name ENG', 'explanation': 'Name VLAN ENG.'}
                        ]
                    },
                    {
                        'task_id': 'task_2',
                        'title': 'Assign Switch Ports to Respective VLANs',
                        'instruction': 'Assign Fa0/1 and Fa0/2 to VLAN 10 (Sales), and Fa0/3 to VLAN 20 (Engineering).',
                        'target_device': 'sw1',
                        'expected_config': {
                            'ports': {'Fa0/1': 10, 'Fa0/2': 10, 'Fa0/3': 20}
                        },
                        'hints': [
                            'Configure interface Fa0/1: "switchport mode access", then "switchport access vlan 10".',
                            'Repeat for Fa0/2 with vlan 10, and Fa0/3 with vlan 20.',
                            'Verify with "show vlan brief".'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'sw1', 'action': 'cli_command', 'command': 'interface FastEthernet0/1', 'explanation': 'Select Fa0/1.'},
                            {'step': 2, 'device': 'sw1', 'action': 'cli_command', 'command': 'switchport access vlan 10', 'explanation': 'Assign to VLAN 10.'},
                            {'step': 3, 'device': 'sw1', 'action': 'cli_command', 'command': 'interface FastEthernet0/2', 'explanation': 'Select Fa0/2.'},
                            {'step': 4, 'device': 'sw1', 'action': 'cli_command', 'command': 'switchport access vlan 10', 'explanation': 'Assign to VLAN 10.'},
                            {'step': 5, 'device': 'sw1', 'action': 'cli_command', 'command': 'interface FastEthernet0/3', 'explanation': 'Select Fa0/3.'},
                            {'step': 6, 'device': 'sw1', 'action': 'cli_command', 'command': 'switchport access vlan 20', 'explanation': 'Assign to VLAN 20.'}
                        ]
                    },
                    {
                        'task_id': 'task_3',
                        'title': 'Verify Inter-VLAN Isolation',
                        'instruction': 'Confirm PC-Sales-1 can ping PC-Sales-2 (both on VLAN 10), but CANNOT ping PC-Eng-1 (VLAN 20).',
                        'target_device': 'pc1',
                        'expected_config': {'isolation_verified': True},
                        'hints': [
                            'From PC-Sales-1, ping 192.168.10.11 (should succeed).',
                            'From PC-Sales-1, ping 192.168.20.10 (should fail/timeout due to Layer 2 isolation).'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc1', 'action': 'cli_command', 'command': 'ping 192.168.10.11', 'explanation': 'Ping peer on same VLAN 10.'},
                            {'step': 2, 'device': 'pc1', 'action': 'cli_command', 'command': 'ping 192.168.20.10', 'explanation': 'Test ping to isolated VLAN 20.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'devices': {
                        'sw1': {
                            'vlans': [10, 20],
                            'interfaces': {
                                'Fa0/1': {'vlan': 10, 'mode': 'access'},
                                'Fa0/2': {'vlan': 10, 'mode': 'access'},
                                'Fa0/3': {'vlan': 20, 'mode': 'access'}
                            }
                        }
                    },
                    'ping_tests': [
                        {'from': 'pc1', 'to': '192.168.10.11', 'expect': 'success'},
                        {'from': 'pc1', 'to': '192.168.20.10', 'expect': 'drop'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Hosts on the same VLAN cannot ping each other',
                        'cause': 'One of the switch ports is assigned to the wrong VLAN or is in shutdown state.',
                        'diagnosis': 'Execute "show vlan brief" to check port memberships and "show interfaces status".',
                        'fix': 'Reassign the port to the correct VLAN: "switchport access vlan 10".'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'What standard defines Virtual LAN tagging on Ethernet frames?',
                        'options': [
                            {'id': 'A', 'text': 'IEEE 802.1D'},
                            {'id': 'B', 'text': 'IEEE 802.1Q'},
                            {'id': 'C', 'text': 'IEEE 802.3ab'},
                            {'id': 'D', 'text': 'IEEE 802.11ac'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'IEEE 802.1Q is the industry standard for VLAN tagging, inserting a 4-byte tag into the Ethernet frame header containing a 12-bit VLAN identifier.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Router Configuration & IP Subnetting',
        'slug': 'router-config-subnetting',
        'description': 'Configure Cisco router interfaces, establish subnet boundaries, implement static routing, calculate network/broadcast addresses, and resolve default gateways.',
        'level': 'beginner',
        'category': 'switching_routing',
        'estimated_hours': 4.5,
        'icon': 'fa-route',
        'badge_name': 'Certified Routing Associate',
        'order': 4,
        'lessons': [
            {
                'title': 'Router Interface Configuration & Subnet Gateways',
                'slug': 'router-interface-config',
                'lesson_number': 1,
                'difficulty': 'beginner',
                'estimated_minutes': 30,
                'summary': 'Configure Cisco GigabitEthernet interfaces with IP addresses, activate ports with "no shutdown", and establish default gateways.',
                'section_a_intro': {
                    'definition': 'A router is a Layer 3 networking device that forwards data packets between disparate computer networks based on IP destination addresses.',
                    'purpose': 'Connects separate local area networks together and provides access to wide area networks (WANs) and the Internet.',
                    'why_needed': 'Switches cannot route between different IP subnets. Routers act as default gateways to inspect IP headers and choose optimal forwarding paths.',
                    'where_used': 'Every branch office, campus border, home broadband gateway, and ISP backbone.',
                    'real_world_examples': 'Cisco ISR 4000 series branch routers connecting office LANs to MPLS and Internet uplinks.',
                    'advantages': ['Broadcast domain containment', 'Dynamic path selection', 'NAT and firewall integration'],
                    'limitations': ['Higher latency per packet than hardware Layer 2 switching', 'Requires IP planning and routing table maintenance']
                },
                'section_b_how_it_works': {
                    'architecture': 'Router maintains a Routing Information Base (RIB) and Forwarding Information Base (FIB) to perform longest-prefix-match IP lookups.',
                    'protocols': ['IPv4', 'ICMP', 'ARP', 'OSPF', 'BGP'],
                    'interfaces': ['GigabitEthernet', 'Serial WAN', 'SVI', 'Sub-interfaces'],
                    'data_flow': 'Ingress frame -> L2 CRC check -> Decapsulate frame -> Inspect L3 destination IP -> RIB lookup -> Decrement TTL -> Encapsulate with next-hop MAC -> Egress.',
                    'device_interactions': 'Endpoints send all off-subnet traffic to the router interface MAC address resolved via ARP.',
                    'osi_layers': 'Layer 3 Network Layer.'
                },
                'section_c_connection': {
                    'required_devices': ['Cisco Router RTR-01', 'LAN-1 Switch', 'LAN-2 Switch'],
                    'cable_types': ['Cat6 Straight-Through cables'],
                    'port_selection': 'RTR-01 g0/0 to LAN-1; RTR-01 g0/1 to LAN-2',
                    'interface_compatibility': '1000BASE-T',
                    'connection_diagram': '[LAN-1: 192.168.1.0/24] <--- g0/0 --- [RTR-01] --- g0/1 ---> [LAN-2: 192.168.2.0/24]',
                    'ip_requirements': 'g0/0: 192.168.1.1/24; g0/1: 192.168.2.1/24',
                    'power_poe': 'AC Mains power.'
                },
                'section_d_configuration': {
                    'device_setup': 'Set hostname RTR-01 and disable DNS lookup.',
                    'interface_config': 'Assign IP addresses to g0/0 and g0/1 and enable interfaces with "no shutdown".',
                    'ip_config': 'Ensure proper subnet masks (255.255.255.0).',
                    'network_services': 'Directly connected routes automatically populate the routing table.',
                    'security_settings': 'Configure console and vty passwords.',
                    'verification': 'show ip interface brief and show ip route.'
                },
                'section_e_commands': [
                    {
                        'command': 'interface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\n no shutdown',
                        'syntax': 'ip address <ip> <mask>\nno shutdown',
                        'purpose': 'Assign IPv4 address to router interface and change administrative state from shutdown to UP.',
                        'params': '<ip>: interface IPv4 address; <mask>: dotted decimal subnet mask',
                        'mode': 'Interface Configuration Mode',
                        'expected_output': '%LINK-3-UPDOWN: Interface GigabitEthernet0/0, changed state to up',
                        'verification_commands': ['show ip interface brief'],
                        'common_errors': 'Forgetting "no shutdown" leaves interface in "administratively down" state.'
                    },
                    {
                        'command': 'show ip route',
                        'syntax': 'show ip route',
                        'purpose': 'Display active IPv4 routing table containing connected, static, and dynamic routes.',
                        'params': 'none',
                        'mode': 'Privileged EXEC Mode',
                        'expected_output': 'Codes: C - connected, S - static, O - OSPF\nC    192.168.1.0/24 is directly connected, GigabitEthernet0/0\nC    192.168.2.0/24 is directly connected, GigabitEthernet0/1',
                        'verification_commands': ['show ip route connected'],
                        'common_errors': 'Missing route indicates interface is down or mask is misconfigured.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'rtr1', 'name': 'RTR-01', 'type': 'router', 'x': 340, 'y': 150, 'interfaces': ['g0/0', 'g0/1']},
                        {'id': 'pc1', 'name': 'PC-Dept-A', 'type': 'pc_workstation', 'x': 160, 'y': 280, 'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                        {'id': 'pc2', 'name': 'PC-Dept-B', 'type': 'pc_workstation', 'x': 520, 'y': 280, 'ip': '192.168.2.10', 'mask': '255.255.255.0', 'gateway': '192.168.2.1'}
                    ],
                    'links': [
                        {'from': 'pc1', 'from_port': 'eth0', 'to': 'rtr1', 'to_port': 'g0/0', 'cable': 'copper_straight'},
                        {'from': 'pc2', 'from_port': 'eth0', 'to': 'rtr1', 'to_port': 'g0/1', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Configure Router Interfaces g0/0 and g0/1',
                        'instruction': 'On RTR-01, configure g0/0 with 192.168.1.1/24 and g0/1 with 192.168.2.1/24, enabling both with "no shutdown".',
                        'target_device': 'rtr1',
                        'expected_config': {
                            'interfaces': {
                                'g0/0': {'ip': '192.168.1.1', 'mask': '255.255.255.0', 'status': 'up'},
                                'g0/1': {'ip': '192.168.2.1', 'mask': '255.255.255.0', 'status': 'up'}
                            }
                        },
                        'hints': [
                            'Enter "enable", then "configure terminal".',
                            'Select "interface g0/0", run "ip address 192.168.1.1 255.255.255.0" and "no shutdown".',
                            'Select "interface g0/1", run "ip address 192.168.2.1 255.255.255.0" and "no shutdown".'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'rtr1', 'action': 'cli_command', 'command': 'enable', 'explanation': 'Privileged mode.'},
                            {'step': 2, 'device': 'rtr1', 'action': 'cli_command', 'command': 'configure terminal', 'explanation': 'Global config.'},
                            {'step': 3, 'device': 'rtr1', 'action': 'cli_command', 'command': 'interface g0/0', 'explanation': 'Select g0/0.'},
                            {'step': 4, 'device': 'rtr1', 'action': 'cli_command', 'command': 'ip address 192.168.1.1 255.255.255.0', 'explanation': 'Set IP.'},
                            {'step': 5, 'device': 'rtr1', 'action': 'cli_command', 'command': 'no shutdown', 'explanation': 'Bring up interface.'},
                            {'step': 6, 'device': 'rtr1', 'action': 'cli_command', 'command': 'interface g0/1', 'explanation': 'Select g0/1.'},
                            {'step': 7, 'device': 'rtr1', 'action': 'cli_command', 'command': 'ip address 192.168.2.1 255.255.255.0', 'explanation': 'Set IP.'},
                            {'step': 8, 'device': 'rtr1', 'action': 'cli_command', 'command': 'no shutdown', 'explanation': 'Bring up interface.'}
                        ]
                    },
                    {
                        'task_id': 'task_2',
                        'title': 'Verify Cross-Subnet Routing Between PC-Dept-A and PC-Dept-B',
                        'instruction': 'From PC-Dept-A (192.168.1.10), ping PC-Dept-B (192.168.2.10) across the router.',
                        'target_device': 'pc1',
                        'expected_config': {'ping_success': '192.168.2.10'},
                        'hints': [
                            'Open terminal on PC-Dept-A.',
                            'Execute "ping 192.168.2.10".',
                            'Verify all 4 echo packets reply successfully.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc1', 'action': 'cli_command', 'command': 'ping 192.168.2.10', 'explanation': 'Ping remote subnet endpoint.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'devices': {
                        'rtr1': {
                            'interfaces': {
                                'g0/0': {'ip': '192.168.1.1', 'status': 'up'},
                                'g0/1': {'ip': '192.168.2.1', 'status': 'up'}
                            }
                        }
                    },
                    'ping_tests': [
                        {'from': 'pc1', 'to': '192.168.2.10', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Endpoint cannot ping default gateway',
                        'cause': 'Wrong gateway IP configured on endpoint, or router interface is administratively down.',
                        'diagnosis': 'Execute "show ip interface brief" on router and "ipconfig" on endpoint.',
                        'fix': 'Correct the endpoint default gateway and run "no shutdown" on the router interface.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'What happens to the TTL (Time to Live) field in an IPv4 packet header when a router forwards it?',
                        'options': [
                            {'id': 'A', 'text': 'It is incremented by 1'},
                            {'id': 'B', 'text': 'It is decremented by 1'},
                            {'id': 'C', 'text': 'It remains completely unchanged'},
                            {'id': 'D', 'text': 'It is reset to 255'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'Every Layer 3 router decrements the TTL field by 1. If TTL reaches 0, the packet is discarded and an ICMP Time Exceeded message is returned, preventing infinite routing loops.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Routing Protocols (Static & Dynamic)',
        'slug': 'routing-protocols-static-dynamic',
        'description': 'Implement static routes, default quad-zero routes (0.0.0.0/0), router-on-a-stick inter-VLAN routing, and Open Shortest Path First (OSPF) dynamic routing.',
        'level': 'intermediate',
        'category': 'switching_routing',
        'estimated_hours': 5.5,
        'icon': 'fa-project-diagram',
        'badge_name': 'Certified Routing Professional',
        'order': 5,
        'lessons': [
            {
                'title': 'Static Routes & Default Gateway Routing (0.0.0.0/0)',
                'slug': 'static-routing-default-routes',
                'lesson_number': 1,
                'difficulty': 'intermediate',
                'estimated_minutes': 30,
                'summary': 'Configure next-hop static routes and default routes (gateway of last resort) between multi-router topologies.',
                'section_a_intro': {
                    'definition': 'A static route is a manually entered path into a router routing table that explicitly defines the next-hop IP address or exit interface for a specific destination network.',
                    'purpose': 'Provides deterministic, low-overhead routing between stub networks and defines the default route to the ISP.',
                    'why_needed': 'Without a matching route in the routing table, a router drops unroutable packets and sends an ICMP Destination Net Unreachable message.',
                    'where_used': 'Branch office uplinks, ISP edge routers, point-to-point leased line circuits.',
                    'real_world_examples': 'Enterprise edge router pointing 0.0.0.0/0 to the ISP peering IP.',
                    'advantages': ['Zero bandwidth overhead (no routing protocol advertisements)', 'Predictable traffic paths', 'High security'],
                    'limitations': ['No automatic failover if the next-hop link drops', 'Unscalable in large, complex topologies']
                },
                'section_b_how_it_works': {
                    'architecture': 'Static routes have an administrative distance of 1, taking precedence over dynamic routing protocols like OSPF (AD 110).',
                    'protocols': ['Static IPv4', 'ICMP'],
                    'interfaces': ['Serial point-to-point', 'GigabitEthernet uplinks'],
                    'data_flow': 'Router matches packet destination IP against static route mask. If matched, resolves next-hop ARP MAC and transmits out egress port.',
                    'device_interactions': 'Two interconnected routers forward packets bidirectionally once reciprocal static routes are configured.',
                    'osi_layers': 'Layer 3 Network.'
                },
                'section_c_connection': {
                    'required_devices': ['Router RTR-Branch', 'Router RTR-HQ'],
                    'cable_types': ['Cat6 Straight-Through or Fiber patch'],
                    'port_selection': 'RTR-Branch g0/1 to RTR-HQ g0/0 (Inter-router WAN: 10.0.0.0/30)',
                    'interface_compatibility': '1000BASE-T',
                    'connection_diagram': '[Branch LAN: 192.168.10.0/24] --- [RTR-Branch] <=== WAN: 10.0.0.0/30 ===> [RTR-HQ] --- [HQ LAN: 192.168.20.0/24]',
                    'ip_requirements': 'Branch WAN: 10.0.0.1/30, HQ WAN: 10.0.0.2/30',
                    'power_poe': 'AC Mains power.'
                },
                'section_d_configuration': {
                    'device_setup': 'Configure IP addresses on all LAN and WAN interfaces.',
                    'interface_config': 'Ensure all serial/ethernet links are no shutdown.',
                    'ip_config': 'Add static route on Branch: ip route 192.168.20.0 255.255.255.0 10.0.0.2',
                    'network_services': 'Add reciprocal route on HQ: ip route 192.168.10.0 255.255.255.0 10.0.0.1',
                    'security_settings': 'Filter unapproved subnets.',
                    'verification': 'show ip route static and end-to-end ping.'
                },
                'section_e_commands': [
                    {
                        'command': 'ip route 192.168.20.0 255.255.255.0 10.0.0.2',
                        'syntax': 'ip route <destination_network> <subnet_mask> <next_hop_ip>',
                        'purpose': 'Add a static route to the routing table instructing the router to forward traffic for 192.168.20.0/24 to next-hop 10.0.0.2.',
                        'params': '<dest>: network IP; <mask>: subnet mask; <next_hop>: adjacent router interface IP',
                        'mode': 'Global Configuration Mode',
                        'expected_output': 'RTR(config)#',
                        'verification_commands': ['show ip route static'],
                        'common_errors': 'Configuring one-way static route causes packets to reach destination but replies cannot return.'
                    },
                    {
                        'command': 'ip route 0.0.0.0 0.0.0.0 10.0.0.2',
                        'syntax': 'ip route 0.0.0.0 0.0.0.0 <next_hop_ip>',
                        'purpose': 'Configure default route (gateway of last resort) matching any destination not explicitly listed in the routing table.',
                        'params': '0.0.0.0 0.0.0.0 matches all destination IPs',
                        'mode': 'Global Configuration Mode',
                        'expected_output': 'RTR(config)#',
                        'verification_commands': ['show ip route | include Gateway of last resort'],
                        'common_errors': 'Specifying an unreachable next-hop IP prevents route from entering the routing table.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'rtr_br', 'name': 'RTR-Branch', 'type': 'router', 'x': 200, 'y': 160, 'interfaces': ['g0/0', 'g0/1']},
                        {'id': 'rtr_hq', 'name': 'RTR-HQ', 'type': 'router', 'x': 460, 'y': 160, 'interfaces': ['g0/0', 'g0/1']},
                        {'id': 'pc_br', 'name': 'PC-Branch', 'type': 'pc_workstation', 'x': 100, 'y': 280, 'ip': '192.168.10.5', 'mask': '255.255.255.0', 'gateway': '192.168.10.1'},
                        {'id': 'pc_hq', 'name': 'PC-HQ', 'type': 'pc_workstation', 'x': 560, 'y': 280, 'ip': '192.168.20.5', 'mask': '255.255.255.0', 'gateway': '192.168.20.1'}
                    ],
                    'links': [
                        {'from': 'pc_br', 'from_port': 'eth0', 'to': 'rtr_br', 'to_port': 'g0/0', 'cable': 'copper_straight'},
                        {'from': 'rtr_br', 'from_port': 'g0/1', 'to': 'rtr_hq', 'to_port': 'g0/0', 'cable': 'copper_straight'},
                        {'from': 'rtr_hq', 'from_port': 'g0/1', 'to': 'pc_hq', 'to_port': 'eth0', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Configure Static Route on RTR-Branch',
                        'instruction': 'On RTR-Branch, add a static route for network 192.168.20.0/24 via next-hop 10.0.0.2.',
                        'target_device': 'rtr_br',
                        'expected_config': {'static_routes': [{'network': '192.168.20.0', 'next_hop': '10.0.0.2'}]},
                        'hints': [
                            'Open RTR-Branch terminal and enter config mode.',
                            'Type "ip route 192.168.20.0 255.255.255.0 10.0.0.2".',
                            'Check with "show ip route static".'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'rtr_br', 'action': 'cli_command', 'command': 'enable', 'explanation': 'Privileged mode.'},
                            {'step': 2, 'device': 'rtr_br', 'action': 'cli_command', 'command': 'configure terminal', 'explanation': 'Config mode.'},
                            {'step': 3, 'device': 'rtr_br', 'action': 'cli_command', 'command': 'ip route 192.168.20.0 255.255.255.0 10.0.0.2', 'explanation': 'Add static route.'}
                        ]
                    },
                    {
                        'task_id': 'task_2',
                        'title': 'Configure Reciprocal Static Route on RTR-HQ',
                        'instruction': 'On RTR-HQ, add a static route for network 192.168.10.0/24 via next-hop 10.0.0.1.',
                        'target_device': 'rtr_hq',
                        'expected_config': {'static_routes': [{'network': '192.168.10.0', 'next_hop': '10.0.0.1'}]},
                        'hints': [
                            'Open RTR-HQ terminal and enter config mode.',
                            'Type "ip route 192.168.10.0 255.255.255.0 10.0.0.1".',
                            'Routing must be bidirectional for ICMP replies to succeed.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'rtr_hq', 'action': 'cli_command', 'command': 'enable', 'explanation': 'Privileged mode.'},
                            {'step': 2, 'device': 'rtr_hq', 'action': 'cli_command', 'command': 'configure terminal', 'explanation': 'Config mode.'},
                            {'step': 3, 'device': 'rtr_hq', 'action': 'cli_command', 'command': 'ip route 192.168.10.0 255.255.255.0 10.0.0.1', 'explanation': 'Add reciprocal route.'}
                        ]
                    },
                    {
                        'task_id': 'task_3',
                        'title': 'Test End-to-End Connectivity Across Routers',
                        'instruction': 'From PC-Branch (192.168.10.5), ping PC-HQ (192.168.20.5).',
                        'target_device': 'pc_br',
                        'expected_config': {'ping_success': '192.168.20.5'},
                        'hints': [
                            'Open PC-Branch terminal and run "ping 192.168.20.5".',
                            'Verify all packets are answered.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc_br', 'action': 'cli_command', 'command': 'ping 192.168.20.5', 'explanation': 'End to end ping.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'devices': {
                        'rtr_br': {'static_routes': [{'network': '192.168.20.0', 'next_hop': '10.0.0.2'}]},
                        'rtr_hq': {'static_routes': [{'network': '192.168.10.0', 'next_hop': '10.0.0.1'}]}
                    },
                    'ping_tests': [
                        {'from': 'pc_br', 'to': '192.168.20.5', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Ping times out between subnets',
                        'cause': 'One of the routers lacks a return route back to the sender subnet.',
                        'diagnosis': 'Execute "show ip route" on both routers and verify presence of destination subnet.',
                        'fix': 'Add the missing reciprocal static route on the remote router.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'What is the default Administrative Distance (AD) of a directly connected route in Cisco IOS?',
                        'options': [
                            {'id': 'A', 'text': '0'},
                            {'id': 'B', 'text': '1'},
                            {'id': 'C', 'text': '90'},
                            {'id': 'D', 'text': '110'}
                        ],
                        'correct_answer': 'A',
                        'explanation': 'Directly connected routes have an administrative distance of 0 (most trustworthy). Static routes have an AD of 1.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Network Security & Firewall Administration',
        'slug': 'network-security-firewall',
        'description': 'Deploy stateful packet inspection firewalls, configure Standard/Extended Access Control Lists (ACLs), establish DMZ zones, and configure Port Address Translation (PAT).',
        'level': 'intermediate',
        'category': 'security',
        'estimated_hours': 5.0,
        'icon': 'fa-shield-halved',
        'badge_name': 'Certified Security Engineer',
        'order': 6,
        'lessons': [
            {
                'title': 'Stateful Firewall Inspection & Access Control Lists (ACL)',
                'slug': 'stateful-firewall-acl',
                'lesson_number': 1,
                'difficulty': 'intermediate',
                'estimated_minutes': 30,
                'summary': 'Configure packet filtering rules to allow outbound HTTP/DNS from Inside to Outside while dropping unsolicited inbound connection attempts.',
                'section_a_intro': {
                    'definition': 'A firewall is a network security system that monitors and controls incoming and outgoing network traffic based on predetermined security rules.',
                    'purpose': 'Establishes a barrier between a trusted internal network and an untrusted external network (such as the Internet).',
                    'why_needed': 'Prevents unauthorized external access, blocks malicious port scanning, and isolates compromised subnets.',
                    'where_used': 'Perimeter boundaries, datacenter demilitarized zones (DMZ), branch offices.',
                    'real_world_examples': 'Fortinet FortiGate, Cisco ASA/Firepower, pfSense, iptables.',
                    'advantages': ['Stateful session tracking', 'Deep packet inspection', 'NAT integration'],
                    'limitations': ['Can become a throughput bottleneck without hardware ASIC acceleration']
                },
                'section_b_how_it_works': {
                    'architecture': 'Stateful firewalls maintain a state connection table (conntrack). When an inside host initiates a TCP handshake, return traffic is automatically permitted.',
                    'protocols': ['TCP 3-way handshake', 'UDP pseudo-sessions', 'ICMP tracking'],
                    'interfaces': ['Inside (trusted)', 'Outside (untrusted)', 'DMZ (semi-trusted)'],
                    'data_flow': 'Packet arrives -> Checked against active state table -> If existing session, permit -> If new session, evaluate ACL top-to-bottom -> Explicit permit or implicit deny.',
                    'device_interactions': 'Firewall acts as the default gateway for inside hosts, inspecting every routed packet.',
                    'osi_layers': 'Layer 3 through Layer 7.'
                },
                'section_c_connection': {
                    'required_devices': ['Stateful Firewall FW-01', 'Inside PC', 'Outside Web Server'],
                    'cable_types': ['Cat6 Straight-Through'],
                    'port_selection': 'Inside: eth1 (192.168.1.1); Outside: eth0 (203.0.113.1)',
                    'interface_compatibility': '1000BASE-T',
                    'connection_diagram': '[Inside LAN: 192.168.1.0/24] --- (eth1) [FW-01] (eth0) --- [Outside Web: 203.0.113.100]',
                    'ip_requirements': 'Inside IP: 192.168.1.10/24; Outside IP: 203.0.113.100/24',
                    'power_poe': 'AC Mains power.'
                },
                'section_d_configuration': {
                    'device_setup': 'Assign interfaces to security zones (Inside vs Outside).',
                    'interface_config': 'Set IP addresses and bring up interfaces.',
                    'ip_config': 'Enable NAT/PAT for inside hosts to traverse perimeter.',
                    'network_services': 'Create stateful rule allowing HTTP (TCP 80) and ICMP outbound.',
                    'security_settings': 'Default drop all unsolicited traffic from Outside to Inside.',
                    'verification': 'Verify connection table entries with show firewall connections.'
                },
                'section_e_commands': [
                    {
                        'command': 'firewall rule add chain=FORWARD action=accept src=192.168.1.0/24 dst=0.0.0.0/0 protocol=tcp dport=80',
                        'syntax': 'firewall rule add [options]',
                        'purpose': 'Allow inside clients to initiate outbound HTTP traffic to web servers.',
                        'params': 'chain=FORWARD: routed packets; action=accept; dport=80: HTTP destination port',
                        'mode': 'Firewall CLI',
                        'expected_output': 'Rule added successfully. Position: 1',
                        'verification_commands': ['show firewall rules', 'show firewall conntrack'],
                        'common_errors': 'Placing an explicit drop rule above the permit rule stops matching before evaluation.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'fw1', 'name': 'FW-Perimeter', 'type': 'firewall', 'x': 320, 'y': 180, 'interfaces': ['eth0', 'eth1']},
                        {'id': 'pc_in', 'name': 'PC-Inside', 'type': 'pc_workstation', 'x': 140, 'y': 260, 'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                        {'id': 'srv_web', 'name': 'SRV-Web-Outside', 'type': 'web_server', 'x': 500, 'y': 260, 'ip': '203.0.113.100', 'mask': '255.255.255.0', 'gateway': '203.0.113.1'}
                    ],
                    'links': [
                        {'from': 'pc_in', 'from_port': 'eth0', 'to': 'fw1', 'to_port': 'eth1', 'cable': 'copper_straight'},
                        {'from': 'fw1', 'from_port': 'eth0', 'to': 'srv_web', 'to_port': 'eth0', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Verify Firewall Permitting Outbound Traffic',
                        'instruction': 'From PC-Inside, initiate ping to SRV-Web-Outside (203.0.113.100) to confirm outbound stateful inspection.',
                        'target_device': 'pc_in',
                        'expected_config': {'ping_success': '203.0.113.100'},
                        'hints': [
                            'Open terminal on PC-Inside.',
                            'Execute "ping 203.0.113.100".',
                            'Observe firewall conntrack state tracking the outbound ICMP sequence.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc_in', 'action': 'cli_command', 'command': 'ping 203.0.113.100', 'explanation': 'Send outbound ping.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'ping_tests': [
                        {'from': 'pc_in', 'to': '203.0.113.100', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'All outbound traffic blocked',
                        'cause': 'Implicit deny rule blocking traffic because no permit rule matched.',
                        'diagnosis': 'Check firewall logs for dropped packet events.',
                        'fix': 'Add an explicit permit rule for required port/protocol.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'What is the primary advantage of a stateful firewall over a stateless packet filter?',
                        'options': [
                            {'id': 'A', 'text': 'It automatically tracks active connections and allows established return traffic without explicit inbound rules'},
                            {'id': 'B', 'text': 'It is always cheaper to manufacture'},
                            {'id': 'C', 'text': 'It requires no configuration rules'},
                            {'id': 'D', 'text': 'It replaces all Layer 2 switches'}
                        ],
                        'correct_answer': 'A',
                        'explanation': 'Stateful firewalls maintain connection tables tracking TCP sequence numbers and port pairs, permitting legitimate return traffic automatically.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Wireless Networking & Access Points',
        'slug': 'wireless-networking-ap',
        'description': 'Deploy enterprise Wi-Fi 6 (802.11ax) access points, configure SSIDs, 802.1Q VLAN mapping, WPA2/WPA3 Enterprise authentication, and RF channel allocation.',
        'level': 'intermediate',
        'category': 'infrastructure',
        'estimated_hours': 4.0,
        'icon': 'fa-wifi',
        'badge_name': 'Certified Wireless Specialist',
        'order': 7,
        'lessons': [
            {
                'title': 'Enterprise Access Point Configuration & Multi-SSID VLAN Mapping',
                'slug': 'enterprise-ap-multi-ssid',
                'lesson_number': 1,
                'difficulty': 'intermediate',
                'estimated_minutes': 25,
                'summary': 'Configure dual-band 2.4GHz/5GHz Access Points mapping Corporate SSID to VLAN 10 and Guest SSID to VLAN 30.',
                'section_a_intro': {
                    'definition': 'A Wireless Access Point (WAP) is a networking hardware device that allows Wi-Fi client devices to connect to a wired network using 802.11 radio frequencies.',
                    'purpose': 'Provides untethered high-speed mobile network access across offices, campuses, and homes.',
                    'why_needed': 'Mobile laptops, tablets, and smartphones require reliable wireless connectivity without physical cabling.',
                    'where_used': 'Ceiling-mounted in offices, hospitality, auditoriums, outdoor campuses.',
                    'real_world_examples': 'Cisco Catalyst 9100 series, Aruba AP-500 series, Ubiquiti UniFi U6-Pro.',
                    'advantages': ['User mobility', 'Eliminates desktop patch cables', 'Multi-SSID tenant segmentation'],
                    'limitations': ['Radio frequency interference', 'Shared wireless medium contention (CSMA/CA)']
                },
                'section_b_how_it_works': {
                    'architecture': 'AP bridges 802.11 wireless frames into 802.3 Ethernet frames, tagging each SSID onto the appropriate 802.1Q VLAN trunk.',
                    'protocols': ['802.11a/b/g/n/ac/ax (Wi-Fi 6)', 'WPA3-Enterprise', 'EAP-TLS', 'RADIUS'],
                    'interfaces': ['GigabitEthernet PoE port', '2.4 GHz Radio', '5 GHz Radio'],
                    'data_flow': 'Client associates to SSID -> 4-way WPA handshake -> AP tags frame with VLAN 10 -> Switch forwards onto wired LAN.',
                    'device_interactions': 'AP is powered via PoE switch port (802.3af/at) and connected to a trunk port.',
                    'osi_layers': 'Layer 1 (RF) and Layer 2 (MAC).'
                },
                'section_c_connection': {
                    'required_devices': ['Wireless Access Point AP-01', 'PoE Switch SW-PoE', 'Laptop Client'],
                    'cable_types': ['Cat6 UTP with PoE Power (802.3at 30W)'],
                    'port_selection': 'Switch port Fa0/24 (PoE Enabled Trunk) to AP Uplink port',
                    'interface_compatibility': '1000BASE-T PoE+',
                    'connection_diagram': '[Laptop: Wi-Fi] ~~~ 5GHz ~~~> [AP-01] <=== Cat6 PoE ===> [PoE Switch: Fa0/24]',
                    'ip_requirements': 'AP Management IP: 192.168.1.50/24; Corporate SSID: 192.168.10.0/24',
                    'power_poe': 'PoE+ 802.3at providing 25.5W power budget.'
                },
                'section_d_configuration': {
                    'device_setup': 'Configure AP hostname, management IP, and default gateway.',
                    'interface_config': 'Create SSID "Corp-Secure" (VLAN 10, WPA2-PSK) and "Guest-WiFi" (VLAN 30, Open/Portal).',
                    'ip_config': 'Ensure DHCP scopes are active on VLAN 10 and 30.',
                    'network_services': 'Enable 20MHz/40MHz channel width and non-overlapping channels (1, 6, 11 on 2.4GHz).',
                    'security_settings': 'Enable Client Isolation on Guest SSID.',
                    'verification': 'Verify client association and IP lease acquisition.'
                },
                'section_e_commands': [
                    {
                        'command': 'wireless ssid add name="Corp-Secure" vlan=10 security=wpa2-psk key="SecurePass123"',
                        'syntax': 'wireless ssid add [parameters]',
                        'purpose': 'Create wireless network mapping to VLAN 10 with WPA2 pre-shared key encryption.',
                        'params': 'name: broadcast SSID string; vlan: 802.1Q tag; key: encryption passphrase',
                        'mode': 'AP Configuration Mode',
                        'expected_output': 'SSID "Corp-Secure" enabled on 2.4GHz and 5GHz radios.',
                        'verification_commands': ['show wireless clients', 'show wireless ap status'],
                        'common_errors': 'Wrong VLAN tag leaves wireless clients unable to receive DHCP leases.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'ap1', 'name': 'AP-Office-01', 'type': 'wireless_ap', 'x': 320, 'y': 160, 'ip': '192.168.1.50'},
                        {'id': 'sw1', 'name': 'SW-PoE-01', 'type': 'poe_switch', 'x': 320, 'y': 280},
                        {'id': 'lap1', 'name': 'Laptop-User', 'type': 'laptop', 'x': 140, 'y': 160, 'ip': '192.168.10.25', 'gateway': '192.168.10.1'}
                    ],
                    'links': [
                        {'from': 'sw1', 'from_port': 'Gi0/24', 'to': 'ap1', 'to_port': 'eth0', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Verify AP Power & Link State',
                        'instruction': 'Verify AP-Office-01 has established PoE power link and is operational.',
                        'target_device': 'ap1',
                        'expected_config': {'status': 'active'},
                        'hints': [
                            'Check AP status in device inspector.',
                            'Verify PoE switch port provides required wattage.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'ap1', 'action': 'select', 'explanation': 'Inspect AP status.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'devices': {
                        'ap1': {'status': 'active'}
                    }
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'AP will not power on',
                        'cause': 'Connected switch port lacks PoE capability or PoE power budget is exhausted.',
                        'diagnosis': 'Run "show power inline" on the PoE switch.',
                        'fix': 'Connect AP to an 802.3at PoE+ enabled switch port or use an external PoE injector.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'Which of the following channels in the 2.4 GHz band are non-overlapping in North America?',
                        'options': [
                            {'id': 'A', 'text': 'Channels 1, 2, and 3'},
                            {'id': 'B', 'text': 'Channels 1, 6, and 11'},
                            {'id': 'C', 'text': 'Channels 3, 7, and 9'},
                            {'id': 'D', 'text': 'Channels 2, 4, and 8'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'In the 2.4 GHz Wi-Fi spectrum, channels 1, 6, and 11 have 25 MHz separation and do not overlap with each other, preventing co-channel interference.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Network Attached Storage (NAS) & SAN',
        'slug': 'nas-san-storage-networking',
        'description': 'Configure high-performance storage networking: NFS, SMB/CIFS, iSCSI block storage, RAID arrays (0, 1, 5, 10), LACP bonding, and dedicated storage VLANs.',
        'level': 'intermediate',
        'category': 'services_storage',
        'estimated_hours': 4.0,
        'icon': 'fa-hard-drive',
        'badge_name': 'Certified Storage Specialist',
        'order': 8,
        'lessons': [
            {
                'title': 'NAS Configuration: RAID Arrays, SMB/NFS Shares & Storage Subnets',
                'slug': 'nas-raid-smb-storage-subnets',
                'lesson_number': 1,
                'difficulty': 'intermediate',
                'estimated_minutes': 30,
                'summary': 'Deploy a high-availability NAS with RAID 5 redundancy, link aggregation (LACP), and isolated storage VLANs.',
                'section_a_intro': {
                    'definition': 'Network Attached Storage (NAS) is a dedicated file-level storage server connected to a computer network providing data access to a heterogeneous group of clients.',
                    'purpose': 'Centralizes enterprise data storage, file sharing, automated backups, and media libraries.',
                    'why_needed': 'Eliminates fragmented storage across individual PCs and provides high-availability disk redundancy against hardware drive failures.',
                    'where_used': 'Enterprise file shares, virtualization datastores, video surveillance archives, database backups.',
                    'real_world_examples': 'Synology DiskStation, QNAP Enterprise, TrueNAS CORE, NetApp FAS.',
                    'advantages': ['Centralized management', 'Fault-tolerant RAID parity', 'Snapshot point-in-time recovery'],
                    'limitations': ['File-level latency is higher than direct block storage (SAN Fibre Channel)']
                },
                'section_b_how_it_works': {
                    'architecture': 'Storage arrays utilize hardware/software RAID controllers across multiple SATA/SAS/NVMe disks, exposed via TCP/IP protocols.',
                    'protocols': ['NFS v3/v4', 'SMB 3.1.1 (CIFS)', 'iSCSI', 'SNMP'],
                    'interfaces': ['Dual 10GbE SFP+ uplinks', 'LACP 802.3ad Bonded Interfaces'],
                    'data_flow': 'Client issues SMB/NFS read/write request -> NAS CPU parses filesystem -> RAID controller distributes blocks with parity across disk array.',
                    'device_interactions': 'Workstations mount network drive paths (e.g., \\\\192.168.40.10\\data) over a dedicated Storage VLAN.',
                    'osi_layers': 'Layer 7 Application storage protocols over Layer 4 TCP.'
                },
                'section_c_connection': {
                    'required_devices': ['Enterprise NAS Server', 'Distribution Switch', 'Client Workstation'],
                    'cable_types': ['Dual Cat6a Copper 10G or SFP+ Twinax DAC cables'],
                    'port_selection': 'NAS eth0 & eth1 to Switch ports Gi0/1-2 (LACP Port-Channel 1)',
                    'interface_compatibility': '10GBASE-T / 10GbE SFP+',
                    'connection_diagram': '[NAS: 192.168.40.10] <== Dual 10G LACP ==> [Switch] <--- [Client: 192.168.40.100]',
                    'ip_requirements': 'Storage VLAN 40: Subnet 192.168.40.0/24',
                    'power_poe': 'Dual redundant AC power supplies (UPS protected).'
                },
                'section_d_configuration': {
                    'device_setup': 'Initialize RAID 5 volume with 4x 4TB drives (12TB usable capacity).',
                    'interface_config': 'Bond interfaces eth0 and eth1 into balance-xor or LACP 802.3ad trunk.',
                    'ip_config': 'Static IP: 192.168.40.10 255.255.255.0.',
                    'network_services': 'Create shared folder "Engineering" with SMB 3.0 permissions.',
                    'security_settings': 'Restrict NFS access by client subnet export rules.',
                    'verification': 'Verify share mount and benchmark read/write throughput.'
                },
                'section_e_commands': [
                    {
                        'command': 'storage share create name=engineering path=/volume1/engineering protocol=smb,nfs',
                        'syntax': 'storage share create [options]',
                        'purpose': 'Create high-availability network share export for client endpoints.',
                        'params': 'name: share name; path: local disk mount; protocol: enabled protocols',
                        'mode': 'NAS Web GUI / Admin Shell',
                        'expected_output': 'Share "engineering" created successfully with 12TB quota.',
                        'verification_commands': ['show storage shares', 'show storage raid status'],
                        'common_errors': 'Incorrect permission mask blocks write operations for authenticated users.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'nas1', 'name': 'NAS-Enterprise', 'type': 'nas_storage', 'x': 460, 'y': 180, 'ip': '192.168.40.10', 'mask': '255.255.255.0'},
                        {'id': 'sw1', 'name': 'SW-Core-01', 'type': 'layer2_switch', 'x': 300, 'y': 180},
                        {'id': 'pc1', 'name': 'PC-Storage-Client', 'type': 'pc_workstation', 'x': 140, 'y': 280, 'ip': '192.168.40.100', 'mask': '255.255.255.0'}
                    ],
                    'links': [
                        {'from': 'nas1', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Gi0/1', 'cable': 'copper_straight'},
                        {'from': 'pc1', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/1', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Test Connectivity to NAS Storage',
                        'instruction': 'From PC-Storage-Client, ping NAS-Enterprise (192.168.40.10) on the dedicated storage subnet.',
                        'target_device': 'pc1',
                        'expected_config': {'ping_success': '192.168.40.10'},
                        'hints': [
                            'Open terminal on PC-Storage-Client.',
                            'Execute "ping 192.168.40.10".',
                            'Verify low-latency Layer 2 communication.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc1', 'action': 'cli_command', 'command': 'ping 192.168.40.10', 'explanation': 'Ping NAS.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'ping_tests': [
                        {'from': 'pc1', 'to': '192.168.40.10', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Storage array reports degraded state',
                        'cause': 'A single hard drive in the RAID 5 array has experienced physical sector failure.',
                        'diagnosis': 'Inspect SMART disk health logs to identify failed drive bay.',
                        'fix': 'Hot-swap the failed hard disk with an identical replacement drive to initiate RAID rebuild.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'How many drive failures can a RAID 5 array tolerate without data loss?',
                        'options': [
                            {'id': 'A', 'text': '0 drives'},
                            {'id': 'B', 'text': '1 drive'},
                            {'id': 'C', 'text': '2 drives'},
                            {'id': 'D', 'text': '3 drives'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'RAID 5 uses distributed parity across all disks in the array, allowing it to withstand the failure of exactly one drive without losing data.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Network Printers & Print Server Configuration',
        'slug': 'network-printers-print-servers',
        'description': 'Deploy enterprise network printers, configure static IP reservations, LPR/RAW port 9100 protocols, centralized Windows/Linux print servers, and secure printer access control.',
        'level': 'beginner',
        'category': 'services_storage',
        'estimated_hours': 3.0,
        'icon': 'fa-print',
        'badge_name': 'Certified Print Infrastructure Specialist',
        'order': 9,
        'lessons': [
            {
                'title': 'Enterprise Network Printer Setup & Print Spooler Configuration',
                'slug': 'network-printer-spooler-setup',
                'lesson_number': 1,
                'difficulty': 'beginner',
                'estimated_minutes': 25,
                'summary': 'Configure static IP assignments for network multifunction printers (MFPs) and establish TCP/IP RAW Port 9100 communication.',
                'section_a_intro': {
                    'definition': 'A network printer is an output device connected directly to a computer network with its own internal Network Interface Card (NIC) and IP address.',
                    'purpose': 'Allows all authorized users across a network to print documents without requiring a host PC to remain powered on.',
                    'why_needed': 'USB-connected printers require a dedicated host PC and cannot handle enterprise print loads, access accounting, or central spooling.',
                    'where_used': 'Office print bays, accounting departments, hospital nurses stations, educational labs.',
                    'real_world_examples': 'HP LaserJet Enterprise, Xerox VersaLink, Canon imageRUNNER.',
                    'advantages': ['Independent network entity', 'High volume queueing', 'SNMP toner/paper status alerts'],
                    'limitations': ['Security risk if left on default passwords and exposed without ACLs']
                },
                'section_b_how_it_works': {
                    'architecture': 'Endpoints or print servers send PostScript/PCL print jobs over TCP Port 9100 (RAW) or Port 515 (LPR) to the printer embedded print engine.',
                    'protocols': ['RAW TCP 9100', 'LPR/LPD (RFC 1179)', 'IPP (Internet Printing Protocol - TCP 631)', 'SNMP'],
                    'interfaces': ['100/1000Base-TX RJ45 Ethernet port'],
                    'data_flow': 'Client PC -> Print Spooler -> Format to PCL/PostScript -> TCP 9100 stream -> Printer RAM -> Raster Image Processor (RIP) -> Laser Engine.',
                    'device_interactions': 'Printer requests DHCP with client-identifier, or is configured with a permanent static IP address outside the DHCP pool.',
                    'osi_layers': 'Application Layer printing protocols over Layer 4 TCP.'
                },
                'section_c_connection': {
                    'required_devices': ['Network Laser Printer PRN-01', 'Workgroup Switch SW-01', 'Client PC'],
                    'cable_types': ['Cat6 Straight-Through UTP copper cable'],
                    'port_selection': 'Switch port Fa0/10 (Access VLAN 10 or dedicated Printer VLAN)',
                    'interface_compatibility': '10/100/1000Base-T Auto-negotiation',
                    'connection_diagram': '[Client PC: 192.168.10.15] ---> [Switch] <--- [Network Printer: 192.168.10.200]',
                    'ip_requirements': 'Printer Static IP: 192.168.10.200/24; Default Gateway: 192.168.10.1',
                    'power_poe': 'Dedicated 110V/220V 15A AC wall outlet (Printers draw significant heating element power; NEVER run on PoE or small battery UPS).'
                },
                'section_d_configuration': {
                    'device_setup': 'Assign static IP address 192.168.10.200, subnet mask 255.255.255.0, gateway 192.168.10.1 via front LCD or web console.',
                    'interface_config': 'Disable unused protocols (AppleTalk, IPX/SPX) to reduce broadcast noise.',
                    'ip_config': 'Create static DHCP reservation in router/server scope.',
                    'network_services': 'Enable SNMP v3 for paper jam and toner level monitoring.',
                    'security_settings': 'Change default administrator password and restrict HTTP management to the IT admin VLAN.',
                    'verification': 'Ping printer IP and send test print page via RAW port 9100.'
                },
                'section_e_commands': [
                    {
                        'command': 'ping 192.168.10.200',
                        'syntax': 'ping <printer_ip>',
                        'purpose': 'Verify IP reachability to the network printer.',
                        'params': '<printer_ip>: target printer IPv4 address',
                        'mode': 'PC / Server Terminal',
                        'expected_output': 'Reply from 192.168.10.200: bytes=32 time=1ms TTL=64',
                        'verification_commands': ['telnet 192.168.10.200 9100'],
                        'common_errors': 'Host unreachable if printer is powered down or asleep in deep hibernation.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'prn1', 'name': 'PRN-Office-Laser', 'type': 'network_printer', 'x': 460, 'y': 220, 'ip': '192.168.10.200', 'mask': '255.255.255.0', 'gateway': '192.168.10.1'},
                        {'id': 'sw1', 'name': 'SW-01', 'type': 'layer2_switch', 'x': 300, 'y': 220},
                        {'id': 'pc1', 'name': 'PC-User', 'type': 'pc_workstation', 'x': 140, 'y': 220, 'ip': '192.168.10.15', 'mask': '255.255.255.0', 'gateway': '192.168.10.1'}
                    ],
                    'links': [
                        {'from': 'pc1', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/1', 'cable': 'copper_straight'},
                        {'from': 'prn1', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/10', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Test Network Reachability to Laser Printer',
                        'instruction': 'From PC-User, execute ping 192.168.10.200 to verify connection to the network printer.',
                        'target_device': 'pc1',
                        'expected_config': {'ping_success': '192.168.10.200'},
                        'hints': [
                            'Open terminal on PC-User.',
                            'Type "ping 192.168.10.200".',
                            'Verify printer responds to ICMP echo requests.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc1', 'action': 'cli_command', 'command': 'ping 192.168.10.200', 'explanation': 'Ping printer.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'ping_tests': [
                        {'from': 'pc1', 'to': '192.168.10.200', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Printer frequently changes IP address, breaking user print queues',
                        'cause': 'Printer configured with dynamic DHCP without a MAC reservation.',
                        'diagnosis': 'Check printer IP on LCD display vs printer port settings on Windows clients.',
                        'fix': 'Assign a permanent static IP or bind a static DHCP reservation to the printer MAC address.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'What standard TCP port is used for direct RAW network printing (AppSocket/JetDirect)?',
                        'options': [
                            {'id': 'A', 'text': 'Port 80'},
                            {'id': 'B', 'text': 'Port 443'},
                            {'id': 'C', 'text': 'Port 9100'},
                            {'id': 'D', 'text': 'Port 53'}
                        ],
                        'correct_answer': 'C',
                        'explanation': 'TCP port 9100 is the standard port for RAW socket network printing originally popularized by HP JetDirect.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'CCTV & Surveillance Networking (IP Cameras & NVR)',
        'slug': 'cctv-ipcamera-nvr-networking',
        'description': 'Design and deploy physical security networks: Power over Ethernet (PoE 802.3af/at), IP cameras, Network Video Recorders (NVR), bandwidth calculation, RTSP streaming, and isolated surveillance VLANs.',
        'level': 'intermediate',
        'category': 'infrastructure',
        'estimated_hours': 4.5,
        'icon': 'fa-video',
        'badge_name': 'Certified Surveillance Network Engineer',
        'order': 10,
        'lessons': [
            {
                'title': 'IP Camera Power over Ethernet (PoE) & NVR Subnet Isolation',
                'slug': 'cctv-poe-nvr-isolation',
                'lesson_number': 1,
                'difficulty': 'intermediate',
                'estimated_minutes': 30,
                'summary': 'Architect an isolated surveillance VLAN 50 connecting PoE IP cameras to a central Network Video Recorder (NVR).',
                'section_a_intro': {
                    'definition': 'An IP Camera is a digital video camera that captures high-definition surveillance footage, digitizes it, and transmits it over an Ethernet IP network to a Network Video Recorder (NVR).',
                    'purpose': 'Provides commercial and residential physical security monitoring, motion detection, and video archiving.',
                    'why_needed': 'Legacy analog CCTV required expensive point-to-point coaxial cabling. IP cameras leverage existing standard structured cabling and PoE.',
                    'where_used': 'Building perimeters, parking lots, hallways, retail stores, banks, data centers.',
                    'real_world_examples': 'Hikvision 4K DarkFighter, Axis Communications Dome, Dahua Starlight IP Cameras.',
                    'advantages': ['Single cable for power and data (PoE)', 'Ultra HD 4K video resolution', 'Remote PTZ control and digital zoom'],
                    'limitations': ['Continuous high network bandwidth consumption', 'High storage capacity requirements']
                },
                'section_b_how_it_works': {
                    'architecture': 'Cameras stream real-time video encoded in H.264/H.265 via Real-Time Streaming Protocol (RTSP) across an isolated Surveillance VLAN.',
                    'protocols': ['RTSP (TCP/UDP 554)', 'ONVIF (Profile S/G/T)', 'RTP/RTCP', 'PoE 802.3af/802.3at'],
                    'interfaces': ['PoE 100BASE-TX RJ45 ports', 'Hardware NVR Gigabit/10G uplink ports'],
                    'data_flow': 'CMOS Image Sensor -> H.265 Hardware Encoder -> RTP Packets -> Cat6 Cable -> PoE Switch -> NVR Storage Engine -> RAID Hard Drives.',
                    'device_interactions': 'Cameras are isolated on a dedicated VLAN with NO internet access to prevent botnet infections (e.g. Mirai botnet).',
                    'osi_layers': 'Application Layer video streams over Layer 4 UDP/TCP.'
                },
                'section_c_connection': {
                    'required_devices': ['PoE IP Cameras (CAM-01, CAM-02)', 'PoE Switch (802.3at)', 'Network Video Recorder (NVR-01)'],
                    'cable_types': ['Cat6 UTP Solid Copper with high-quality RJ45 connectors'],
                    'port_selection': 'Switch ports Fa0/1-4 for Cameras (PoE enabled); Port Gi0/1 for NVR (Trunk/Access)',
                    'interface_compatibility': '10/100/1000Base-T PoE',
                    'connection_diagram': '[CAM-01: .50.11] ---> (PoE) [SW-PoE: Fa0/1] & [CAM-02: .50.12] ---> (PoE) [SW-PoE: Fa0/2] <===> [NVR: .50.2]',
                    'ip_requirements': 'Surveillance VLAN 50: 192.168.50.0/24 (CAM-01: .11, CAM-02: .12, NVR: .2)',
                    'power_poe': '802.3af (15.4W) for static cameras; 802.3at (30W) for motorized PTZ cameras with built-in IR heaters.'
                },
                'section_d_configuration': {
                    'device_setup': 'Assign static IP addresses to NVR and all IP cameras on VLAN 50.',
                    'interface_config': 'Verify PoE negotiation on switch ports: show power inline.',
                    'ip_config': 'Ensure cameras and NVR reside in 192.168.50.0/24.',
                    'network_services': 'Configure ONVIF discovery and H.265 compression profile.',
                    'security_settings': 'BLOCK all outbound Internet access from VLAN 50 at the firewall.',
                    'verification': 'Verify NVR discovers camera video feeds and recording state is active.'
                },
                'section_e_commands': [
                    {
                        'command': 'show power inline',
                        'syntax': 'show power inline [interface]',
                        'purpose': 'Check PoE power consumption, voltage, and remaining power budget per switch port.',
                        'params': 'none or specific port like Fa0/1',
                        'mode': 'Switch Privileged EXEC',
                        'expected_output': 'Interface Admin  Oper       Power(Watts) Device        Class\nFa0/1     auto   on         12.5         IEEE-PD       3\nFa0/2     auto   on         14.2         IEEE-PD       3',
                        'verification_commands': ['show interfaces status'],
                        'common_errors': 'Exceeding the total switch PoE power budget turns off lowest-priority ports.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'cam1', 'name': 'CAM-Perimeter-01', 'type': 'ip_camera', 'x': 140, 'y': 140, 'ip': '192.168.50.11', 'mask': '255.255.255.0'},
                        {'id': 'cam2', 'name': 'CAM-Perimeter-02', 'type': 'ip_camera', 'x': 140, 'y': 280, 'ip': '192.168.50.12', 'mask': '255.255.255.0'},
                        {'id': 'sw_poe', 'name': 'SW-PoE-CCTV', 'type': 'poe_switch', 'x': 320, 'y': 210},
                        {'id': 'nvr1', 'name': 'NVR-Central-01', 'type': 'nvr_recorder', 'x': 500, 'y': 210, 'ip': '192.168.50.2', 'mask': '255.255.255.0'}
                    ],
                    'links': [
                        {'from': 'cam1', 'from_port': 'eth0', 'to': 'sw_poe', 'to_port': 'Fa0/1', 'cable': 'copper_straight'},
                        {'from': 'cam2', 'from_port': 'eth0', 'to': 'sw_poe', 'to_port': 'Fa0/2', 'cable': 'copper_straight'},
                        {'from': 'sw_poe', 'from_port': 'Gi0/1', 'to': 'nvr1', 'to_port': 'eth0', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Verify NVR Communication to IP Cameras',
                        'instruction': 'From NVR-Central-01 terminal, ping CAM-Perimeter-01 (192.168.50.11) to confirm video stream reachability.',
                        'target_device': 'nvr1',
                        'expected_config': {'ping_success': '192.168.50.11'},
                        'hints': [
                            'Open NVR terminal.',
                            'Type "ping 192.168.50.11".',
                            'Verify camera is receiving power and responding to ICMP.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'nvr1', 'action': 'cli_command', 'command': 'ping 192.168.50.11', 'explanation': 'Ping camera.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'ping_tests': [
                        {'from': 'nvr1', 'to': '192.168.50.11', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'IP Camera loses power at night when IR illuminators turn on',
                        'cause': 'Infrared LED night vision draws additional wattage exceeding the port 802.3af PoE limit.',
                        'diagnosis': 'Check switch port power allocation; camera draws <15W by day but >20W with IR active.',
                        'fix': 'Upgrade switch port power configuration to 802.3at PoE+ (up to 30W).'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'Why should IP surveillance cameras always be placed on an isolated VLAN without Internet access?',
                        'options': [
                            {'id': 'A', 'text': 'To save cable costs'},
                            {'id': 'B', 'text': 'To prevent camera firmware vulnerabilities from being exploited by internet botnets'},
                            {'id': 'C', 'text': 'Because IP cameras cannot understand IP addresses'},
                            {'id': 'D', 'text': 'To increase the camera frame rate to 240 fps'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'Surveillance cameras frequently have unpatched firmware vulnerabilities. Isolating them on a dedicated VLAN with strict firewall blocking stops unauthorized access and botnet recruitment.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Server Networking (Windows & Linux Infrastructure)',
        'slug': 'server-networking-windows-linux',
        'description': 'Configure enterprise server network stacks: Linux iproute2/Netplan, Windows Server NIC Teaming (LACP), static IP configuration, DHCP server scope deployment, and DNS resolution.',
        'level': 'intermediate',
        'category': 'services_storage',
        'estimated_hours': 5.0,
        'icon': 'fa-server',
        'badge_name': 'Certified Systems Infrastructure Engineer',
        'order': 11,
        'lessons': [
            {
                'title': 'DHCP Server Implementation: Scopes, Exclusions & Reservations',
                'slug': 'dhcp-server-scopes-reservations',
                'lesson_number': 1,
                'difficulty': 'intermediate',
                'estimated_minutes': 30,
                'summary': 'Configure an enterprise DHCP server to automatically lease IP addresses, subnet masks, default gateways, and DNS servers to network clients.',
                'section_a_intro': {
                    'definition': 'The Dynamic Host Configuration Protocol (DHCP) is a client/server network management protocol used to dynamically assign IP addresses and network parameters to devices.',
                    'purpose': 'Eliminates the tedious, error-prone manual configuration of IP addresses on hundreds of client endpoints.',
                    'why_needed': 'Without DHCP, network administrators would have to manually walk to every laptop, phone, and PC to configure unique IPs, risking duplicate IP conflicts.',
                    'where_used': 'Every corporate LAN, home Wi-Fi router, university campus, enterprise active directory domain.',
                    'real_world_examples': 'Windows Server DHCP role, Linux Kea/ISC-DHCP-Server, Cisco IOS DHCP pool.',
                    'advantages': ['Automated IP management', 'Centralized parameter changes (change DNS once for all hosts)', 'Prevents duplicate IP collisions'],
                    'limitations': ['Single point of failure if DHCP server goes offline without redundancy/failover']
                },
                'section_b_how_it_works': {
                    'architecture': 'DHCP operates through the 4-step D-O-R-A process over UDP ports 67 (server) and 68 (client).',
                    'protocols': ['UDP 67 (DHCP Server)', 'UDP 68 (DHCP Client)', 'BOOTP Relay (RFC 1542)'],
                    'interfaces': ['Physical Ethernet NIC', 'DHCP Relay Agent on router interfaces'],
                    'data_flow': '1. Discover (Client broadcast) -> 2. Offer (Server unicast/broadcast) -> 3. Request (Client selects IP) -> 4. Acknowledge (Server confirms lease).',
                    'device_interactions': 'When client and server are on different subnets, the router acts as a DHCP Relay Agent (ip helper-address).',
                    'osi_layers': 'Application Layer over UDP Transport Layer.'
                },
                'section_c_connection': {
                    'required_devices': ['DHCP Server SRV-DHCP', 'Workgroup Switch SW-01', 'Client PC-Client'],
                    'cable_types': ['Cat6 Straight-Through'],
                    'port_selection': 'Server to switch port Gi0/1; Client to switch port Fa0/1',
                    'interface_compatibility': '1000BASE-T',
                    'connection_diagram': '[SRV-DHCP: 192.168.1.5] <== Gi0/1 ==> [Switch: SW-01] <== Fa0/1 ==> [PC-Client: (DHCP)]',
                    'ip_requirements': 'DHCP Scope: 192.168.1.100 - 192.168.1.200, Mask: 255.255.255.0, GW: 192.168.1.1, DNS: 192.168.1.5',
                    'power_poe': 'AC Mains power with battery backup.'
                },
                'section_d_configuration': {
                    'device_setup': 'Configure static IP 192.168.1.5 on the DHCP server.',
                    'interface_config': 'Create DHCP Pool "OFFICE_POOL".',
                    'ip_config': 'Define network 192.168.1.0/24, exclude static range 192.168.1.1 - 192.168.1.99.',
                    'network_services': 'Specify default router (Option 3) and DNS server (Option 6).',
                    'security_settings': 'Enable DHCP Snooping on switches to block unauthorized rogue DHCP servers.',
                    'verification': 'Release and renew IP on client with ipconfig /renew.'
                },
                'section_e_commands': [
                    {
                        'command': 'ip dhcp pool OFFICE_POOL\n network 192.168.1.0 255.255.255.0\n default-router 192.168.1.1\n dns-server 192.168.1.5',
                        'syntax': 'ip dhcp pool <name>',
                        'purpose': 'Create and configure a DHCP scope pool distributing IP addresses and network options.',
                        'params': 'network: subnet; default-router: gateway; dns-server: nameserver',
                        'mode': 'Global Configuration Mode',
                        'expected_output': 'DHCP pool OFFICE_POOL initialized.',
                        'verification_commands': ['show ip dhcp binding', 'show ip dhcp pool'],
                        'common_errors': 'Forgetting to exclude default gateway causes IP conflict with the router.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'dhcp1', 'name': 'SRV-DHCP-01', 'type': 'dhcp_server', 'x': 460, 'y': 180, 'ip': '192.168.1.5', 'mask': '255.255.255.0'},
                        {'id': 'sw1', 'name': 'SW-01', 'type': 'layer2_switch', 'x': 300, 'y': 180},
                        {'id': 'pc1', 'name': 'PC-Workstation', 'type': 'pc_workstation', 'x': 140, 'y': 280, 'ip': '192.168.1.105', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'}
                    ],
                    'links': [
                        {'from': 'dhcp1', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Gi0/1', 'cable': 'copper_straight'},
                        {'from': 'pc1', 'from_port': 'eth0', 'to': 'sw1', 'to_port': 'Fa0/1', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Verify Client DHCP Lease Acquisition',
                        'instruction': 'From PC-Workstation, execute ipconfig /renew to verify dynamic IP acquisition from SRV-DHCP-01.',
                        'target_device': 'pc1',
                        'expected_config': {'dhcp_acquired': True},
                        'hints': [
                            'Open terminal on PC-Workstation.',
                            'Type "ipconfig".',
                            'Verify IPv4 address is within the leased 192.168.1.x range.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc1', 'action': 'cli_command', 'command': 'ipconfig', 'explanation': 'Check IP configuration.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'devices': {
                        'pc1': {'ip': '192.168.1.105', 'gateway': '192.168.1.1'}
                    }
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Client receives an APIPA address starting with 169.254.x.x',
                        'cause': 'DHCP Discover broadcasts received no response from any DHCP server.',
                        'diagnosis': 'Check physical cable connection, DHCP server service status, and router DHCP relay configuration.',
                        'fix': 'Restart DHCP service and configure "ip helper-address <dhcp_ip>" on the router gateway interface.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'What are the four sequential steps of the DHCP lease negotiation process?',
                        'options': [
                            {'id': 'A', 'text': 'Detect, Open, Route, Assign'},
                            {'id': 'B', 'text': 'Discover, Offer, Request, Acknowledge (DORA)'},
                            {'id': 'C', 'text': 'Dial, Obtain, Return, Authenticate'},
                            {'id': 'D', 'text': 'Data, Output, Receive, Acknowledge'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'The DHCP handshake follows DORA: 1. DHCP Discover, 2. DHCP Offer, 3. DHCP Request, and 4. DHCP Acknowledge.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Enterprise Network Design & High Availability',
        'slug': 'enterprise-network-design-ha',
        'description': 'Implement Cisco 3-tier hierarchical network design (Core, Distribution, Access), First Hop Redundancy Protocols (HSRP/VRRP), and LACP EtherChannel link aggregation.',
        'level': 'advanced',
        'category': 'switching_routing',
        'estimated_hours': 6.0,
        'icon': 'fa-sitemap',
        'badge_name': 'Certified Network Design Architect',
        'order': 12,
        'lessons': [
            {
                'title': 'First Hop Redundancy: HSRP & VRRP Default Gateway Failover',
                'slug': 'hsrp-vrrp-gateway-redundancy',
                'lesson_number': 1,
                'difficulty': 'advanced',
                'estimated_minutes': 35,
                'summary': 'Configure Hot Standby Router Protocol (HSRP) sharing a Virtual IP address to ensure seamless, zero-downtime default gateway failover.',
                'section_a_intro': {
                    'definition': 'First Hop Redundancy Protocols (FHRP) such as HSRP and VRRP allow multiple physical routers to share a single virtual IP and MAC address to act as a resilient default gateway.',
                    'purpose': 'Prevents network-wide outages when a primary default gateway router experiences hardware failure or cable severance.',
                    'why_needed': 'Endpoints are typically configured with a single static default gateway IP. If that single physical router dies, all off-subnet communication halts.',
                    'where_used': 'Enterprise datacenters, hospital clinical networks, banking transaction cores.',
                    'real_world_examples': 'HSRP on Cisco Catalyst 9000 cores, VRRP on open-standard multi-vendor networks.',
                    'advantages': ['Sub-second automatic failover', 'Zero client configuration changes', 'Active/Standby redundancy'],
                    'limitations': ['Requires matching configuration across redundant router pairs']
                },
                'section_b_how_it_works': {
                    'architecture': 'Active router responds to ARP requests for Virtual IP (e.g. 192.168.1.1). Standby router listens to periodic multicast hello packets (224.0.0.2).',
                    'protocols': ['HSRP (UDP 1985)', 'VRRP (IP Protocol 112)', 'GLBP'],
                    'interfaces': ['GigabitEthernet interfaces on redundant router pair'],
                    'data_flow': 'If Active router misses 3 consecutive hello packets (holdtime 10s), Standby router automatically transitions to Active and takes over Virtual MAC.',
                    'device_interactions': 'Clients always send traffic to Virtual IP 192.168.1.1 and never notice the physical failover.',
                    'osi_layers': 'Layer 3 First-Hop Redundancy.'
                },
                'section_c_connection': {
                    'required_devices': ['Router RTR-Primary', 'Router RTR-Secondary', 'Core Switch SW-Core', 'Host PC'],
                    'cable_types': ['Cat6a Gigabit Copper uplinks'],
                    'port_selection': 'RTR-Primary g0/0 and RTR-Secondary g0/0 to Core Switch',
                    'interface_compatibility': '1000BASE-T',
                    'connection_diagram': '[RTR-Primary: .1.2 (Active)] & [RTR-Secondary: .1.3 (Standby)] ===> Virtual IP: 192.168.1.1 ===> [Host PC]',
                    'ip_requirements': 'Virtual IP: 192.168.1.1; RTR-Primary: 192.168.1.2; RTR-Secondary: 192.168.1.3',
                    'power_poe': 'Dual redundant A/B feed power supplies.'
                },
                'section_d_configuration': {
                    'device_setup': 'Configure HSRP Group 1 on both routers.',
                    'interface_config': 'Set priority 110 on RTR-Primary with preemption enabled.',
                    'ip_config': 'Configure priority 100 on RTR-Secondary.',
                    'network_services': 'Verify hello timer (3s) and hold timer (10s).',
                    'security_settings': 'Enable MD5 authentication on HSRP messages.',
                    'verification': 'show standby brief'
                },
                'section_e_commands': [
                    {
                        'command': 'interface GigabitEthernet0/0\n standby 1 ip 192.168.1.1\n standby 1 priority 110\n standby 1 preempt',
                        'syntax': 'standby <group> ip <virtual-ip>\nstandby <group> priority <priority>\nstandby <group> preempt',
                        'purpose': 'Configure HSRP Active router with Virtual IP 192.168.1.1, high priority, and preemption.',
                        'params': 'priority 110: higher than default 100 ensures Active state; preempt: reclaims Active when recovered',
                        'mode': 'Interface Configuration Mode',
                        'expected_output': '%HSRP-5-STATECHANGE: GigabitEthernet0/0 Grp 1 state Standby -> Active',
                        'verification_commands': ['show standby brief'],
                        'common_errors': 'Omitting "preempt" prevents the primary router from resuming active status after reboot.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'rtr_p', 'name': 'RTR-Primary', 'type': 'router', 'x': 200, 'y': 140, 'interfaces': ['g0/0']},
                        {'id': 'rtr_s', 'name': 'RTR-Secondary', 'type': 'router', 'x': 440, 'y': 140, 'interfaces': ['g0/0']},
                        {'id': 'sw_core', 'name': 'SW-Core', 'type': 'layer3_switch', 'x': 320, 'y': 240},
                        {'id': 'pc1', 'name': 'PC-Host', 'type': 'pc_workstation', 'x': 320, 'y': 340, 'ip': '192.168.1.50', 'gateway': '192.168.1.1'}
                    ],
                    'links': [
                        {'from': 'rtr_p', 'from_port': 'g0/0', 'to': 'sw_core', 'to_port': 'Gi0/1', 'cable': 'copper_straight'},
                        {'from': 'rtr_s', 'from_port': 'g0/0', 'to': 'sw_core', 'to_port': 'Gi0/2', 'cable': 'copper_straight'},
                        {'from': 'pc1', 'from_port': 'eth0', 'to': 'sw_core', 'to_port': 'Fa0/1', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Verify HSRP Gateway Reachability from Host',
                        'instruction': 'From PC-Host, execute ping 192.168.1.1 to confirm default gateway reachability via the HSRP Virtual IP.',
                        'target_device': 'pc1',
                        'expected_config': {'ping_success': '192.168.1.1'},
                        'hints': [
                            'Open terminal on PC-Host.',
                            'Type "ping 192.168.1.1".',
                            'Verify active router answers the Virtual IP.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc1', 'action': 'cli_command', 'command': 'ping 192.168.1.1', 'explanation': 'Ping Virtual Gateway.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'ping_tests': [
                        {'from': 'pc1', 'to': '192.168.1.1', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'Both routers claim Active state simultaneously (Split Brain)',
                        'cause': 'HSRP hello multicast packets are blocked between the two routers due to an intermediate switch VLAN mismatch or ACL.',
                        'diagnosis': 'Execute "show standby brief" on both routers. If both say Active, hello packets are not traversing the link.',
                        'fix': 'Verify intermediate switch ports belong to the same VLAN and do not block UDP port 1985.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'What does the "preempt" command do in Cisco HSRP configuration?',
                        'options': [
                            {'id': 'A', 'text': 'It shuts down the standby router immediately'},
                            {'id': 'B', 'text': 'It enables a router with higher priority to reclaim the Active role when it comes back online'},
                            {'id': 'C', 'text': 'It disables all encryption on the router'},
                            {'id': 'D', 'text': 'It converts HSRP into OSPF'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'Without preempt, a router that reboots will remain Standby even if its priority is higher than the currently active router. Preempt forces it to resume the Active role.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Network Troubleshooting & Diagnostics Lab',
        'slug': 'network-troubleshooting-diagnostics',
        'description': 'Master systematic diagnostic methodologies (Bottom-Up, Top-Down, Divide-and-Conquer), decode packet capture logs, isolate IP conflicts, and resolve duplex mismatches.',
        'level': 'advanced',
        'category': 'troubleshooting',
        'estimated_hours': 5.0,
        'icon': 'fa-wrench',
        'badge_name': 'Certified Network Troubleshooter',
        'order': 13,
        'lessons': [
            {
                'title': 'Systematic Fault Isolation & Multi-Layer Diagnostics',
                'slug': 'systematic-fault-isolation',
                'lesson_number': 1,
                'difficulty': 'advanced',
                'estimated_minutes': 30,
                'summary': 'Diagnose a broken multi-device enterprise topology step-by-step: Physical layer, Data link layer, Network layer, and Transport layer.',
                'section_a_intro': {
                    'definition': 'Network troubleshooting is the structured process of diagnosing, locating, and resolving hardware, software, and configuration faults within computer networks.',
                    'purpose': 'Minimizes costly business downtime and restores critical communication services quickly and efficiently.',
                    'why_needed': 'Random trial-and-error changes often introduce secondary defects and compound outages. Systematic methodologies guarantee fast resolution.',
                    'where_used': 'Network Operations Centers (NOC), Tier-3 engineering escalations, on-call site reliability engineering.',
                    'real_world_examples': 'Isolating a flapping fiber optic uplink, resolving a routing loop black hole, fixing MTU fragmentation drops.',
                    'advantages': ['Structured root cause analysis', 'Reproducible diagnosis', 'Prevents recurring incidents'],
                    'limitations': ['Requires thorough knowledge of protocol encapsulation across all 7 layers']
                },
                'section_b_how_it_works': {
                    'architecture': 'Troubleshooting methodologies: 1. Bottom-Up (L1 to L7), 2. Top-Down (L7 to L1), 3. Divide-and-Conquer (start at L3/L4 with ping/traceroute).',
                    'protocols': ['ICMP', 'ARP', 'DNS', 'TCP SYN/ACK', 'SNMP'],
                    'interfaces': ['Physical transceivers', 'SVI', 'Routing tables'],
                    'data_flow': 'Step 1: Verify physical link LEDs -> Step 2: Verify MAC table learning -> Step 3: Verify IP address & gateway -> Step 4: Verify routing table -> Step 5: Verify ACL/Firewall.',
                    'device_interactions': 'Ping confirms Layer 3 reachability; Traceroute isolates the exact hop where packets are discarded.',
                    'osi_layers': 'All 7 OSI Layers.'
                },
                'section_c_connection': {
                    'required_devices': ['Troubled Endpoint PC-A', 'Intermediate Switch', 'Border Router', 'Remote Server'],
                    'cable_types': ['Cat6 UTP / Fiber'],
                    'port_selection': 'All transit ports between client and remote server',
                    'interface_compatibility': 'Auto-negotiation check',
                    'connection_diagram': '[PC-A] ---> [Switch] ---> [Router] ---> [Remote Server]',
                    'ip_requirements': 'Inspect IP configurations across all hops.',
                    'power_poe': 'Verify power indicators.'
                },
                'section_d_configuration': {
                    'device_setup': 'Collect baseline running configs.',
                    'interface_config': 'Inspect show interfaces status for speed/duplex mismatches.',
                    'ip_config': 'Verify subnet masks match throughout the broadcast domain.',
                    'network_services': 'Check DNS resolution via nslookup.',
                    'security_settings': 'Check for blocking access-lists on transit router interfaces.',
                    'verification': 'Verify end-to-end ping and TCP port connection.'
                },
                'section_e_commands': [
                    {
                        'command': 'traceroute 192.168.20.10',
                        'syntax': 'traceroute <destination_ip>',
                        'purpose': 'Trace every hop along the routed path to identify the exact router where packets are dropped.',
                        'params': '<destination_ip>: destination address',
                        'mode': 'Router / Endpoint CLI',
                        'expected_output': '1 192.168.1.1 1 ms\n2 10.0.0.2 2 ms\n3 192.168.20.10 3 ms',
                        'verification_commands': ['ping', 'show ip route'],
                        'common_errors': 'Asterisks (***) indicate a firewall dropping ICMP/UDP probes or an unreachable hop.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'pc1', 'name': 'PC-Diagnostic', 'type': 'pc_workstation', 'x': 140, 'y': 220, 'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                        {'id': 'rtr1', 'name': 'RTR-Gateway', 'type': 'router', 'x': 340, 'y': 220, 'interfaces': ['g0/0', 'g0/1']},
                        {'id': 'srv1', 'name': 'SRV-Remote', 'type': 'web_server', 'x': 540, 'y': 220, 'ip': '192.168.2.50', 'mask': '255.255.255.0', 'gateway': '192.168.2.1'}
                    ],
                    'links': [
                        {'from': 'pc1', 'from_port': 'eth0', 'to': 'rtr1', 'to_port': 'g0/0', 'cable': 'copper_straight'},
                        {'from': 'rtr1', 'from_port': 'g0/1', 'to': 'srv1', 'to_port': 'eth0', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Diagnose End-to-End Path Connectivity',
                        'instruction': 'From PC-Diagnostic, execute ping 192.168.2.50 to test Layer 3 path reachability to SRV-Remote.',
                        'target_device': 'pc1',
                        'expected_config': {'ping_success': '192.168.2.50'},
                        'hints': [
                            'Open PC-Diagnostic terminal.',
                            'Execute "ping 192.168.2.50".',
                            'Verify gateway routes packets successfully.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc1', 'action': 'cli_command', 'command': 'ping 192.168.2.50', 'explanation': 'Execute diagnostic ping.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'ping_tests': [
                        {'from': 'pc1', 'to': '192.168.2.50', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'High packet loss and sluggish file transfers across a single link',
                        'cause': 'Duplex mismatch where one interface is set to 100/Full and the opposite side is auto-negotiating to 100/Half.',
                        'diagnosis': 'Inspect "show interfaces" on the switch; look for late collisions on the half-duplex side and FCS/CRC errors on the full-duplex side.',
                        'fix': 'Set both sides of the link to auto-negotiate or hardcode both sides to full duplex.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'Which troubleshooting approach begins by testing with ping and traceroute at Layer 3 to determine whether to investigate higher or lower layers?',
                        'options': [
                            {'id': 'A', 'text': 'Bottom-Up'},
                            {'id': 'B', 'text': 'Top-Down'},
                            {'id': 'C', 'text': 'Divide-and-Conquer'},
                            {'id': 'D', 'text': 'Substitution Method'}
                        ],
                        'correct_answer': 'C',
                        'explanation': 'The Divide-and-Conquer method starts in the middle of the OSI model (typically Layer 3/4 with ping or telnet). If ping succeeds, the lower layers are proven operational and attention shifts up.'
                    }
                ]
            }
        ]
    },
    {
        'title': 'Practical Network Administration & Hands-on Exam',
        'slug': 'practical-network-admin-exam',
        'description': 'The capstone examination of Ramonet Academy. Configure a multi-site enterprise topology from scratch, resolve sabotaged faults, secure perimeters, and earn your official certification.',
        'level': 'advanced',
        'category': 'troubleshooting',
        'estimated_hours': 6.0,
        'icon': 'fa-certificate',
        'badge_name': 'Ramonet Certified Network Architect (RCNA)',
        'order': 14,
        'lessons': [
            {
                'title': 'Comprehensive Enterprise Campus Capstone Lab & Exam',
                'slug': 'comprehensive-enterprise-capstone-exam',
                'lesson_number': 1,
                'difficulty': 'advanced',
                'estimated_minutes': 45,
                'summary': 'Configure full enterprise campus: VLANs, Inter-VLAN routing, OSPF, stateful firewall rules, and verify end-to-end multi-site packet delivery.',
                'section_a_intro': {
                    'definition': 'The Ramonet Academy Capstone Practical Examination tests your cumulative mastery of enterprise switching, routing, IP subnetting, firewall policies, and diagnostics.',
                    'purpose': 'Validates hands-on engineering competence in configuring, securing, and troubleshooting production network infrastructure.',
                    'why_needed': 'Theoretical knowledge alone does not prepare engineers for real-world outages. Hands-on configuration under simulated conditions proves mastery.',
                    'where_used': 'Enterprise engineering competency validation, technical interviews, certification benchmarking.',
                    'real_world_examples': 'Provisioning a brand new branch office network from unconfigured hardware to production readiness.',
                    'advantages': ['Hands-on validation', 'Multi-point verification scoring', 'Official verified digital credential'],
                    'limitations': ['Rigorous multi-point pass threshold (80% or higher required)']
                },
                'section_b_how_it_works': {
                    'architecture': 'Complete 3-tier enterprise campus design: Access Switches -> Distribution Multi-Layer Switches -> Border Firewall -> Edge Router.',
                    'protocols': ['802.1Q VLANs', 'Static / OSPF Routing', 'NAT/PAT', 'Stateful Inspection', 'DHCP'],
                    'interfaces': ['Trunks, Access ports, Routed GigabitEthernet, DMZ'],
                    'data_flow': 'End-to-end packet delivery verified across 4 subnets through automated simulation scoring.',
                    'device_interactions': 'Coordinated operation across PCs, Layer 2 switches, Routers, Firewalls, and Servers.',
                    'osi_layers': 'All Layers (1 through 7).'
                },
                'section_c_connection': {
                    'required_devices': ['Branch PC', 'Access Switch', 'Core Router', 'Perimeter Firewall', 'Enterprise Server'],
                    'cable_types': ['Cat6 Straight-Through and Fiber patch cables'],
                    'port_selection': 'Standardized structured port assignments',
                    'interface_compatibility': '1000BASE-T Gigabit',
                    'connection_diagram': '[Branch PC] ---> [Switch] ---> [Core Router] ---> [Firewall] ---> [Enterprise Server]',
                    'ip_requirements': 'Full campus IP addressing plan: 192.168.10.0/24, 192.168.20.0/24, 10.0.0.0/30, 172.16.1.0/24',
                    'power_poe': 'Full redundant enterprise power infrastructure.'
                },
                'section_d_configuration': {
                    'device_setup': 'Configure hostnames, banners, and administration passwords.',
                    'interface_config': 'Set up 802.1Q VLANs and assign interfaces.',
                    'ip_config': 'Configure interface IP addresses and subnet masks.',
                    'network_services': 'Deploy routing tables and stateful inspection policies.',
                    'security_settings': 'Lock down access and filter unneeded transit ports.',
                    'verification': 'Execute multi-point automated test suite.'
                },
                'section_e_commands': [
                    {
                        'command': 'show ip route',
                        'syntax': 'show ip route',
                        'purpose': 'Verify full routing table convergence across all campus subnets.',
                        'params': 'none',
                        'mode': 'Privileged EXEC',
                        'expected_output': 'Routing table converged with all subnets reachable.',
                        'verification_commands': ['ping', 'traceroute'],
                        'common_errors': 'Missing return routes cause one-way packet drops.'
                    }
                ],
                'has_practical_lab': True,
                'lab_topology': {
                    'devices': [
                        {'id': 'pc_client', 'name': 'PC-Campus-Client', 'type': 'pc_workstation', 'x': 120, 'y': 220, 'ip': '192.168.10.15', 'mask': '255.255.255.0', 'gateway': '192.168.10.1'},
                        {'id': 'sw_access', 'name': 'SW-Access-01', 'type': 'layer2_switch', 'x': 280, 'y': 220},
                        {'id': 'rtr_core', 'name': 'RTR-Campus-Core', 'type': 'router', 'x': 440, 'y': 220, 'interfaces': ['g0/0', 'g0/1']},
                        {'id': 'srv_hq', 'name': 'SRV-HQ-Data', 'type': 'file_server', 'x': 600, 'y': 220, 'ip': '192.168.20.100', 'mask': '255.255.255.0', 'gateway': '192.168.20.1'}
                    ],
                    'links': [
                        {'from': 'pc_client', 'from_port': 'eth0', 'to': 'sw_access', 'to_port': 'Fa0/1', 'cable': 'copper_straight'},
                        {'from': 'sw_access', 'from_port': 'Gi0/1', 'to': 'rtr_core', 'to_port': 'g0/0', 'cable': 'copper_straight'},
                        {'from': 'rtr_core', 'from_port': 'g0/1', 'to': 'srv_hq', 'to_port': 'eth0', 'cable': 'copper_straight'}
                    ]
                },
                'lab_tasks': [
                    {
                        'task_id': 'task_1',
                        'title': 'Configure Core Router Gateway Interfaces',
                        'instruction': 'On RTR-Campus-Core, configure g0/0 with 192.168.10.1/24 and g0/1 with 192.168.20.1/24, enabling both with "no shutdown".',
                        'target_device': 'rtr_core',
                        'expected_config': {
                            'interfaces': {
                                'g0/0': {'ip': '192.168.10.1', 'mask': '255.255.255.0', 'status': 'up'},
                                'g0/1': {'ip': '192.168.20.1', 'mask': '255.255.255.0', 'status': 'up'}
                            }
                        },
                        'hints': [
                            'Open RTR-Campus-Core terminal and enter config mode.',
                            'Configure interface g0/0 with IP 192.168.10.1 255.255.255.0 and "no shutdown".',
                            'Configure interface g0/1 with IP 192.168.20.1 255.255.255.0 and "no shutdown".'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'rtr_core', 'action': 'cli_command', 'command': 'enable', 'explanation': 'Privileged mode.'},
                            {'step': 2, 'device': 'rtr_core', 'action': 'cli_command', 'command': 'configure terminal', 'explanation': 'Global config.'},
                            {'step': 3, 'device': 'rtr_core', 'action': 'cli_command', 'command': 'interface g0/0', 'explanation': 'Select g0/0.'},
                            {'step': 4, 'device': 'rtr_core', 'action': 'cli_command', 'command': 'ip address 192.168.10.1 255.255.255.0', 'explanation': 'Set g0/0 IP.'},
                            {'step': 5, 'device': 'rtr_core', 'action': 'cli_command', 'command': 'no shutdown', 'explanation': 'Enable g0/0.'},
                            {'step': 6, 'device': 'rtr_core', 'action': 'cli_command', 'command': 'interface g0/1', 'explanation': 'Select g0/1.'},
                            {'step': 7, 'device': 'rtr_core', 'action': 'cli_command', 'command': 'ip address 192.168.20.1 255.255.255.0', 'explanation': 'Set g0/1 IP.'},
                            {'step': 8, 'device': 'rtr_core', 'action': 'cli_command', 'command': 'no shutdown', 'explanation': 'Enable g0/1.'}
                        ]
                    },
                    {
                        'task_id': 'task_2',
                        'title': 'Verify End-to-End Enterprise Packet Delivery',
                        'instruction': 'From PC-Campus-Client (192.168.10.15), ping SRV-HQ-Data (192.168.20.100) to complete the capstone exam.',
                        'target_device': 'pc_client',
                        'expected_config': {'ping_success': '192.168.20.100'},
                        'hints': [
                            'Open terminal on PC-Campus-Client.',
                            'Execute "ping 192.168.20.100".',
                            'Verify all 4 echo replies return with 0% packet loss.'
                        ],
                        'show_me_steps': [
                            {'step': 1, 'device': 'pc_client', 'action': 'cli_command', 'command': 'ping 192.168.20.100', 'explanation': 'Test full campus reachability.'}
                        ]
                    }
                ],
                'lab_solution_state': {
                    'devices': {
                        'rtr_core': {
                            'interfaces': {
                                'g0/0': {'ip': '192.168.10.1', 'status': 'up'},
                                'g0/1': {'ip': '192.168.20.1', 'status': 'up'}
                            }
                        }
                    },
                    'ping_tests': [
                        {'from': 'pc_client', 'to': '192.168.20.100', 'expect': 'success'}
                    ]
                },
                'section_g_troubleshooting': [
                    {
                        'symptom': 'End-to-end ping fails across the core router',
                        'cause': 'One of the router interfaces remained in shutdown state or wrong gateway was set on the host.',
                        'diagnosis': 'Run "show ip interface brief" on the router and "ipconfig" on the client.',
                        'fix': 'Issue "no shutdown" on the router interface and verify host gateway points to 192.168.10.1.'
                    }
                ],
                'quizzes': [
                    {
                        'question_type': 'mcq',
                        'question_text': 'What is the primary architectural function of the Distribution Layer in Cisco hierarchical network design?',
                        'options': [
                            {'id': 'A', 'text': 'Direct physical connection to user desktop endpoints'},
                            {'id': 'B', 'text': 'Routing, policy enforcement, access-control, and aggregation of access layer switches'},
                            {'id': 'C', 'text': 'Supplying PoE electrical power to IP phones'},
                            {'id': 'D', 'text': 'Connecting international undersea optical cables'}
                        ],
                        'correct_answer': 'B',
                        'explanation': 'The Distribution layer acts as the boundary between the Core and Access layers, performing routing, packet filtering (ACLs), inter-VLAN routing, and traffic policy enforcement.'
                    }
                ]
            }
        ]
    }
]
