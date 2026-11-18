from django.test import TestCase
from django.contrib.auth import get_user_model
from projects.models import NetworkProject
from projects.digital_twin import DigitalTwinManager
from simulation.protocol_analyzer import ProtocolAnalyzerEngine
from simulation.what_if_engine import WhatIfEngine
from configuration.automation_studio import NetworkAutomationStudio
from configuration.compliance_engine import ComplianceEngine
from monitoring.ha_engine import HighAvailabilityEngine
from monitoring.qos_engine import QoSEngine
from topology.cable_tracer import CableTracer
from networktools.capacity_cost_planner import CapacityCostPlanner
from troubleshooting.incident_engine import IncidentResponseEngine

User = get_user_model()


class NetworkDigitalTwinTests(TestCase):
    """Test Suite for Module 1: Network Digital Twin"""

    def setUp(self):
        self.user = User.objects.create_user(username='twin_tester', password='SecTestPassword123!')
        self.project = NetworkProject.objects.create(
            user=self.user,
            name='Enterprise Production Network',
            description='Production core topology',
            metadata={
                'devices': [
                    {'id': 'core-sw-01', 'name': 'Core-SW01', 'category': 'Switch', 'ip': '10.0.0.1', 'vlan': 1},
                    {'id': 'acc-sw-01', 'name': 'Access-SW01', 'category': 'Switch', 'ip': '10.0.0.2', 'vlan': 10}
                ],
                'connections': [
                    {'id': 'conn-1', 'source': 'core-sw-01', 'target': 'acc-sw-01', 'cable': 'fiber', 'source_port': 'Gig1/1/1', 'target_port': 'Gig0/1'}
                ]
            }
        )

    def test_create_digital_twin(self):
        success, twin, msg = DigitalTwinManager.create_twin(self.project.id, 'Enterprise Twin Sandbox', self.user)
        self.assertTrue(success)
        self.assertIsNotNone(twin)
        self.assertEqual(twin.name, 'Enterprise Twin Sandbox')
        self.assertTrue(twin.metadata['twin_metadata']['is_digital_twin'])
        self.assertEqual(twin.metadata['twin_metadata']['original_project_id'], self.project.id)

    def test_compare_digital_twin_diff(self):
        success, twin, msg = DigitalTwinManager.create_twin(self.project.id, 'Enterprise Twin Diff', self.user)
        self.assertTrue(success)

        # Modify twin metadata: modify existing device, add new firewall
        twin_meta = twin.metadata
        twin_meta['devices'][0]['name'] = 'Core-SW01-Upgraded'
        twin_meta['devices'].append({'id': 'fw-01', 'name': 'Perimeter-FW', 'category': 'Firewall', 'ip': '10.0.0.254'})
        twin.metadata = twin_meta
        twin.save()

        diff = DigitalTwinManager.compare_twin(self.project.id, twin.id)
        self.assertIn('summary', diff)
        self.assertEqual(diff['summary']['devices_added'], 1)
        self.assertEqual(diff['summary']['devices_modified'], 1)
        self.assertEqual(diff['added_devices'][0]['id'], 'fw-01')
        self.assertEqual(diff['modified_devices'][0]['device_id'], 'core-sw-01')

    def test_commit_digital_twin_to_production(self):
        success, twin, msg = DigitalTwinManager.create_twin(self.project.id, 'Enterprise Twin Commit', self.user)
        self.assertTrue(success)

        twin_meta = twin.metadata
        twin_meta['devices'][0]['name'] = 'Core-SW01-Committed'
        twin.metadata = twin_meta
        twin.save()

        commit_ok, commit_msg = DigitalTwinManager.commit_to_production(self.project.id, twin.id)
        self.assertTrue(commit_ok)
        self.project.refresh_from_db()
        self.assertEqual(self.project.metadata['devices'][0]['name'], 'Core-SW01-Committed')

    def test_discard_digital_twin(self):
        success, twin, msg = DigitalTwinManager.create_twin(self.project.id, 'Enterprise Twin Discard', self.user)
        self.assertTrue(success)
        twin_id = twin.id
        discard_ok, discard_msg = DigitalTwinManager.discard_twin(twin_id)
        self.assertTrue(discard_ok)
        self.assertFalse(NetworkProject.objects.filter(id=twin_id).exists())


