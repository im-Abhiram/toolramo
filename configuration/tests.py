import json
from django.test import TestCase, Client
from django.urls import reverse

class ConfigurationAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_assistant_view(self):
        resp = self.client.get(reverse('configuration:assistant'))
        self.assertEqual(resp.status_code, 200)

    def test_cctv_view(self):
        resp = self.client.get(reverse('configuration:cctv'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'CCTV Surveillance Network Planner')

    def test_cctv_calculate_api_normal(self):
        payload = {
            'cameras': [
                {'name': 'Cam1', 'ip': '192.168.50.11', 'resolution': '1080p', 'codec': 'H.265', 'fps': 30, 'type': 'bullet'},
                {'name': 'Cam2', 'ip': '192.168.50.12', 'resolution': '4K', 'codec': 'H.265', 'fps': 30, 'type': 'ptz'}
            ],
            'nvr_channels': 16,
            'poe_budget_watts': 370.0,
            'retention_days': 30
        }
        resp = self.client.post(
            reverse('configuration:api_cctv_calc'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['camera_count'], 2)
        self.assertGreater(data['total_bandwidth_mbps'], 0)
        self.assertEqual(data['total_poe_watts'], 12.0 + 25.0) # 12W bullet + 25W ptz
        self.assertGreater(data['required_storage_tb'], 0)
        self.assertEqual(len(data['alerts']), 0)

    def test_cctv_calculate_api_channel_and_poe_overflow(self):
        # 10 PTZ cameras (25W * 10 = 250W) on an 8-channel NVR with 130W budget
        cameras = [{'name': f'Cam{i}', 'ip': f'192.168.50.{i}', 'resolution': '4K', 'codec': 'H.264', 'fps': 30, 'type': 'ptz'} for i in range(1, 11)]
        payload = {
            'cameras': cameras,
            'nvr_channels': 8,
            'poe_budget_watts': 130.0,
            'retention_days': 30
        }
        resp = self.client.post(
            reverse('configuration:api_cctv_calc'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['camera_count'], 10)
        # Should have alerts for both channel overflow and PoE overload
        alert_types = [a['type'] for a in data['alerts']]
        self.assertIn('channel_overflow', alert_types)
        self.assertIn('poe_overload', alert_types)

    def test_ipam_view(self):
        resp = self.client.get(reverse('configuration:ipam'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Central IP Address Management')

    def test_ipam_validate_api_duplicates(self):
        payload = {
            'devices': [
                {'name': 'PC1', 'ip': '192.168.1.10', 'gateway': '192.168.1.1'},
                {'name': 'PC2', 'ip': '192.168.1.10', 'gateway': '192.168.1.1'}, # Duplicate IP!
                {'name': 'R1', 'ip': '192.168.1.1', 'gateway': '192.168.1.1'}
            ]
        }
        resp = self.client.post(
            reverse('configuration:api_ipam_validate'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data['valid'])
        self.assertEqual(len(data['duplicates']), 1)
        self.assertEqual(data['duplicates'][0]['ip'], '192.168.1.10')

    def test_ipam_validate_api_clean(self):
        payload = {
            'devices': [
                {'name': 'PC1', 'ip': '192.168.1.10', 'gateway': '192.168.1.1'},
                {'name': 'PC2', 'ip': '192.168.1.11', 'gateway': '192.168.1.1'}
            ]
        }
        resp = self.client.post(
            reverse('configuration:api_ipam_validate'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['valid'])
        self.assertEqual(len(data['duplicates']), 0)
