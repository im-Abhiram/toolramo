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
