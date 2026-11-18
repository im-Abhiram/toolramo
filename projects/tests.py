import json
from django.test import TestCase, Client
from django.urls import reverse

class ProjectsAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_project_manager_view(self):
        resp = self.client.get(reverse('projects:manager'))
        self.assertEqual(resp.status_code, 200)

    def test_documentation_view(self):
        resp = self.client.get(reverse('projects:documentation'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Network Infrastructure Documentation Generator')

    def test_api_export_documentation_json(self):
        payload = {
            'format': 'json',
            'project_name': 'Test-Network',
            'devices': [{'name': 'R1', 'category': 'Router', 'ip': '192.168.1.1'}]
        }
        resp = self.client.post(
            reverse('projects:api_export_documentation'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['generator'], 'Ramonet Network Architecture Suite')
        self.assertEqual(data['project']['name'], 'Test-Network')
        self.assertEqual(len(data['devices']), 1)

    def test_api_export_documentation_csv(self):
        payload = {
            'format': 'csv',
            'project_name': 'Test-Network',
            'devices': [{'name': 'R1', 'category': 'Router', 'role': 'Gateway', 'ip': '192.168.1.1', 'interfaces': ['Gi0/0']}]
        }
        resp = self.client.post(
            reverse('projects:api_export_documentation'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="Test-Network_Inventory.csv"', resp['Content-Disposition'])

    def test_scenarios_view(self):
        resp = self.client.get(reverse('projects:scenarios'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Network Scenario Library')
        self.assertContains(resp, '1. Basic Home Office LAN')
        self.assertContains(resp, '16. Zero-Trust Micro-Segmentation')

    def test_changes_view(self):
        resp = self.client.get(reverse('projects:changes'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Network Change Management & Snapshot Diffs')

    def test_api_snapshot_diff(self):
        payload = {
            'device_name': 'Switch-1',
            'config_before': 'hostname Switch-1\nvlan 10\n name Staff\nend',
            'config_after': 'hostname Switch-1\nvlan 10\n name Staff\nvlan 20\n name Guests\nend'
        }
        resp = self.client.post(
            reverse('projects:api_snapshot_diff'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data['is_identical'])
        self.assertGreater(data['lines_added'], 0)

    def test_backups_view(self):
        resp = self.client.get(reverse('projects:backups'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Configuration Backup & Safe Restore')

    def test_api_backup_restore(self):
        # Clean payload
        clean_payload = {
            'devices': [
                {'name': 'R1', 'ip': '192.168.1.1'},
                {'name': 'PC1', 'ip': '192.168.1.10', 'gateway': '192.168.1.1'}
            ],
            'connections': []
        }
        resp = self.client.post(
            reverse('projects:api_backup_restore'),
            data=json.dumps(clean_payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['is_valid'])
        self.assertEqual(data['device_count'], 2)