class ProtocolAnalyzerTests(TestCase):
    """Test Suite for Module 2: Packet Capture & Protocol Analyzer"""

    def test_generate_arp_packet_capture(self):
        packets = ProtocolAnalyzerEngine.generate_capture('arp_resolution')
        self.assertGreaterEqual(len(packets), 2)
        arp_req = packets[0]
        self.assertEqual(arp_req['protocol'], 'ARP')
        self.assertEqual(arp_req['action'], 'BROADCAST')
        self.assertIn('osi_layers', arp_req)
        self.assertIn('layer_1_physical', arp_req['osi_layers'])
        self.assertIn('layer_2_datalink', arp_req['osi_layers'])
        self.assertIn('layer_3_network', arp_req['osi_layers'])
        self.assertIn('hex_dump', arp_req)

    def test_generate_dhcp_dora_capture(self):
        packets = ProtocolAnalyzerEngine.generate_capture('dhcp_dora')
        self.assertEqual(len(packets), 4)  # Discover, Offer, Request, ACK
        self.assertIn('DHCP Discover', packets[0]['info'])
        self.assertIn('DHCP Offer', packets[1]['info'])
        self.assertIn('DHCP Request', packets[2]['info'])
        self.assertIn('DHCP ACK', packets[3]['info'])

    def test_generate_dns_and_http_capture(self):
        dns_packets = ProtocolAnalyzerEngine.generate_capture('dns_query')
        self.assertGreaterEqual(len(dns_packets), 2)
        self.assertEqual(dns_packets[0]['protocol'], 'UDP')
        self.assertIn('Standard query', dns_packets[0]['info'])

        http_packets = ProtocolAnalyzerEngine.generate_capture('http_session')
        self.assertGreaterEqual(len(http_packets), 4)
        self.assertEqual(http_packets[0]['protocol'], 'TCP')

    def test_wireshark_syntax_filtering(self):
        packets = ProtocolAnalyzerEngine.generate_capture('dhcp_dora')
        filtered_bootp = ProtocolAnalyzerEngine.filter_packets(packets, 'udp')
        self.assertEqual(len(filtered_bootp), 4)
        filtered_empty = ProtocolAnalyzerEngine.filter_packets(packets, 'icmp')
        self.assertEqual(len(filtered_empty), 0)


class WhatIfSimulationTests(TestCase):
    """Test Suite for Module 3: What-If Simulation Engine"""

    def setUp(self):
        self.topology = {
            'devices': [
                {'id': 'sw-core', 'name': 'Core-Switch', 'category': 'switches', 'ip': '10.0.0.1'},
                {'id': 'sw-acc-1', 'name': 'Access-01', 'category': 'switches', 'ip': '10.0.0.10'},
                {'id': 'r-gw', 'name': 'Gateway-Router', 'category': 'routers', 'ip': '10.0.0.254'},
                {'id': 'fw-1', 'name': 'Perimeter-FW', 'category': 'firewalls', 'ip': '10.0.0.253'}
            ],
            'connections': [
                {'id': 'c1', 'source': 'sw-core', 'target': 'sw-acc-1'},
                {'id': 'c2', 'source': 'sw-core', 'target': 'r-gw'},
                {'id': 'c3', 'source': 'r-gw', 'target': 'fw-1'}
            ]
        }

    def test_core_switch_failure_scenario(self):
        result = WhatIfEngine.evaluate_scenario('CORE_SWITCH_FAIL', self.topology)
        self.assertEqual(result['scenario']['key'], 'CORE_SWITCH_FAIL')
        self.assertEqual(result['risk_level'], 'CRITICAL')
        self.assertLess(result['metrics']['reachability_after'], result['metrics']['reachability_before'])
        self.assertGreater(len(result['affected_devices']), 0)
        self.assertGreater(len(result['mitigation_advice']), 0)

    def test_wan_link_drop_scenario(self):
        result = WhatIfEngine.evaluate_scenario('WAN_LINK_DROP', self.topology)
        self.assertEqual(result['scenario']['key'], 'WAN_LINK_DROP')
        self.assertEqual(result['risk_level'], 'HIGH')
        self.assertLess(result['metrics']['reachability_after'], result['metrics']['reachability_before'])
        self.assertEqual(result['metrics']['reachability_after'], 45.0)

    def test_cctv_bandwidth_surge_scenario(self):
        result = WhatIfEngine.evaluate_scenario('ADD_CCTV_CAMERAS', self.topology, {'camera_count': 50})
        self.assertEqual(result['scenario']['key'], 'ADD_CCTV_CAMERAS')
        self.assertEqual(result['risk_level'], 'HIGH')
        self.assertGreater(result['metrics']['latency_after_ms'], result['metrics']['latency_before_ms'])


