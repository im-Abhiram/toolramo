from django.test import TestCase
from simulation.engine import NetworkSimulationEngine

class NetworkSimulationEngineTests(TestCase):
    def setUp(self):
        # Topology: PC1 -> Switch1 -> Router1 -> Switch2 -> PC2
        self.e2e_topology = {
            'devices': [
                {
                    'id': 'pc1', 'name': 'PC1', 'category': 'computers',
                    'ip': '192.168.1.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1',
                    'interfaces': [{'name': 'eth0', 'status': 'up'}]
                },
                {
                    'id': 'sw1', 'name': 'Switch1', 'category': 'switches',
                    'interfaces': [{'name': 'Fa0/1', 'status': 'up'}, {'name': 'Gi0/1', 'status': 'up'}]
                },
                {
                    'id': 'r1', 'name': 'Router1', 'category': 'routers', 'ip': '192.168.1.1',
                    'interfaces': [
                        {'name': 'Gi0/0', 'ip': '192.168.1.1', 'mask': '255.255.255.0', 'status': 'up'},
                        {'name': 'Gi0/1', 'ip': '10.0.0.1', 'mask': '255.255.255.0', 'status': 'up'}
                    ]
                },
                {
                    'id': 'sw2', 'name': 'Switch2', 'category': 'switches',
                    'interfaces': [{'name': 'Gi0/1', 'status': 'up'}, {'name': 'Fa0/1', 'status': 'up'}]
                },
                {
                    'id': 'pc2', 'name': 'PC2', 'category': 'computers',
                    'ip': '10.0.0.50', 'subnet_mask': '255.255.255.0', 'gateway': '10.0.0.1',
                    'interfaces': [{'name': 'eth0', 'status': 'up'}]
                }
            ],
            'connections': [
                {'id': 'c1', 'source_device': 'pc1', 'source_port': 'eth0', 'target_device': 'sw1', 'target_port': 'Fa0/1', 'status': 'connected'},
                {'id': 'c2', 'source_device': 'sw1', 'source_port': 'Gi0/1', 'target_device': 'r1', 'target_port': 'Gi0/0', 'status': 'connected'},
                {'id': 'c3', 'source_device': 'r1', 'source_port': 'Gi0/1', 'target_device': 'sw2', 'target_port': 'Gi0/1', 'status': 'connected'},
                {'id': 'c4', 'source_device': 'sw2', 'source_port': 'Fa0/1', 'target_device': 'pc2', 'target_port': 'eth0', 'status': 'connected'}
            ]
        }

    def test_e2e_successful_ping(self):
        """End-to-End packet forwarding: PC1 -> Switch1 -> Router1 -> Switch2 -> PC2"""
        engine = NetworkSimulationEngine(self.e2e_topology)
        result = engine.simulate_packet('pc1', '10.0.0.50', protocol='ICMP')
        self.assertTrue(result['success'])
        self.assertGreaterEqual(len(result['hops']), 4)
        self.assertIn('PC2', result['summary'])

    def test_e2e_incorrect_gateway_detection(self):
        """Verify simulator detects when host has an invalid default gateway"""
        topo = dict(self.e2e_topology)
        # Point PC1 to an unreachable gateway IP
        topo['devices'][0]['gateway'] = '192.168.99.1'

        engine = NetworkSimulationEngine(topo)
        result = engine.simulate_packet('pc1', '10.0.0.50', protocol='ICMP')
        self.assertFalse(result['success'])

    def test_missing_route_drop(self):
        """Verify router drops packet when destination network has no route in routing table"""
        engine = NetworkSimulationEngine(self.e2e_topology)
        # Attempt to ping an unrouted 172.16.1.10 destination
        result = engine.simulate_packet('pc1', '172.16.1.10', protocol='ICMP')
        self.assertFalse(result['success'])
        self.assertEqual(result['drop_reason'], 'NO_ROUTE_TO_HOST')

    def test_disconnected_cable_drop(self):
        """Verify simulator drops packet when an interface has no connected cable"""
        topo = {
            'devices': [
                {'id': 'pc1', 'name': 'PC1', 'ip': '192.168.1.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0'}]},
                {'id': 'pc2', 'name': 'PC2', 'ip': '192.168.1.20', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0'}]}
            ],
            'connections': [] # No cables
        }
        engine = NetworkSimulationEngine(topo)
        result = engine.simulate_packet('pc1', '192.168.1.20', protocol='ICMP')
        self.assertFalse(result['success'])
        self.assertEqual(result['drop_reason'], 'CABLE_DISCONNECTED')

    def test_stateful_firewall_filtering(self):
        """Verify stateful firewall allows permitted traffic and drops denied ports"""
        fw_topo = {
            'devices': [
                {'id': 'client', 'name': 'ClientPC', 'ip': '192.168.1.50', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0'}]},
                {
                    'id': 'fw1', 'name': 'Firewall', 'category': 'firewalls', 'ip': '192.168.1.1',
                    'default_policy': 'deny',
                    'firewall_rules': [
                        {'id': 1, 'src_ip': '192.168.1.0/24', 'dest_ip': 'any', 'protocol': 'tcp', 'port': '80', 'action': 'allow', 'enabled': True},
                        {'id': 2, 'src_ip': 'any', 'dest_ip': 'any', 'protocol': 'any', 'port': 'any', 'action': 'deny', 'enabled': True}
                    ],
                    'interfaces': [
                        {'name': 'LAN', 'ip': '192.168.1.1', 'mask': '255.255.255.0'},
                        {'name': 'WAN', 'ip': '10.0.0.1', 'mask': '255.255.255.0'}
                    ]
                },
                {'id': 'srv', 'name': 'WebServer', 'ip': '10.0.0.100', 'subnet_mask': '255.255.255.0', 'gateway': '10.0.0.1', 'interfaces': [{'name': 'eth0'}]}
            ],
            'connections': [
                {'source_device': 'client', 'source_port': 'eth0', 'target_device': 'fw1', 'target_port': 'LAN', 'status': 'connected'},
                {'source_device': 'fw1', 'source_port': 'WAN', 'target_device': 'srv', 'target_port': 'eth0', 'status': 'connected'}
            ]
        }
        engine = NetworkSimulationEngine(fw_topo)
        
        # Test HTTP (Port 80) -> ALLOWED by Rule 1
        res_http = engine.simulate_packet('client', '10.0.0.100', protocol='TCP', dest_port=80)
        self.assertTrue(res_http['success'])

        # Test SSH (Port 22) -> DENIED by Rule 2
        res_ssh = engine.simulate_packet('client', '10.0.0.100', protocol='TCP', dest_port=22)
        self.assertFalse(res_ssh['success'])
        self.assertEqual(res_ssh['drop_reason'], 'FIREWALL_DENY')

    def test_cctv_ip_camera_to_nvr_stream(self):
        """Verify IP Camera RTSP (Port 554) video stream communication to NVR"""
        cctv_topo = {
            'devices': [
                {'id': 'cam1', 'name': 'DomeCamera', 'category': 'cctv', 'ip': '192.168.10.11', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.10.1', 'interfaces': [{'name': 'eth0_PoE'}]},
                {'id': 'sw_poe', 'name': 'PoESwitch', 'category': 'switches', 'interfaces': [{'name': 'Port1'}, {'name': 'Port8'}]},
                {'id': 'nvr', 'name': 'NVR', 'category': 'cctv', 'ip': '192.168.10.100', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.10.1', 'interfaces': [{'name': 'LAN1'}]}
            ],
            'connections': [
                {'source_device': 'cam1', 'source_port': 'eth0_PoE', 'target_device': 'sw_poe', 'target_port': 'Port1', 'status': 'connected'},
                {'source_device': 'sw_poe', 'source_port': 'Port8', 'target_device': 'nvr', 'target_port': 'LAN1', 'status': 'connected'}
            ]
        }
        engine = NetworkSimulationEngine(cctv_topo)
        res = engine.simulate_packet('cam1', '192.168.10.100', protocol='TCP', dest_port=554)
        self.assertTrue(res['success'])

    def test_nas_smb_file_sharing(self):
        """Verify client connection to NAS storage server via SMB (Port 445)"""
        nas_topo = {
            'devices': [
                {'id': 'pc', 'name': 'ClientPC', 'ip': '192.168.1.50', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0'}]},
                {'id': 'sw', 'name': 'Switch', 'category': 'switches', 'interfaces': [{'name': 'Fa0/1'}, {'name': 'Fa0/2'}]},
                {'id': 'nas', 'name': 'SynologyNAS', 'category': 'storage', 'ip': '192.168.1.20', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0'}]}
            ],
            'connections': [
                {'source_device': 'pc', 'source_port': 'eth0', 'target_device': 'sw', 'target_port': 'Fa0/1', 'status': 'connected'},
                {'source_device': 'sw', 'source_port': 'Fa0/2', 'target_device': 'nas', 'target_port': 'eth0', 'status': 'connected'}
            ]
        }
        engine = NetworkSimulationEngine(nas_topo)
        res = engine.simulate_packet('pc', '192.168.1.20', protocol='TCP', dest_port=445)
        self.assertTrue(res['success'])

    def test_printer_raw_port_9100_connectivity(self):
        """Verify network printer connectivity over RAW port 9100"""
        print_topo = {
            'devices': [
                {'id': 'pc', 'name': 'ClientPC', 'ip': '192.168.1.50', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0'}]},
                {'id': 'sw', 'name': 'Switch', 'category': 'switches', 'interfaces': [{'name': 'Fa0/1'}, {'name': 'Fa0/5'}]},
                {'id': 'printer', 'name': 'HP-LaserJet', 'category': 'printers', 'ip': '192.168.1.200', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0'}]}
            ],
            'connections': [
                {'source_device': 'pc', 'source_port': 'eth0', 'target_device': 'sw', 'target_port': 'Fa0/1', 'status': 'connected'},
                {'source_device': 'sw', 'source_port': 'Fa0/5', 'target_device': 'printer', 'target_port': 'eth0', 'status': 'connected'}
            ]
        }
        engine = NetworkSimulationEngine(print_topo)
        res = engine.simulate_packet('pc', '192.168.1.200', protocol='TCP', dest_port=9100)
        self.assertTrue(res['success'])

    def test_mixed_shorthand_port_names_routing(self):
        """Verify logical connections route accurately across mismatched port aliases (e.g. g0/1 vs Gi0/1 vs GigabitEthernet0/1)"""
        mixed_topo = {
            'devices': [
                {'id': 'pc1', 'name': 'PC1', 'category': 'computers', 'ip': '192.168.1.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]},
                {'id': 'sw1', 'name': 'Switch1', 'category': 'switches', 'interfaces': [{'name': 'FastEthernet0/1', 'status': 'up'}, {'name': 'GigabitEthernet0/1', 'status': 'up'}]},
                {'id': 'r1', 'name': 'Router1', 'category': 'routers', 'ip': '192.168.1.1', 'interfaces': [
                    {'name': 'Gi0/0', 'ip': '192.168.1.1', 'mask': '255.255.255.0', 'status': 'up'},
                    {'name': 'Gi0/1', 'ip': '10.0.0.1', 'mask': '255.255.255.0', 'status': 'up'}
                ]},
                {'id': 'srv1', 'name': 'WebServer', 'category': 'servers', 'ip': '10.0.0.100', 'subnet_mask': '255.255.255.0', 'gateway': '10.0.0.1', 'interfaces': [{'name': 'eth0', 'status': 'up'}]}
            ],
            'connections': [
                {'id': 'c1', 'source_device': 'pc1', 'source_port': 'eth0', 'target_device': 'sw1', 'target_port': 'fa0/1', 'status': 'connected'},
                {'id': 'c2', 'source_device': 'sw1', 'source_port': 'Gi0/1', 'target_device': 'r1', 'target_port': 'g0/0', 'status': 'connected'},
                {'id': 'c3', 'source_device': 'r1', 'source_port': 'GigabitEthernet 0/1', 'target_device': 'srv1', 'target_port': 'eth0', 'status': 'connected'}
            ]
        }
        engine = NetworkSimulationEngine(mixed_topo)
        res = engine.simulate_packet('pc1', '10.0.0.100', protocol='ICMP')
        self.assertTrue(res['success'], f"Failed: {res.get('drop_reason')} - {res.get('details')}")
        self.assertEqual(res['hops'][-1]['device_name'], 'WebServer')
