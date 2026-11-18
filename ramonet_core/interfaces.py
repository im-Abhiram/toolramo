"""
Ramonet Core - Interfaces & Connection Manager
Validates physical links, cable types, port compatibility, and patch panel mappings.
"""
from typing import Dict, List, Any, Optional, Tuple

class ConnectionManager:
    """Validates cable compatibility and tracks physical connections."""

    CABLE_COMPATIBILITY = {
        'copper_straight': ['copper', 'rj45', '1000base-t', '100base-tx', '10gbase-t'],
        'copper_crossover': ['copper', 'rj45', '1000base-t', '100base-tx'],
        'fiber': ['fiber', 'sfp', 'sfp+', 'optical', '1000base-sx', '10gbase-sr'],
        'serial': ['serial', 'v.35', 'smart-serial'],
        'wireless': ['wireless', '802.11', 'wifi']
    }

    @classmethod
    def validate_cable_compatibility(cls, cable_type: str, port_type_a: str, port_type_b: str) -> Tuple[bool, str]:
        allowed = cls.CABLE_COMPATIBILITY.get(cable_type.lower(), ['copper'])
        a_ok = any(opt in port_type_a.lower() for opt in allowed)
        b_ok = any(opt in port_type_b.lower() for opt in allowed)

        if not a_ok:
            return False, f"Cable {cable_type} is incompatible with port type {port_type_a}"
        if not b_ok:
            return False, f"Cable {cable_type} is incompatible with port type {port_type_b}"
        return True, "Cable compatible"

    @classmethod
    def find_connected_peer(cls, connections: List[Dict[str, Any]], dev_id: str, port_name: str) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        for conn in connections:
            if conn.get('status', 'connected') != 'connected':
                continue
            src_d = str(conn.get('source_device', conn.get('from', '')))
            src_p = str(conn.get('source_port', conn.get('from_port', ''))).lower()
            dst_d = str(conn.get('target_device', conn.get('to', '')))
            dst_p = str(conn.get('target_port', conn.get('to_port', ''))).lower()

            target_p = port_name.lower()
            if src_d == str(dev_id) and src_p == target_p:
                return dst_d, conn.get('target_port', conn.get('to_port', '')), conn
            if dst_d == str(dev_id) and dst_p == target_p:
                return src_d, conn.get('source_port', conn.get('from_port', '')), conn
        return None


class InterfaceManager:
    """Manages interface properties, PoE budgeting, and port statistics."""

    @classmethod
    def calculate_poe_usage(cls, switch_dev: Dict[str, Any], connected_devices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates consumed PoE wattage against switch PoE budget."""
        budget = float(switch_dev.get('poe_budget_watts', 0.0))
        consumed = 0.0
        ports_powered = []

        for dev in connected_devices:
            # Check if dev consumes PoE (like IP camera, AP)
            power_draw = float(dev.get('power_watts', 0.0))
            if dev.get('type') in ['ip_camera', 'wireless_ap', 'voip_phone'] or dev.get('poe_pd'):
                consumed += power_draw
                ports_powered.append({
                    'device_id': dev.get('id'),
                    'device_name': dev.get('name'),
                    'watts': power_draw
                })

        remaining = max(0.0, budget - consumed)
        over_budget = consumed > budget if budget > 0 else False

        return {
            'budget_watts': budget,
            'consumed_watts': consumed,
            'remaining_watts': remaining,
            'is_over_budget': over_budget,
            'powered_devices': ports_powered
        }

    @classmethod
    def calculate_poe_power(cls, switch_dev: Dict[str, Any], connected_devices: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Calculates PoE consumption and available headroom margin."""
        budget = float(switch_dev.get('power_budget_watts', switch_dev.get('poe_budget_watts', 370.0)))
        total_drawn = 0.0

        for iface in switch_dev.get('interfaces', []):
            total_drawn += float(iface.get('poe_draw_watts', 0.0))

        if connected_devices:
            for dev in connected_devices:
                if dev.get('poe_pd') or dev.get('type') in ['ip_camera', 'wireless_ap']:
                    total_drawn += float(dev.get('power_watts', 0.0))

        margin = max(0.0, budget - total_drawn)
        return {
            'total_drawn_watts': total_drawn,
            'available_margin_watts': margin,
            'is_overloaded': total_drawn > budget if budget > 0 else False,
            'budget_watts': budget
        }
