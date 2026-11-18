import json
from django.test import TestCase, Client
from django.urls import reverse

class MonitoringAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_monitoring_dashboard_view(self):
        resp = self.client.get(reverse('monitoring:dashboard'))
        self.assertEqual(resp.status_code, 200)

    def test_monitoring_stats_api(self):
        resp = self.client.get(reverse('monitoring:stats_api'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('health_score', data)
        self.assertIn('total_packets', data)
        self.assertIn('traffic_history', data)

    def test_security_audit_view(self):
        resp = self.client.get(reverse('monitoring:security_audit'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Network Security Assessment')

    def test_api_run_security_audit(self):
        resp = self.client.post(
            reverse('monitoring:api_run_security_audit'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('security_score', data)
        self.assertIn('findings', data)
        self.assertGreater(data['total_findings'], 0)

    def test_capacity_view(self):
        resp = self.client.get(reverse('monitoring:capacity'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Network Health & Capacity Planning')

    def test_api_capacity_stats(self):
        resp = self.client.get(reverse('monitoring:api_capacity_stats'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('overall_utilization_pct', data)
        self.assertIn('interfaces', data)
        self.assertIn('hourly_bandwidth', data)

    def test_alerts_view(self):
        resp = self.client.get(reverse('monitoring:alerts'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Network Event & Alert Centre')

    def test_alert_lifecycle_api(self):
        # 1. List alerts
        resp = self.client.get(reverse('monitoring:api_get_alerts'))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(len(data['alerts']), 0)
        first_alert = data['alerts'][0]
        alert_id = first_alert['id']

        # 2. Acknowledge alert
        ack_resp = self.client.post(
            reverse('monitoring:api_acknowledge_alert'),
            data=json.dumps({'alert_id': alert_id}),
            content_type='application/json'
        )
        self.assertEqual(ack_resp.status_code, 200)
        self.assertEqual(ack_resp.json()['alert']['status'], 'acknowledged')

        # 3. Resolve alert
        res_resp = self.client.post(
            reverse('monitoring:api_resolve_alert'),
            data=json.dumps({'alert_id': alert_id}),
            content_type='application/json'
        )
        self.assertEqual(res_resp.status_code, 200)
        self.assertEqual(res_resp.json()['alert']['status'], 'resolved')
