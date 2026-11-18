import json
from django.test import TestCase, Client
from django.urls import reverse

class NetworkToolsAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_toolbox_view(self):
        resp = self.client.get(reverse('networktools:toolbox'))
        self.assertEqual(resp.status_code, 200)

    def test_discovery_view(self):
        resp = self.client.get(reverse('networktools:discovery'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Network Discovery & Automated Inventory')

    def test_api_run_discovery_lldp(self):
        resp = self.client.post(
            reverse('networktools:api_run_discovery'),
            data=json.dumps({'protocol': 'lldp'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['protocol'], 'LLDP')
        self.assertEqual(data['scan_status'], 'Completed')
        self.assertGreater(data['discovered_devices_count'], 0)
        self.assertGreater(len(data['arp_table']), 0)
        self.assertGreaterEqual(data['rogue_devices_detected'], 1)
