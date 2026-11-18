import json
from django.test import TestCase, Client
from django.urls import reverse

class TopologyRackDesignerTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_designer_view_loads(self):
        resp = self.client.get(reverse('topology:designer'))
        self.assertEqual(resp.status_code, 200)

    def test_rack_view_loads(self):
        resp = self.client.get(reverse('topology:rack'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Physical Network Rack Designer')

    def test_api_validate_rack_valid(self):
        payload = {
            'rack_units': 42,
            'mounted_devices': [
                {'device_id': 'sw1', 'device_name': 'Switch-1', 'start_u': 40, 'size_u': 1, 'power_watts': 150.0},
                {'device_id': 'r1', 'device_name': 'Router-1', 'start_u': 38, 'size_u': 2, 'power_watts': 200.0}
            ]
        }
        resp = self.client.post(
            reverse('topology:api_validate_rack'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['valid'])
        self.assertEqual(data['occupied_u'], 3)
        self.assertEqual(data['free_u'], 39)
        self.assertEqual(data['total_watts'], 350.0)
        self.assertAlmostEqual(data['total_btu_hr'], 350.0 * 3.412142, places=1)

    def test_api_validate_rack_collision(self):
        # Overlapping units 41 (sw1 takes 40, 41; sw2 takes 41)
        payload = {
            'rack_units': 42,
            'mounted_devices': [
                {'device_id': 'sw1', 'device_name': 'Switch-1', 'start_u': 40, 'size_u': 2, 'power_watts': 150.0},
                {'device_id': 'sw2', 'device_name': 'Switch-2', 'start_u': 41, 'size_u': 1, 'power_watts': 100.0}
            ]
        }
        resp = self.client.post(
            reverse('topology:api_validate_rack'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data['valid'])
        self.assertGreater(len(data['errors']), 0)
        self.assertTrue(any('overlap' in err.lower() or 'collides' in err.lower() for err in data['errors']))
