from django.test import TestCase
from devices.models import DeviceCategory, DeviceDefinition

class DeviceModelTests(TestCase):
    def setUp(self):
        self.category = DeviceCategory.objects.create(name='Test Category', slug='test_cat')
        self.device = DeviceDefinition.objects.create(
            name='Test Switch',
            category=self.category,
            model_name='TS-1000',
            device_type='switch',
            description='Test Switch Description',
            available_interfaces=[{'name': 'eth0', 'type': 'copper', 'speed': 1000}],
            supported_protocols=['IPv4', '802.1Q']
        )

    def test_device_creation(self):
        self.assertEqual(self.device.name, 'Test Switch')
        self.assertEqual(self.device.category.slug, 'test_cat')

    def test_palette_json_serialization(self):
        json_str = self.device.to_palette_json()
        self.assertIn('TS-1000', json_str)
        self.assertIn('eth0', json_str)
