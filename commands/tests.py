from django.test import TestCase
from commands.cli_engine import DeviceCLISession

class CLISimulationEngineTests(TestCase):
    def setUp(self):
        self.router_data = {
            'id': 'r1',
            'name': 'EdgeRouter',
            'cli_platform': 'cisco_ios',
            'interfaces': [
                {'name': 'GigabitEthernet0/0', 'ip': '', 'mask': '', 'status': 'administratively_down'}
            ],
            'routes': [],
            'vlans': {}
        }
        self.session = DeviceCLISession(self.router_data)

    def test_cisco_mode_transitions(self):
        """Test User EXEC -> Privileged EXEC -> Global Config -> Interface Config"""
        self.assertEqual(self.session.get_prompt(), 'EdgeRouter>')
        
        self.session.execute('enable')
        self.assertEqual(self.session.get_prompt(), 'EdgeRouter#')
        
        self.session.execute('configure terminal')
        self.assertEqual(self.session.get_prompt(), 'EdgeRouter(config)#')
        
        self.session.execute('interface GigabitEthernet0/0')
        self.assertEqual(self.session.get_prompt(), 'EdgeRouter(config-if)#GigabitEthernet0/0')
        
        self.session.execute('exit')
        self.assertEqual(self.session.get_prompt(), 'EdgeRouter(config)#')
        
        self.session.execute('end')
        self.assertEqual(self.session.get_prompt(), 'EdgeRouter#')

    def test_interface_configuration_mutation(self):
        """Test that configuring an IP address and 'no shutdown' mutates device state"""
        self.session.execute('enable')
        self.session.execute('configure terminal')
        self.session.execute('interface GigabitEthernet0/0')
        
        # Configure IP & enable
        self.session.execute('ip address 192.168.1.1 255.255.255.0')
        self.session.execute('no shutdown')
        
        iface = self.router_data['interfaces'][0]
        self.assertEqual(iface['ip'], '192.168.1.1')
        self.assertEqual(iface['mask'], '255.255.255.0')
        self.assertEqual(iface['status'], 'up')

    def test_show_ip_interface_brief(self):
        """Verify dynamic output generation for 'show ip interface brief'"""
        self.session.execute('enable')
        res = self.session.execute('show ip interface brief')
        self.assertIn('GigabitEthernet0/0', res['output'])
        self.assertIn('Interface', res['output'])

    def test_context_help(self):
        """Verify '?' context-sensitive help"""
        res = self.session.execute('?')
        self.assertIn('enable', res['output'])
        self.assertIn('ping', res['output'])

    def test_stateful_session_across_requests(self):
        """Verify that passing session_state preserves privileged mode and interfaces across requests"""
        # Request 1: enable
        s1 = DeviceCLISession(self.router_data, session_state={'mode': 'user_exec'})
        r1 = s1.execute('enable')
        self.assertEqual(r1['mode'], 'priv_exec')
        self.assertEqual(r1['prompt'], 'EdgeRouter#')
        state1 = r1['session_state']
        self.assertEqual(state1['mode'], 'priv_exec')

        # Request 2: ? in priv_exec mode
        s2 = DeviceCLISession(self.router_data, session_state=state1)
        r2 = s2.execute('?')
        self.assertEqual(r2['mode'], 'priv_exec')
        self.assertEqual(r2['prompt'], 'EdgeRouter#')
        self.assertIn('configure', r2['output'])
        self.assertNotIn('Turn on privileged commands', r2['output'])

        # Request 3: configure terminal
        r3 = s2.execute('configure terminal')
        self.assertEqual(r3['mode'], 'global_config')
        state3 = r3['session_state']

        # Request 4: interface GigabitEthernet0/0
        s4 = DeviceCLISession(self.router_data, session_state=state3)
        r4 = s4.execute('interface GigabitEthernet0/0')
        self.assertEqual(r4['mode'], 'interface_config')
        self.assertEqual(r4['session_state']['current_interface'], 'GigabitEthernet0/0')

    def test_space_interface_and_cidr_ip(self):
        """Verify interface with spaces and CIDR notation IP configuration"""
        self.session.execute('enable')
        self.session.execute('configure terminal')
        res_if = self.session.execute('interface FastEthernet 0/1')
        self.assertEqual(self.session.mode, 'interface_config')
        self.assertEqual(self.session.current_interface, 'FastEthernet0/1')

        self.session.execute('ip address 10.10.10.1/24')
        self.session.execute('no shut')
        ifc = [i for i in self.router_data['interfaces'] if i['name'] == 'FastEthernet0/1'][0]
        self.assertEqual(ifc['ip'], '10.10.10.1')
        self.assertEqual(ifc['mask'], '255.255.255.0')
        self.assertEqual(ifc['status'], 'up')

    def test_windows_workstation_cli(self):
        """Verify PC / Windows command prompt execution and friendly hints"""
        pc_data = {
            'id': 'pc1',
            'name': 'Client-PC',
            'category': 'computers',
            'ip': '192.168.1.55',
            'subnet_mask': '255.255.255.0',
            'gateway': '192.168.1.1'
        }
        session = DeviceCLISession(pc_data)
        self.assertEqual(session.platform, 'windows_cmd')
        self.assertIn('C:\\Users\\Admin>', session.get_prompt())

        r_ip = session.execute('ipconfig')
        self.assertIn('192.168.1.55', r_ip['output'])

        r_hint = session.execute('enable')
        self.assertIn('Cisco IOS command', r_hint['output'])

    def test_api_execute_endpoint(self):
        """Verify API /api/commands/execute/ works without CSRF restriction"""
        client = self.client
        payload = {
            'command': 'enable',
            'device': self.router_data,
            'session_state': {'mode': 'user_exec'}
        }
        resp = client.post('/api/commands/execute/', payload, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data.get('mode'), 'priv_exec')
