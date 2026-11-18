import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from academy.models import Course, Lesson, QuizQuestion, DeviceGuide, Achievement, UserCourseProgress, UserLearningProfile

class AcademyModelTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            title='Test Networking Course',
            slug='test-networking-course',
            description='Test course description',
            level='beginner',
            category='foundations',
            estimated_hours=3.5,
            icon='fa-network-wired',
            badge_name='Certified Test Engineer',
            order=1
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='Test Lesson 1',
            slug='test-lesson-1',
            lesson_number=1,
            summary='Test lesson summary',
            difficulty='beginner',
            estimated_minutes=20,
            section_a_intro={'definition': 'Test Definition', 'purpose': 'Test Purpose', 'advantages': ['Adv 1'], 'limitations': ['Lim 1']},
            section_b_how_it_works={'architecture': 'Test Architecture', 'protocols': ['IPv4'], 'data_flow': 'L7 to L1', 'osi_layers': 'All'},
            section_c_connection={'required_devices': ['PC', 'Switch'], 'cable_types': ['Cat6'], 'connection_diagram': '[PC] --- [Switch]'},
            section_d_configuration={'device_setup': 'Setup host', 'interface_config': 'Configure ports', 'ip_config': 'Set IP', 'security_settings': 'Secure'},
            section_e_commands=[{'command': 'ipconfig', 'syntax': 'ipconfig', 'purpose': 'Show IP', 'mode': 'CMD', 'expected_output': '192.168.1.10'}],
            has_practical_lab=True,
            lab_topology={
                'devices': [
                    {'id': 'pc1', 'name': 'PC-01', 'type': 'pc_workstation', 'x': 100, 'y': 100, 'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                    {'id': 'rtr1', 'name': 'RTR-01', 'type': 'router', 'x': 300, 'y': 100, 'ip': '192.168.1.1', 'mask': '255.255.255.0'}
                ],
                'links': [
                    {'from': 'pc1', 'from_port': 'eth0', 'to': 'rtr1', 'to_port': 'g0/0', 'cable': 'copper_straight'}
                ]
            },
            lab_tasks=[
                {
                    'task_id': 'task_1',
                    'title': 'Verify PC IP',
                    'instruction': 'Check IP address',
                    'target_device': 'pc1',
                    'expected_config': {'ip': '192.168.1.10'},
                    'hints': ['Hint 1', 'Hint 2', 'Hint 3']
                }
            ],
            lab_solution_state={'ping_tests': [{'from': 'pc1', 'to': '192.168.1.1', 'expect': 'success'}]},
            section_g_troubleshooting=[{'symptom': 'Cannot ping', 'cause': 'Port down', 'diagnosis': 'Check LED', 'fix': 'no shutdown'}],
            order=1
        )
        self.quiz = QuizQuestion.objects.create(
            lesson=self.lesson,
            question_type='mcq',
            question_text='What layer is IP?',
            options=[{'id': 'A', 'text': 'Layer 2'}, {'id': 'B', 'text': 'Layer 3'}],
            correct_answer='B',
            explanation='IP operates at Layer 3 Network.',
            order=1
        )
        self.device = DeviceGuide.objects.create(
            device_type='router',
            name='Enterprise Router',
            slug='enterprise-router',
            category='Routers',
            summary='Test router summary',
            section_1_intro='Intro text',
            section_2_purpose='Purpose text',
            section_3_applications='Applications text',
            section_4_appearance_ports='Appearance text',
            section_5_interfaces='Interfaces text',
            section_6_connection_methods='Connection text',
            section_7_cables='Cables text',
            section_8_power_requirements='Power text',
            section_9_ip_configuration='IP config text',
            section_10_device_settings='Settings text',
            section_11_commands=[{'cmd': 'show ip route'}],
            section_12_command_explanations=[{'cmd': 'show ip route', 'explanation': 'Inspects routes'}],
            section_13_verification='Verification text',
            section_14_common_mistakes=['Mistake 1'],
            section_15_troubleshooting=[{'issue': 'Down', 'fix': 'no shut'}],
            section_16_security_practices=['Disable telnet'],
            section_17_practical_project={'title': 'Project', 'summary': 'Do project'},
            order=1
        )

    def test_course_properties(self):
        self.assertEqual(self.course.lesson_count, 1)
        self.assertTrue(self.course.has_practical_labs)
        self.assertEqual(str(self.course), "Test Networking Course (Beginner)")

    def test_lesson_properties(self):
        self.assertEqual(self.lesson.quizzes.count(), 1)
        self.assertTrue(self.lesson.has_practical_lab)
        self.assertIn('definition', self.lesson.section_a_intro)

    def test_device_guide_17_sections(self):
        self.assertEqual(self.device.name, 'Enterprise Router')
        self.assertTrue(bool(self.device.section_1_intro))
        self.assertTrue(bool(self.device.section_17_practical_project))


class AcademyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(
            title='Intro to Networking',
            slug='intro-to-networking',
            description='Foundation course',
            level='beginner',
            category='foundations',
            order=1
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='OSI Model',
            slug='osi-model',
            lesson_number=1,
            summary='Overview of OSI',
            has_practical_lab=True,
            lab_topology={
                'devices': [
                    {'id': 'pc1', 'name': 'PC-01', 'type': 'pc_workstation', 'x': 100, 'y': 100, 'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                    {'id': 'rtr1', 'name': 'RTR-01', 'type': 'router', 'x': 300, 'y': 100, 'ip': '192.168.1.1', 'mask': '255.255.255.0'}
                ],
                'links': [
                    {'from': 'pc1', 'from_port': 'eth0', 'to': 'rtr1', 'to_port': 'g0/0', 'cable': 'copper_straight'}
                ]
            },
            lab_tasks=[
                {
                    'task_id': 'task_1',
                    'title': 'Verify IP',
                    'instruction': 'Check IP',
                    'target_device': 'pc1',
                    'expected_config': {'ip': '192.168.1.10'},
                    'hints': ['Hint 1', 'Hint 2', 'Hint 3']
                }
            ],
            order=1
        )
        self.device = DeviceGuide.objects.create(
            device_type='layer2_switch',
            name='Access Switch',
            slug='access-switch',
            category='Switches',
            summary='Switch summary',
            section_1_intro='Intro',
            section_2_purpose='Purpose',
            order=1
        )

    def test_dashboard_view(self):
        resp = self.client.get(reverse('academy:dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'RamoNet Academy')
        self.assertContains(resp, 'Intro to Networking')

    def test_course_detail_view(self):
        resp = self.client.get(reverse('academy:course_detail', args=[self.course.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.course.title)
        self.assertContains(resp, self.lesson.title)

    def test_lesson_reader_view(self):
        resp = self.client.get(reverse('academy:lesson_reader', args=[self.course.slug, self.lesson.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.lesson.title)
        self.assertContains(resp, 'SECTION A — INTRODUCTION')
        self.assertContains(resp, 'Launch Practical Lab')

    def test_practical_lab_view(self):
        resp = self.client.get(reverse('academy:practical_lab', args=[self.course.slug, self.lesson.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'lab-topology-svg')
        self.assertContains(resp, 'CLI Terminal')
        self.assertContains(resp, 'Progressive Hints')

    def test_device_guides_catalogue_view(self):
        resp = self.client.get(reverse('academy:device_guides'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Access Switch')

    def test_device_guide_detail_view(self):
        resp = self.client.get(reverse('academy:device_guide_detail', args=[self.device.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.device.name)
        self.assertContains(resp, '17 Standard Sections')

    def test_certificate_view(self):
        resp = self.client.get(reverse('academy:certificate', args=[self.course.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Certificate of Completion')
        self.assertContains(resp, 'RAMONET-')


class AcademyApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.course = Course.objects.create(title='C1', slug='c1', order=1)
        self.lesson = Lesson.objects.create(
            course=self.course,
            title='L1',
            slug='l1',
            has_practical_lab=True,
            lab_topology={
                'devices': [
                    {'id': 'pc1', 'name': 'PC-1', 'type': 'pc_workstation', 'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                    {'id': 'rtr1', 'name': 'RTR-1', 'type': 'router', 'ip': '192.168.1.1', 'mask': '255.255.255.0'}
                ],
                'links': [
                    {'from': 'pc1', 'to': 'rtr1', 'cable': 'copper_straight'}
                ]
            },
            lab_tasks=[
                {
                    'task_id': 'task_1',
                    'title': 'Set IP',
                    'target_device': 'pc1',
                    'expected_config': {'ip': '192.168.1.10'},
                    'hints': ['Check IP', 'Check terminal', 'ipconfig']
                }
            ],
            order=1
        )

    def test_verify_step_api_success(self):
        payload = {
            'lesson_id': self.lesson.id,
            'task_id': 'task_1',
            'target_device': 'pc1',
            'expected_config': {'ip': '192.168.1.10'},
            'test_type': 'config',
            'topology': self.lesson.lab_topology
        }
        resp = self.client.post(
            reverse('academy:api_verify_step'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('passed'))

    def test_verify_step_api_mismatch_detection(self):
        bad_topology = {
            'devices': [
                {'id': 'pc1', 'name': 'PC-1', 'ip': '10.0.0.99'}
            ]
        }
        payload = {
            'lesson_id': self.lesson.id,
            'task_id': 'task_1',
            'target_device': 'pc1',
            'expected_config': {'ip': '192.168.1.10'},
            'test_type': 'config',
            'topology': bad_topology
        }
        resp = self.client.post(
            reverse('academy:api_verify_step'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data.get('passed'))
        self.assertTrue(len(data.get('mistakes', [])) > 0)

    def test_exam_evaluate_api(self):
        payload = {
            'lesson_id': self.lesson.id,
            'topology': {
                'devices': [
                    {'id': 'pc1', 'name': 'PC-1', 'type': 'pc_workstation', 'ip': '192.168.1.10', 'mask': '255.255.255.0', 'gateway': '192.168.1.1'},
                    {'id': 'sw1', 'name': 'SW-1', 'type': 'layer2_switch'},
                    {'id': 'rtr1', 'name': 'RTR-1', 'type': 'router', 'ip': '192.168.1.1', 'mask': '255.255.255.0'}
                ],
                'links': [
                    {'from': 'pc1', 'to': 'sw1', 'cable': 'copper_straight'},
                    {'from': 'sw1', 'to': 'rtr1', 'cable': 'copper_straight'}
                ]
            }
        }
        resp = self.client.post(
            reverse('academy:api_exam_evaluate'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('score', data)
        self.assertIn('grade', data)
        self.assertIn('rubric', data)
        self.assertTrue(data.get('score') >= 75)

    def test_progressive_hint_api(self):
        resp = self.client.get(
            reverse('academy:api_hint'),
            {'lesson_id': self.lesson.id, 'task_id': 'task_1', 'level': 2}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get('hint_level'), 2)
        self.assertEqual(data.get('hint_text'), 'Check terminal')

    def test_sync_progress_api(self):
        user = User.objects.create_user('teststudent', 'test@local.dev', 'pass123')
        self.client.force_login(user)

        resp = self.client.post(
            reverse('academy:api_sync_progress'),
            data=json.dumps({
                'course_slug': self.course.slug,
                'completed_lesson_id': self.lesson.id,
                'score': 100
            }),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get('status'), 'synced')

        prog = UserCourseProgress.objects.filter(user=user, course=self.course).first()
        self.assertIsNotNone(prog)
        self.assertIn(self.lesson.id, prog.completed_lessons)
