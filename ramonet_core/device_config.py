"""
Ramonet Core - Device Configuration Service
The authoritative service responsible for mutating and retrieving device configuration state.
Supports both instance operations (service.set_hostname(...)) and classmethod operations (DeviceConfigurationService.set_hostname(dev, ...)).
"""
from typing import Dict, List, Any, Optional
import ipaddress
from .device_registry import DeviceCapabilityManager, DeviceCapabilities

class DeviceConfigurationService:
    """Authoritative API for inspecting and modifying a single device configuration state."""

    def __init__(self, device_data: Dict[str, Any]):
        self.device = device_data

    @property
    def id(self) -> str:
        return str(self.device.get('id', ''))

    @property
    def name(self) -> str:
        return str(self.device.get('name', 'Device'))

    @property
    def device_type(self) -> str:
        return str(self.device.get('type', 'general')).lower()

    @classmethod
    def _extract_dict(cls, dev_or_self: Any) -> Dict[str, Any]:
        if isinstance(dev_or_self, DeviceConfigurationService):
            return dev_or_self.device
        elif isinstance(dev_or_self, dict):
            return dev_or_self
        raise TypeError(f"Expected DeviceConfigurationService or dict, got {type(dev_or_self)}")

    @classmethod
    def set_hostname(cls, dev_or_self: Any, new_hostname: str) -> None:
        dev = cls._extract_dict(dev_or_self)
        dev['name'] = str(new_hostname).strip()

    @classmethod
    def set_management_ip(cls, dev_or_self: Any, ip: str, mask: str = '255.255.255.0', gateway: str = '') -> None:
        dev = cls._extract_dict(dev_or_self)
        dev['ip'] = str(ip).strip()
        dev['mask'] = str(mask).strip()
        dev['gateway'] = str(gateway).strip()

    @classmethod
    def get_interface(cls, dev_or_self: Any, iface_name: str) -> Optional[Dict[str, Any]]:
        dev = cls._extract_dict(dev_or_self)
        for iface in dev.get('interfaces', []):
            if iface.get('name', '').lower() == iface_name.lower():
                return iface
        return None

    @classmethod
    def ensure_interface(cls, dev_or_self: Any, iface_name: str, iface_type: str = 'copper', speed: int = 1000) -> Dict[str, Any]:
        dev = cls._extract_dict(dev_or_self)
        existing = cls.get_interface(dev, iface_name)
        if existing:
            return existing
        new_iface = {
            'name': iface_name,
            'type': iface_type,
            'speed': speed,
            'status': 'up',
            'ip': '',
            'mask': '255.255.255.0',
            'mode': 'access',
            'vlan': 1
        }
        if 'interfaces' not in dev:
            dev['interfaces'] = []
        dev['interfaces'].append(new_iface)
        return new_iface

    @classmethod
    def set_interface_ip(cls, dev_or_self: Any, iface_name: str, ip: str, mask: str = '255.255.255.0', status: Optional[str] = None) -> bool:
        dev = cls._extract_dict(dev_or_self)
        iface = cls.get_interface(dev, iface_name)
        if not iface:
            iface = cls.ensure_interface(dev, iface_name)
        iface['ip'] = str(ip).strip()
        iface['mask'] = str(mask).strip()
        if status:
            iface['status'] = status
        if not dev.get('ip') or iface_name in ['GigabitEthernet0/0', 'eth0', 'Fa0/1']:
            dev['ip'] = iface['ip']
            dev['mask'] = iface['mask']
        return True

    @classmethod
    def set_interface_status(cls, dev_or_self: Any, iface_name: str, status: str) -> bool:
        dev = cls._extract_dict(dev_or_self)
        iface = cls.get_interface(dev, iface_name)
        if not iface:
            return False
        iface['status'] = 'up' if status.lower() in ['up', 'no shutdown'] else 'down'
        return True

    @classmethod
    def set_port_mode(cls, dev_or_self: Any, iface_name: str, mode: str, vlan: int = 1, allowed_vlans: Optional[List[int]] = None, native_vlan: int = 1) -> bool:
        dev = cls._extract_dict(dev_or_self)
        iface = cls.get_interface(dev, iface_name)
        if not iface:
            iface = cls.ensure_interface(dev, iface_name)

        iface['mode'] = mode.lower()
        if mode.lower() == 'access':
            iface['vlan'] = int(vlan)
            if 'port_vlans' not in dev:
                dev['port_vlans'] = {}
            dev['port_vlans'][iface_name] = int(vlan)
        elif mode.lower() == 'trunk':
            iface['native_vlan'] = int(native_vlan)
            iface['allowed_vlans'] = allowed_vlans or [1, 10, 20, 30, 40, 50, 99]
        return True

    @classmethod
    def set_interface_mode(cls, dev_or_self: Any, iface_name: str, mode: str, vlan: int = 1, allowed_vlans: Optional[List[int]] = None, native_vlan: int = 1) -> bool:
        """Alias for set_port_mode."""
        return cls.set_port_mode(dev_or_self, iface_name, mode, vlan=vlan, allowed_vlans=allowed_vlans, native_vlan=native_vlan)

    @classmethod
    def create_vlan(cls, dev_or_self: Any, vlan_id: int, name: str = '') -> bool:
        dev = cls._extract_dict(dev_or_self)
        v_id = int(vlan_id)
        if 'vlans' not in dev:
            dev['vlans'] = [1]
        
        # Support dict format {'10': {'name': 'Sales'}} or list format [1, 10]
        if isinstance(dev['vlans'], dict):
            dev['vlans'][str(v_id)] = {'name': name or f'VLAN_{v_id}'}
        else:
            if v_id not in dev['vlans']:
                dev['vlans'].append(v_id)
                dev['vlans'].sort()
        return True

    @classmethod
    def add_vlan(cls, dev_or_self: Any, vlan_id: int, name: str = '') -> bool:
        """Alias for create_vlan."""
        return cls.create_vlan(dev_or_self, vlan_id, name)

    @classmethod
    def add_static_route(cls, dev_or_self: Any, dest_net: str, mask: str, next_hop: str, exit_iface: str = '') -> bool:
        dev = cls._extract_dict(dev_or_self)
        if 'routing' not in dev:
            dev['routing'] = {'enabled': True, 'static_routes': []}
        routes = dev['routing'].setdefault('static_routes', [])
        for r in routes:
            if r.get('network') == dest_net and r.get('mask') == mask:
                r['next_hop'] = next_hop
                r['interface'] = exit_iface
                return True
        routes.append({
            'network': dest_net,
            'mask': mask,
            'next_hop': next_hop,
            'interface': exit_iface
        })
        return True

    @classmethod
    def generate_running_config(cls, dev_or_self: Any) -> str:
        dev = cls._extract_dict(dev_or_self)
        name = dev.get('name', 'Device')
        lines = [
            f"! Running configuration for {name}",
            f"hostname {name}",
            "!"
        ]

        # VLANs
        vlans = dev.get('vlans', [])
        if isinstance(vlans, dict):
            for v_str, v_info in vlans.items():
                if str(v_str) != '1':
                    lines.append(f"vlan {v_str}")
                    lines.append(f" name {v_info.get('name', f'VLAN_{v_str}')}")
                    lines.append("!")
        elif isinstance(vlans, list):
            for v in vlans:
                if v > 1:
                    lines.append(f"vlan {v}")
                    lines.append(f" name VLAN_{v}")
                    lines.append("!")

        # Interfaces
        for iface in dev.get('interfaces', []):
            lines.append(f"interface {iface.get('name')}")
            if iface.get('ip'):
                lines.append(f" ip address {iface.get('ip')} {iface.get('mask', '255.255.255.0')}")
            if iface.get('mode') == 'access':
                lines.append(" switchport mode access")
                lines.append(f" switchport access vlan {iface.get('vlan', 1)}")
            elif iface.get('mode') == 'trunk':
                lines.append(" switchport mode trunk")
                if iface.get('native_vlan'):
                    lines.append(f" switchport trunk native vlan {iface.get('native_vlan')}")
            if iface.get('status') == 'down':
                lines.append(" shutdown")
            else:
                lines.append(" no shutdown")
            lines.append("!")

        # Static Routes
        routes = dev.get('routing', {}).get('static_routes', [])
        for r in routes:
            lines.append(f"ip route {r.get('network')} {r.get('mask')} {r.get('next_hop')}")

        lines.append("end")
        return "\n".join(lines)
