"""
Ramonet Core - Unified Topology Engine
Coordinates the logical topology, IPAM, Physical Racks, CCTV Planner, and Documentation state.
"""
from typing import Dict, List, Any, Optional
import json
from .device_registry import DeviceRegistry
from .device_config import DeviceConfigurationService
from .validator import ConfigurationValidator
from .simulation import UnifiedSimulationEngine

class TopologyEngine:
    """The central project topology and state manager."""

    def __init__(self, project_id: Optional[str] = None, name: str = 'Default Project'):
        self.project_id = project_id or 'proj_default'
        self.name = name
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.connections: List[Dict[str, Any]] = []
        self.racks: Dict[str, Dict[str, Any]] = {}
        self.ipam_subnets: List[Dict[str, Any]] = [
            {'cidr': '192.168.1.0/24', 'name': 'LAN Management', 'vlan': 1, 'gateway': '192.168.1.1'},
            {'cidr': '192.168.10.0/24', 'name': 'Sales Department', 'vlan': 10, 'gateway': '192.168.10.1'},
            {'cidr': '192.168.20.0/24', 'name': 'Engineering Department', 'vlan': 20, 'gateway': '192.168.20.1'},
            {'cidr': '192.168.50.0/24', 'name': 'CCTV Surveillance', 'vlan': 50, 'gateway': '192.168.50.1'}
        ]

    def add_device(self, dev_id: str, name: str, device_type: str, x: int = 150, y: int = 150) -> Dict[str, Any]:
        dev = DeviceRegistry.create_default_device(dev_id, name, device_type, x, y)
        self.devices[dev_id] = dev
        return dev

    def remove_device(self, dev_id: str) -> bool:
        if dev_id in self.devices:
            del self.devices[dev_id]
            # Remove associated connections
            self.connections = [
                c for c in self.connections
                if str(c.get('source_device', c.get('from'))) != str(dev_id)
                and str(c.get('target_device', c.get('to'))) != str(dev_id)
            ]
            return True
        return False

    def connect(self, dev_a_id: str, port_a: str, dev_b_id: str, port_b: str, cable: str = 'copper_straight') -> Dict[str, Any]:
        conn = {
            'id': f"conn_{dev_a_id}_{port_a}_{dev_b_id}_{port_b}",
            'source_device': str(dev_a_id),
            'source_port': str(port_a),
            'target_device': str(dev_b_id),
            'target_port': str(port_b),
            'from': str(dev_a_id),
            'from_port': str(port_a),
            'to': str(dev_b_id),
            'to_port': str(port_b),
            'cable': cable,
            'status': 'connected'
        }
        self.connections.append(conn)
        return conn

    def get_cctv_plan(self) -> Dict[str, Any]:
        """Calculates aggregate CCTV bandwidth, PoE power consumption, and storage requirements."""
        cameras = [d for d in self.devices.values() if d.get('type') == 'ip_camera']
        nvrs = [d for d in self.devices.values() if d.get('type') == 'nvr_recorder']
        poe_switches = [d for d in self.devices.values() if d.get('type') in ['poe_switch', 'layer2_switch']]

        total_bandwidth_mbps = 0.0
        total_poe_watts = 0.0
        camera_items = []

        for cam in cameras:
            cctv_cfg = cam.get('services', {}).get('cctv', {})
            bitrate_kbps = cctv_cfg.get('bitrate_kbps', 4096)
            bw_mbps = bitrate_kbps / 1000.0
            poe_w = float(cam.get('power_watts', 12.0))

            total_bandwidth_mbps += bw_mbps
            total_poe_watts += poe_w

            camera_items.append({
                'id': cam.get('id'),
                'name': cam.get('name'),
                'ip': cam.get('ip', 'Unassigned'),
                'resolution': cctv_cfg.get('resolution', '1080p'),
                'fps': cctv_cfg.get('fps', 30),
                'codec': cctv_cfg.get('codec', 'H.265'),
                'bandwidth_mbps': bw_mbps,
                'poe_watts': poe_w
            })

        # Calculate retention storage: (bandwidth Mbps * 3600 * 24 * days) / (8 * 1024 * 1024) TB
        retention_days = 30
        if nvrs:
            retention_days = nvrs[0].get('services', {}).get('nvr', {}).get('retention_days', 30)

        daily_gb = (total_bandwidth_mbps * 3600 * 24) / (8 * 1024)
        total_storage_tb = (daily_gb * retention_days) / 1024.0

        # Check total switch PoE capacity
        available_poe_budget = sum(float(sw.get('poe_budget_watts', 0.0)) for sw in poe_switches)
        poe_exceeded = total_poe_watts > available_poe_budget if available_poe_budget > 0 else False

        return {
            'camera_count': len(cameras),
            'nvr_count': len(nvrs),
            'cameras': camera_items,
            'total_bandwidth_mbps': round(total_bandwidth_mbps, 2),
            'total_poe_watts': round(total_poe_watts, 1),
            'available_poe_budget_watts': available_poe_budget,
            'is_poe_exceeded': poe_exceeded,
            'retention_days': retention_days,
            'required_storage_tb': round(total_storage_tb, 2)
        }

    def get_ipam_records(self) -> List[Dict[str, Any]]:
        """Maps devices to IPAM records and detects conflicts."""
        records = []
        for dev in self.devices.values():
            ip = dev.get('ip')
            if ip:
                records.append({
                    'device_id': dev.get('id'),
                    'device_name': dev.get('name'),
                    'device_type': dev.get('type'),
                    'ip': ip,
                    'mask': dev.get('mask', '255.255.255.0'),
                    'gateway': dev.get('gateway', ''),
                    'status': 'Allocated Static'
                })
        return records

    def export_data(self) -> Dict[str, Any]:
        return {
            'project_id': self.project_id,
            'name': self.name,
            'devices': list(self.devices.values()),
            'connections': self.connections,
            'racks': self.racks,
            'ipam_subnets': self.ipam_subnets
        }

    def import_data(self, data: Dict[str, Any]) -> None:
        self.project_id = data.get('project_id', self.project_id)
        self.name = data.get('name', self.name)
        devices_list = data.get('devices', [])
        self.devices = {str(d.get('id')): d for d in devices_list}
        self.connections = data.get('connections', data.get('links', []))
        self.racks = data.get('racks', {})
        self.ipam_subnets = data.get('ipam_subnets', self.ipam_subnets)
