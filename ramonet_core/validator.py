"""
Ramonet Core - Configuration Validator
Validates device configurations, subnetting rules, duplicate IPs, VLAN consistency,
and physical rack unit allocations.
"""
from typing import Dict, List, Any, Tuple
import ipaddress

class ConfigurationValidator:
    """Authoritative validation engine for Ramonet networks."""

    @classmethod
    def validate_ip_address(cls, ip_str: str) -> bool:
        try:
            ipaddress.IPv4Address(ip_str.strip())
            return True
        except (ValueError, AttributeError):
            return False

    @classmethod
    def validate_ipv4(cls, ip_str: str) -> bool:
        """Alias for validate_ip_address."""
        return cls.validate_ip_address(ip_str)

    @classmethod
    def validate_subnet_mask(cls, mask_str: str) -> bool:
        try:
            ipaddress.IPv4Network(f"0.0.0.0/{mask_str.strip()}", strict=False)
            return True
        except (ValueError, AttributeError):
            return False

    @classmethod
    def are_in_same_subnet(cls, ip1: str, ip2: str, mask: str) -> bool:
        try:
            net1 = ipaddress.IPv4Network(f"{ip1}/{mask}", strict=False)
            net2 = ipaddress.IPv4Network(f"{ip2}/{mask}", strict=False)
            return net1 == net2
        except Exception:
            return False

    @classmethod
    def is_same_subnet(cls, ip1: str, ip2: str, mask: str) -> bool:
        """Alias for are_in_same_subnet."""
        return cls.are_in_same_subnet(ip1, ip2, mask)

    @classmethod
    def check_duplicate_ips(cls, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Finds any IP address conflicts across all devices in a topology."""
        seen_ips: Dict[str, str] = {}
        duplicates: List[Dict[str, Any]] = []

        for d in devices:
            dev_id = str(d.get('id', ''))
            dev_name = d.get('name', 'Device')
            
            # Primary/management IP
            primary_ip = d.get('ip', '').strip()
            if primary_ip and cls.validate_ip_address(primary_ip):
                if primary_ip in seen_ips:
                    duplicates.append({
                        'ip': primary_ip,
                        'device1': seen_ips[primary_ip],
                        'device2': dev_name
                    })
                else:
                    seen_ips[primary_ip] = dev_name

            # Interface-level IPs
            for iface in d.get('interfaces', []):
                if_ip = iface.get('ip', '').strip()
                if if_ip and cls.validate_ip_address(if_ip):
                    if if_ip in seen_ips and seen_ips[if_ip] != dev_name:
                        duplicates.append({
                            'ip': if_ip,
                            'device1': seen_ips[if_ip],
                            'device2': f"{dev_name} ({iface.get('name')})"
                        })
                    else:
                        seen_ips[if_ip] = f"{dev_name} ({iface.get('name')})"

        return duplicates

    @classmethod
    def validate_device_gateways(cls, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verifies that each device's default gateway is on the same subnet as its interface IP."""
        issues: List[Dict[str, Any]] = []
        for d in devices:
            ip = d.get('ip', '').strip()
            gw = d.get('gateway', '').strip()
            mask = d.get('subnet_mask') or d.get('mask') or '255.255.255.0'

            if ip and gw and cls.validate_ip_address(ip) and cls.validate_ip_address(gw):
                if not cls.are_in_same_subnet(ip, gw, mask):
                    issues.append({
                        'device_id': d.get('id'),
                        'device_name': d.get('name'),
                        'ip': ip,
                        'gateway': gw,
                        'mask': mask,
                        'error': f"Default gateway {gw} is not in the same subnet as {ip}/{mask}."
                    })
        return issues

    @classmethod
    def validate_rack_unit_overlap(cls, units: List[Dict[str, Any]], max_u: int = 42) -> Dict[str, Any]:
        """Validates a list of rack-mounted equipment units for boundary and overlap errors."""
        occupied: Dict[int, str] = {}
        errors: List[str] = []

        for idx, item in enumerate(units):
            start = item.get('start_u') or item.get('unit_start') or 1
            size = item.get('size_u') or item.get('height_u') or item.get('rack_units') or 1
            name = item.get('device_name') or item.get('name') or f"Device_{idx+1}"

            if start < 1 or (start + size - 1) > max_u:
                errors.append(f"{name} (U{start}-U{start+size-1}) exceeds rack boundary (1-{max_u}U).")
                continue

            for u in range(start, start + size):
                if u in occupied:
                    errors.append(f"Rack unit U{u} collides between {occupied[u]} and {name}.")
                else:
                    occupied[u] = name

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'occupied_units': sorted(occupied.keys()),
            'occupied_count': len(occupied)
        }

    @classmethod
    def validate_rack_placements(cls, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detects physical rack unit overlaps across devices."""
        rack_occupancy: Dict[str, Dict[int, str]] = {}
        overlaps: List[Dict[str, Any]] = []

        for d in devices:
            placement = d.get('rack_placement', {})
            rack_id = placement.get('rack_id') or d.get('rack_id', 'rack_a')
            u_start = placement.get('unit_start') if placement.get('unit_start') is not None else d.get('start_u')
            u_height = placement.get('height_u') or d.get('size_u') or d.get('rack_units', 1)

            if rack_id and u_start is not None:
                rack_occupancy.setdefault(rack_id, {})
                for u in range(u_start, u_start + u_height):
                    if u in rack_occupancy[rack_id]:
                        overlaps.append({
                            'rack_id': rack_id,
                            'unit': u,
                            'device_1': rack_occupancy[rack_id][u],
                            'device_2': d.get('name') or d.get('device_name', 'Device'),
                            'message': f"Rack unit U{u} overlap between {rack_occupancy[rack_id][u]} and {d.get('name') or d.get('device_name')}."
                        })
                    else:
                        rack_occupancy[rack_id][u] = d.get('name') or d.get('device_name', 'Device')

        return overlaps
