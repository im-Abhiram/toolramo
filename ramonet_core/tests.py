from django.test import TestCase
from ramonet_core import (
    DeviceRegistry,
    DeviceCapabilityManager,
    DeviceConfigurationService,
    CommandParser,
    CommandExecutor,
    ConfigurationValidator,
    InterfaceManager,
    ConnectionManager,
    UnifiedSimulationEngine,
    ConfigurationHistoryManager,
    EventLogger,
)

class RamonetCoreArchitectureTests(TestCase):
    def test_device_registry_specs(self):
        switch_cap = DeviceRegistry.get_default_capabilities('switches')
        self.assertIsNotNone(switch_cap)
        self.assertEqual(switch_cap.rack_units, 1)
        self.assertEqual(switch_cap.cli_platform, 'cisco_ios')
        self.assertTrue(switch_cap.supports_vlans)

        router_cap = DeviceRegistry.get_default_capabilities('routers')
        self.assertIsNotNone(router_cap)
        self.assertEqual(router_cap.rack_units, 2)
        self.assertTrue(router_cap.supports_routing)

    def test_device_config_service_mutation(self):
        dev = {
            'id': 'sw1',
            'name': 'OldSwitch',
            'category': 'switches',
            'vlans': {'1': {'name': 'default'}},
            'interfaces': [{'name': 'Gig1/0/1', 'mode': 'access', 'vlan': 1, 'status': 'up'}]
        }

        # Change hostname
        DeviceConfigurationService.set_hostname(dev, 'CoreSwitch-01')
        self.assertEqual(dev['name'], 'CoreSwitch-01')

        # Add VLAN 20
        DeviceConfigurationService.add_vlan(dev, 20, 'Engineering')
        self.assertIn('20', dev['vlans'])
        self.assertEqual(dev['vlans']['20']['name'], 'Engineering')

        # Assign port to VLAN 20
        DeviceConfigurationService.set_interface_mode(dev, 'Gig1/0/1', 'access', vlan=20)
        self.assertEqual(dev['interfaces'][0]['vlan'], 20)

        # Generate running config
        config_text = DeviceConfigurationService.generate_running_config(dev)
        self.assertIn('hostname CoreSwitch-01', config_text)
        self.assertIn('vlan 20', config_text)
        self.assertIn('switchport access vlan 20', config_text)

    def test_command_executor_cisco_ios(self):
        dev = {
            'id': 'sw1',
            'name': 'Switch',
            'category': 'switches',
            'vlans': {'1': {'name': 'default'}},
            'interfaces': [{'name': 'FastEthernet0/1', 'status': 'up'}]
        }

        # Valid VLAN command
        res = CommandExecutor.execute(dev, 'vlan 30', platform='cisco_ios')
        self.assertTrue(res['success'])
        self.assertIn('30', dev['vlans'])

        # Valid interface access command
        res2 = CommandExecutor.execute(dev, 'switchport access vlan 30', platform='cisco_ios')
        self.assertTrue(res2['success'])

        # Invalid command rejection (No fake successes!)
        res3 = CommandExecutor.execute(dev, 'completely-invalid-junk-command', platform='cisco_ios')
        self.assertFalse(res3['success'])
        self.assertIn('Invalid command syntax', res3['output'])

    def test_configuration_validator(self):
        # Validate IPv4
        self.assertTrue(ConfigurationValidator.validate_ipv4('192.168.1.1'))
        self.assertFalse(ConfigurationValidator.validate_ipv4('999.168.1.1'))

        # Subnet checking
        self.assertTrue(ConfigurationValidator.is_same_subnet('192.168.1.10', '192.168.1.20', '255.255.255.0'))
        self.assertFalse(ConfigurationValidator.is_same_subnet('192.168.1.10', '192.168.2.20', '255.255.255.0'))

        # Duplicate IP detection
        devices = [
            {'name': 'Dev1', 'ip': '10.0.0.1'},
            {'name': 'Dev2', 'ip': '10.0.0.1'},
            {'name': 'Dev3', 'ip': '10.0.0.2'}
        ]
        dups = ConfigurationValidator.check_duplicate_ips(devices)
        self.assertEqual(len(dups), 1)
        self.assertEqual(dups[0]['ip'], '10.0.0.1')

        # Rack overlap check
        units = [
            {'start_u': 1, 'size_u': 2}, # takes 1, 2
            {'start_u': 2, 'size_u': 1}  # collides on 2!
        ]
        overlap_res = ConfigurationValidator.validate_rack_unit_overlap(units, max_u=42)
        self.assertFalse(overlap_res['valid'])
        self.assertGreater(len(overlap_res['errors']), 0)

    def test_poe_power_calculations(self):
        switch = {
            'id': 'sw1',
            'power_budget_watts': 370.0,
            'interfaces': [
                {'name': 'Fa0/1', 'poe_draw_watts': 12.0},
                {'name': 'Fa0/2', 'poe_draw_watts': 25.5}
            ]
        }
        summary = InterfaceManager.calculate_poe_power(switch)
        self.assertEqual(summary['total_drawn_watts'], 37.5)
        self.assertAlmostEqual(summary['available_margin_watts'], 370.0 - 37.5, places=1)
        self.assertFalse(summary['is_overloaded'])

    def test_unified_simulation_engine(self):
        devices = [
            {'id': 'pc1', 'name': 'PC1', 'ip': '192.168.1.10', 'subnet_mask': '255.255.255.0', 'gateway': '192.168.1.1'},
            {'id': 'r1', 'name': 'Router1', 'ip': '192.168.1.1', 'subnet_mask': '255.255.255.0', 'interfaces': [{'name': 'Gi0/0', 'ip': '192.168.1.1', 'status': 'up'}, {'name': 'Gi0/1', 'ip': '10.0.0.1', 'status': 'up'}]},
            {'id': 'srv1', 'name': 'Server1', 'ip': '10.0.0.100', 'subnet_mask': '255.255.255.0', 'gateway': '10.0.0.1'}
        ]
        connections = [
            {'source_device': 'pc1', 'source_port': 'eth0', 'target_device': 'r1', 'target_port': 'Gi0/0'},
            {'source_device': 'r1', 'source_port': 'Gi0/1', 'target_device': 'srv1', 'target_port': 'eth0'}
        ]

        engine = UnifiedSimulationEngine(devices=devices, connections=connections)
        sim_res = engine.simulate_packet(src_dev_id='pc1', dest_ip='10.0.0.100', protocol='ICMP')
        self.assertTrue(sim_res['success'])
        self.assertGreaterEqual(len(sim_res['hops']), 2)
        self.assertEqual(sim_res['hops'][-1]['device_id'], 'srv1')

    def test_history_diff_manager(self):
        before = "hostname R1\ninterface Gi0/0\n ip address 10.0.0.1 255.255.255.0\n"
        after = "hostname R1\ninterface Gi0/0\n ip address 10.0.0.2 255.255.255.0\n"
        diff_lines = ConfigurationHistoryManager.compute_unified_diff(before, after)
        self.assertGreater(len(diff_lines), 0)
        self.assertTrue(any('- ip address 10.0.0.1' in l for l in diff_lines))
        self.assertTrue(any('+ ip address 10.0.0.2' in l for l in diff_lines))

    def test_event_logger(self):
        logger = EventLogger()
        evt = logger.log('warning', 'Link Flap', 'Gig0/1 flapped 3 times', device_id='sw1')
        self.assertEqual(evt['severity'], 'warning')
        self.assertEqual(len(logger.get_active_alerts()), 1)
        logger.acknowledge_alert(evt['id'])
        self.assertEqual(len(logger.get_active_alerts()), 0)
