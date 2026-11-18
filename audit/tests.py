import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from projects.models import NetworkProject
from audit.models import AuditEvent
from audit.logger import SecurityLogger
from accounts.rate_limiter import login_rate_limiter

class SecurityAuditTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Reset in-memory rate limiter before each test run
        login_rate_limiter.reset_all()
        
        # Test users
        self.user_alice = User.objects.create_user(
            username='alice',
            password='ComplexPassword123!',
            email='alice@example.com'
        )
        self.user_bob = User.objects.create_user(
            username='bob',
            password='ComplexPassword123!',
            email='bob@example.com'
        )
        self.user_staff = User.objects.create_user(
            username='staff_sec',
            password='ComplexPassword123!',
            email='staff@example.com',
            is_staff=True
        )
        self.user_instructor = User.objects.create_user(
            username='instructor_dave',
            password='ComplexPassword123!',
            email='dave@example.com'
        )
        self.user_instructor.profile.role = 'instructor'
        self.user_instructor.profile.save()

    # 1. Access Control & Authorization (IDOR, Role Separation)
    def test_project_manager_cross_user_isolation(self):
        """Verify User A's private project is not leaked to User B or anonymous users."""
        proj_alice_private = NetworkProject.objects.create(
            user=self.user_alice,
            name="Alice Secret Enterprise Core",
            is_public=False
        )
        proj_alice_public = NetworkProject.objects.create(
            user=self.user_alice,
            name="Alice Public Topology",
            is_public=True
        )

        # Anonymous request
        resp = self.client.get(reverse('projects:manager'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Alice Secret Enterprise Core")
        self.assertContains(resp, "Alice Public Topology")

        # Bob request (different user)
        self.client.login(username='bob', password='ComplexPassword123!')
        resp_bob = self.client.get(reverse('projects:manager'))
        self.assertEqual(resp_bob.status_code, 200)
        self.assertNotContains(resp_bob, "Alice Secret Enterprise Core")
        self.assertContains(resp_bob, "Alice Public Topology")
        self.client.logout()

        # Alice request (owner)
        self.client.login(username='alice', password='ComplexPassword123!')
        resp_alice = self.client.get(reverse('projects:manager'))
        self.assertEqual(resp_alice.status_code, 200)
        self.assertContains(resp_alice, "Alice Secret Enterprise Core")
        self.assertContains(resp_alice, "Alice Public Topology")
        self.client.logout()

    def test_settings_requires_login(self):
        """Verify unauthenticated access to user settings is redirected to login."""
        resp = self.client.get(reverse('accounts:settings'))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith(reverse('accounts:login')))

        # Authenticated access succeeds
        self.client.login(username='alice', password='ComplexPassword123!')
        resp_auth = self.client.get(reverse('accounts:settings'))
        self.assertEqual(resp_auth.status_code, 200)
        self.client.logout()

    def test_security_dashboard_access_control(self):
        """Verify Security Dashboard is restricted to staff/instructors/architects."""
        url = reverse('audit:security_dashboard')

        # Anonymous -> redirected to login
        resp_anon = self.client.get(url)
        self.assertEqual(resp_anon.status_code, 302)

        # Regular student (Alice) -> 403 Forbidden
        self.client.login(username='alice', password='ComplexPassword123!')
        resp_student = self.client.get(url)
        self.assertEqual(resp_student.status_code, 403)
        self.client.logout()

        # Staff user -> 200 OK
        self.client.login(username='staff_sec', password='ComplexPassword123!')
        resp_staff = self.client.get(url)
        self.assertEqual(resp_staff.status_code, 200)
        self.assertContains(resp_staff, "Security Operations & Audit Center")
        self.client.logout()

        # Instructor user -> 200 OK
        self.client.login(username='instructor_dave', password='ComplexPassword123!')
        resp_inst = self.client.get(url)
        self.assertEqual(resp_inst.status_code, 200)
        self.client.logout()

    # 2. Authentication & Rate Limiting (CWE-307)
    def test_login_rate_limiting_triggers_after_max_attempts(self):
        """Verify 5 failed attempts locks out the attacker with HTTP 429."""
        login_url = reverse('accounts:login')
        client_ip = '198.51.100.42'

        for i in range(5):
            resp = self.client.post(
                login_url,
                {'username': 'alice', 'password': 'WrongPassword1!'},
                REMOTE_ADDR=client_ip
            )
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, "Invalid username or password")

        # 6th attempt must be blocked by rate limiter
        resp_blocked = self.client.post(
            login_url,
            {'username': 'alice', 'password': 'WrongPassword1!'},
            REMOTE_ADDR=client_ip
        )
        self.assertEqual(resp_blocked.status_code, 429)
        self.assertContains(resp_blocked, "Too many failed login attempts", status_code=429)

    def test_login_open_redirect_prevention(self):
        """Verify open redirect vectors in ?next= are sanitized and rejected."""
        login_url = reverse('accounts:login')
        
        # Test malicious external URLs
        malicious_urls = [
            'https://evil-phishing.com/steal-session',
            '//evil.com',
            'javascript:alert(document.cookie)',
            'http://attacker.com'
        ]

        for bad_url in malicious_urls:
            resp = self.client.post(
                f"{login_url}?next={bad_url}",
                {'username': 'alice', 'password': 'ComplexPassword123!'}
            )
            # Must redirect, but NOT to the external domain
            self.assertEqual(resp.status_code, 302)
            self.assertFalse(resp.url.startswith('https://evil-phishing.com'))
            self.assertFalse(resp.url.startswith('//evil.com'))
            self.assertFalse(resp.url.startswith('http://attacker.com'))
            self.assertTrue(resp.url.startswith(reverse('dashboard')) or resp.url.startswith('/'))
            self.client.logout()

    # 3. CSV Formula Injection Neutralization (CWE-1236)
    def test_csv_formula_injection_sanitization(self):
        """Verify dangerous formula prefixes (=, +, -, @) are sanitized with prepended single quote."""
        payload = {
            'format': 'csv',
            'project_name': 'Formula-Test',
            'devices': [
                {'name': '=cmd|\'/C calc\'!A0', 'category': '+SUM(1+1)', 'role': '-2+5', 'ip': '@malicious_site', 'interfaces': ['Gi0/1']}
            ]
        }
        resp = self.client.post(
            reverse('projects:api_export_documentation'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')
        csv_content = resp.content.decode('utf-8')
        
        # Verify prepended single quote
        self.assertIn("'=cmd|'/C calc'!A0", csv_content)
        self.assertIn("'+SUM(1+1)", csv_content)
        self.assertIn("'-2+5", csv_content)
        self.assertIn("'@malicious_site", csv_content)

    # 4. HTTP Header Injection & Filename Sanitization (CWE-113)
    def test_filename_header_injection_sanitization(self):
        """Verify CRLF characters in export filenames are stripped to prevent HTTP response splitting."""
        payload = {
            'format': 'csv',
            'project_name': "Malicious\r\nSet-Cookie: pwned=1\r\nX-Injected: evil",
            'devices': [{'name': 'R1', 'category': 'Router', 'role': 'Core', 'ip': '10.0.0.1'}]
        }
        resp = self.client.post(
            reverse('projects:api_export_documentation'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        cd_header = resp['Content-Disposition']
        self.assertNotIn('\r', cd_header)
        self.assertNotIn('\n', cd_header)
        # Verify that CRLF injection failed: no separate Set-Cookie header was injected
        self.assertNotIn('pwned=1', resp.cookies)

    # 5. Input Bounds & Resource Exhaustion (DoS Protection)
    def test_rack_layout_validation_bounds(self):
        """Verify absurd rack heights or device counts are rejected."""
        url = reverse('topology:api_validate_rack')

        # Absurd rack U height (> 52U)
        resp = self.client.post(
            url,
            data=json.dumps({'total_rack_u': 999999, 'devices': []}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('total_rack_u must be between', resp.json().get('error', ''))

        # Excessive device count (> 100 devices)
        spam_devices = [{'name': f'Dev-{i}', 'u_height': 1, 'u_start': i+1} for i in range(105)]
        resp_spam = self.client.post(
            url,
            data=json.dumps({'total_rack_u': 42, 'devices': spam_devices}),
            content_type='application/json'
        )
        self.assertEqual(resp_spam.status_code, 400)
        self.assertIn('Exceeded maximum device limit', resp_spam.json().get('error', ''))

    def test_simulation_ip_validation(self):
        """Verify malformed destination IP is rejected cleanly with HTTP 400."""
        url = reverse('simulation:trace_api')
        payload = {
            'src_dev_id': 'dev-1',
            'dest_ip': 'not-an-ip-address',
            'protocol': 'icmp'
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json().get('drop_reason'), 'INVALID_IP_FORMAT')
        self.assertIn('not a valid IP address', resp.json().get('details', ''))

    # 6. Security Audit Logger Verification
    def test_security_logger_records_event_and_redacts_secrets(self):
        """Verify SecurityLogger persists events and scrubs sensitive credentials."""
        event = SecurityLogger.log_event(
            action='TEST_SECURITY_EVENT',
            module='audit_test',
            user=self.user_alice,
            details={
                'attempted_action': 'port_scan',
                'password': 'ShouldBeRedactedPassword',
                'token': 'ShouldBeRedactedToken',
                'harmless_info': 'safe_value'
            },
            severity='warning'
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.action, 'TEST_SECURITY_EVENT')
        self.assertEqual(event.details['password'], '[REDACTED]')
        self.assertEqual(event.details['token'], '[REDACTED]')
        self.assertEqual(event.details['harmless_info'], 'safe_value')
        
        # Verify saved in SQLite database
        saved_event = AuditEvent.objects.get(id=event.id)
        self.assertEqual(saved_event.user, self.user_alice)

    # 7. Security Headers Middleware Verification
    def test_security_headers_present_on_responses(self):
        """Verify custom middleware injects nosniff, CSP, and Permissions-Policy headers."""
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['X-Content-Type-Options'], 'nosniff')
        self.assertIn('Content-Security-Policy', resp)
        self.assertIn("default-src 'self'", resp['Content-Security-Policy'])
        self.assertIn("frame-ancestors 'none'", resp['Content-Security-Policy'])
        self.assertIn('Permissions-Policy', resp)