class NetworkAutomationStudioTests(TestCase):
    """Test Suite for Module 4: Network Automation Studio"""

    def setUp(self):
        self.devices = [
            {'id': 'sw1', 'name': 'SW-Floor1', 'category': 'managed_switch', 'vlans': [1], 'interfaces': [{'name': 'Gig0/1', 'type': 'access'}]},
            {'id': 'sw2', 'name': 'SW-Floor2', 'category': 'managed_switch', 'vlans': [1], 'interfaces': [{'name': 'Gig0/1', 'type': 'access'}]}
        ]

    def test_automation_dry_run_does_not_mutate(self):
        result = NetworkAutomationStudio.execute_playbook('PROVISION_VLANS', self.devices, dry_run=True)
        self.assertTrue(result['dry_run'])
        self.assertEqual(result['summary']['total_devices_scanned'], 2)
        # Verify original devices unchanged
        self.assertEqual(self.devices[0]['vlans'], [1])
        self.assertEqual(self.devices[1]['vlans'], [1])
        self.assertFalse(result['rollback_available'])

    def test_automation_live_execution(self):
        result = NetworkAutomationStudio.execute_playbook('PROVISION_VLANS', self.devices, dry_run=False)
        self.assertFalse(result['dry_run'])
        self.assertTrue(result['rollback_available'])
        self.assertEqual(result['summary']['devices_modified'], 2)
        # Verify target switches now have VLANs 10, 20, 30, 99
        self.assertIn(10, self.devices[0]['vlans'])
        self.assertIn(20, self.devices[0]['vlans'])
        self.assertIn(99, self.devices[0]['vlans'])

    def test_automation_port_security_lockdown(self):
        result = NetworkAutomationStudio.execute_playbook('PORT_SECURITY_LOCKDOWN', self.devices, dry_run=False)
        self.assertFalse(result['dry_run'])
        self.assertEqual(result['summary']['devices_modified'], 2)
        self.assertTrue(self.devices[0]['interfaces'][0].get('port_security'))
        self.assertTrue(self.devices[0]['interfaces'][0].get('bpdu_guard'))


class ComplianceEngineTests(TestCase):
    """Test Suite for Module 5: Configuration Compliance Centre"""

    def test_compliance_audit_scoring(self):
        devices = [
            {
                'name': 'Core-SW01',
                'category': 'managed_switch',
                'management_vlan': 1,  # Fails SEC-001 (Management on VLAN 1)
                'telnet_enabled': True,  # Fails SEC-003 (Telnet cleartext enabled)
                'bpdu_guard_enabled': False  # Warns SEC-006
            },
            {
                'name': 'Edge-FW01',
                'category': 'firewall',
                'firewall': {'default_policy': 'allow'}  # Fails SEC-004 (Default permit any)
            }
        ]
        report = ComplianceEngine.audit_topology(devices)
        self.assertIn('compliance_score', report)
        self.assertLess(report['compliance_score'], 100)
        self.assertIn('summary', report)
        self.assertIn('rules', report)
        self.assertIn('remediation_scripts', report)
        self.assertIn('Core-SW01', report['remediation_scripts'])
        self.assertTrue(any('interface Vlan99' in script for script in report['remediation_scripts']['Core-SW01']))

    def test_perfect_compliance_score(self):
        devices = [
            {
                'name': 'SW-Hardened',
                'category': 'managed_switch',
                'management_vlan': 99,
                'interfaces': [],
                'telnet_enabled': False,
                'ntp_configured': True,
                'bpdu_guard_enabled': True,
                'ip': '10.99.0.2'
            },
            {
                'name': 'FW-Hardened',
                'category': 'firewall',
                'firewall': {'default_policy': 'deny'},
                'ntp_configured': True,
                'telnet_enabled': False,
                'ip': '10.99.0.1'
            }
        ]
        report = ComplianceEngine.audit_topology(devices)
        self.assertGreaterEqual(report['compliance_score'], 85)


class HighAvailabilityEngineTests(TestCase):
    """Test Suite for Module 6: High Availability and Redundancy Lab"""

    def test_stp_convergence_normal_and_fault(self):
        normal = HighAvailabilityEngine.simulate_ha_scenario('STP', fault_injected=False)
        self.assertEqual(normal['protocol'], 'STP / RSTP (IEEE 802.1w)')
        self.assertFalse(normal['fault_injected'])
        self.assertTrue(normal['loop_prevented'])
        # Confirm at least one blocking port in triangle
        has_blocking = any(l['state'] == 'BLOCKING' for l in normal['links'])
        self.assertTrue(has_blocking)

        fault = HighAvailabilityEngine.simulate_ha_scenario('STP', fault_injected=True)
        self.assertTrue(fault['fault_injected'])
        self.assertGreater(fault['convergence_time_ms'], 0)
        has_severed = any(l['state'] == 'SEVERED' for l in fault['links'])
        self.assertTrue(has_severed)

    def test_vrrp_failover_simulation(self):
        normal = HighAvailabilityEngine.simulate_ha_scenario('VRRP', fault_injected=False)
        self.assertEqual(normal['virtual_ip'], '192.168.1.1')
        self.assertIn('R1-Master', normal['active_gateway'])

        fault = HighAvailabilityEngine.simulate_ha_scenario('VRRP', fault_injected=True)
        self.assertIn('R2-Backup', fault['active_gateway'])
        self.assertGreater(fault['failover_time_ms'], 0)

    def test_lacp_port_channel_aggregation(self):
        normal = HighAvailabilityEngine.simulate_ha_scenario('LACP', fault_injected=False)
        self.assertEqual(normal['aggregated_bandwidth'], '2 Gbps Full-Duplex')
        self.assertEqual(len(normal['member_links']), 2)

        fault = HighAvailabilityEngine.simulate_ha_scenario('LACP', fault_injected=True)
        self.assertIn('1 Gbps', fault['aggregated_bandwidth'])


