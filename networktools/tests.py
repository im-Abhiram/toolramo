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

    def test_subnet_calculator_view(self):
        resp = self.client.get(reverse('networktools:subnet_calculator'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Subnet Calculator')
        self.assertContains(resp, 'RFC 4632 CIDR')

    def test_ports_cheatsheet_view(self):
        resp = self.client.get(reverse('networktools:ports_cheatsheet'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Common Network Ports Cheat Sheet')
        self.assertContains(resp, 'SSH / SFTP')

    def test_osi_model_view(self):
        resp = self.client.get(reverse('networktools:osi_model'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'OSI 7-Layer Model')
        self.assertContains(resp, 'Application Layer')

    def test_sitemap_xml(self):
        resp = self.client.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('application/xml', resp.headers.get('Content-Type', '') or resp.headers.get('content-type', ''))
        self.assertContains(resp, '<urlset')
        self.assertContains(resp, 'subnet-calculator')

    def test_robots_txt(self):
        resp = self.client.get('/robots.txt')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/plain', resp.headers.get('Content-Type', ''))
        self.assertContains(resp, 'User-agent: *')
        self.assertContains(resp, 'Sitemap:')