class QoSTrafficEngineeringTests(TestCase):
    """Test Suite for Module 7: QoS and Traffic Engineering"""

    def test_qos_prioritization_under_congestion(self):
        res_qos_on = QoSEngine.simulate_qos_comparison(qos_enabled=True, bottleneck_capacity_mbps=10.0)
        res_qos_off = QoSEngine.simulate_qos_comparison(qos_enabled=False, bottleneck_capacity_mbps=10.0)

        voice_on = next(c for c in res_qos_on['classes'] if 'Voice' in c['name'])
        voice_off = next(c for c in res_qos_off['classes'] if 'Voice' in c['name'])

        self.assertEqual(voice_on['loss_percentage'], 0.0)
        self.assertGreater(voice_off['loss_percentage'], 10.0)
        self.assertLess(voice_on['latency_ms'], voice_off['latency_ms'])
        self.assertLess(voice_on['jitter_ms'], voice_off['jitter_ms'])


class CablePortTracerTests(TestCase):
    """Test Suite for Module 8: Intelligent Cable & Port Tracing"""

    def test_trace_cable_path_resolution(self):
        src_dev = {'name': 'Workstation-01', 'category': 'Host', 'vlan': 10, 'ip': '10.10.0.45'}
        dst_dev = {'name': 'App-Server-01', 'category': 'Server', 'vlan': 10, 'ip': '10.10.0.100'}
        result = CableTracer.trace_path(src_dev, 'Gig0/1', dst_dev)
        self.assertTrue(result['path_valid'])
        self.assertEqual(result['total_hops'], 6)
        self.assertEqual(result['source']['name'], 'Workstation-01')
        self.assertEqual(result['destination']['name'], 'App-Server-01')
        self.assertGreater(len(result['hops']), 0)
        self.assertGreater(len(result['diagnostics']), 0)

    def test_cable_mismatched_vlan_warning(self):
        src_dev = {'name': 'Camera-01', 'category': 'Camera', 'vlan': 30, 'ip': '10.30.0.12'}
        dst_dev = {'name': 'File-Server', 'category': 'Server', 'vlan': 20, 'ip': '10.20.0.50'}
        result = CableTracer.trace_path(src_dev, 'eth0', dst_dev)
        warnings = [d['message'] for d in result['diagnostics'] if d['severity'] == 'WARNING']
        self.assertTrue(any('Inter-VLAN' in w for w in warnings))


class CapacityCostPlannerTests(TestCase):
    """Test Suite for Module 9: Network Capacity & Cost Planner"""

    def test_bom_and_capacity_estimation(self):
        params = {
            'workstations': 50,
            'voip_phones': 40,
            'access_points': 6,
            'cameras': 16,
            'servers': 4,
            'retention_days': 30
        }
        res = CapacityCostPlanner.calculate_plan(params)
        self.assertIn('inputs', res)
        self.assertIn('port_density', res)
        self.assertIn('poe_budget', res)
        self.assertIn('rack_thermal', res)
        self.assertIn('ups_storage', res)
        self.assertIn('budgetary_bom', res)

        bom = res['budgetary_bom']
        self.assertGreater(bom['total_estimated_capex'], 0)
        self.assertIn('DISCLAIMER', bom['disclaimer'])
        self.assertGreater(len(bom['items']), 0)


class IncidentResponseSimulatorTests(TestCase):
    """Test Suite for Module 10: Network Incident Response Simulator"""

    def test_incident_scenario_details(self):
        sc = IncidentResponseEngine.get_scenario_details('ROGUE_DHCP')
        self.assertIsNotNone(sc)
        self.assertEqual(sc['severity'], 'CRITICAL')
        self.assertIn('Syslog:', sc['indicator'])
        self.assertIn('Switchport Gi0/14', sc['affected_node'])

    def test_incident_containment_action(self):
        action = 'Shutdown switchport Gi0/14 and enable DHCP Snooping'
        result = IncidentResponseEngine.execute_containment('ROGUE_DHCP', action)
        self.assertTrue(result['success'])
        self.assertIn('incident_report', result)
        report = result['incident_report']
        self.assertEqual(report['status'], 'CONTAINED & MITIGATED')
        self.assertEqual(report['residual_risk'], 'LOW')
        self.assertGreater(len(report['timeline']), 0)
        self.assertGreater(len(report['follow_up_recommendations']), 0)
