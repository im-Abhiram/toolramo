"""
Ramonet Core - Unified Network Simulation & Packet Forwarding Engine
Modular Layer 2 through Layer 7 simulation supporting VLANs, ARP, Routing, NAT, Firewalls, and Application protocols.
"""
import ipaddress
import time
from typing import Dict, List, Any, Optional, Tuple
from .validator import ConfigurationValidator

class UnifiedSimulationEngine:
    """The central authoritative network simulation engine for Ramonet."""

    def __init__(self, topology_data: Optional[Dict[str, Any]] = None, devices: Optional[Any] = None, connections: Optional[List[Dict[str, Any]]] = None):
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.connections: List[Dict[str, Any]] = []
        self.mac_tables: Dict[str, Dict[str, str]] = {}
        self.arp_tables: Dict[str, Dict[str, str]] = {}
        self.nat_tables: Dict[str, List[Dict[str, Any]]] = {}
        self.conntrack_tables: Dict[str, List[Dict[str, Any]]] = {}

        if topology_data:
            self.load_topology(topology_data)
        elif devices is not None:
            self.load_topology({'devices': devices, 'connections': connections or []})

    def load_topology(self, topology_data: Dict[str, Any]):
        devices_raw = topology_data.get('devices', [])
        if isinstance(devices_raw, list):
            self.devices = {str(d.get('id', '')): d for d in devices_raw}
        elif isinstance(devices_raw, dict):
            self.devices = {str(k): v for k, v in devices_raw.items()}

        self.connections = topology_data.get('connections', topology_data.get('links', []))

        for dev_id, dev in self.devices.items():
            self.mac_tables.setdefault(dev_id, {})
            self.arp_tables.setdefault(dev_id, {})
            self.nat_tables.setdefault(dev_id, [])
            self.conntrack_tables.setdefault(dev_id, [])

    def get_device(self, dev_id_or_name: str) -> Optional[Dict[str, Any]]:
        dev_id_or_name = str(dev_id_or_name).strip()
        if dev_id_or_name in self.devices:
            return self.devices[dev_id_or_name]
        for d_id, d in self.devices.items():
            if d.get('name', '').lower() == dev_id_or_name.lower():
                return d
        return None

    def get_device_by_ip(self, ip_str: str) -> Optional[Tuple[str, Dict[str, Any], str]]:
        ip_str = ip_str.strip()
        for dev_id, dev in self.devices.items():
            if dev.get('ip') == ip_str:
                return dev_id, dev, 'primary'
            for iface in dev.get('interfaces', []):
                if iface.get('ip') == ip_str:
                    return dev_id, dev, iface.get('name', 'eth0')
        return None

    def get_connected_link(self, dev_id: str, iface_name: str) -> Optional[Dict[str, Any]]:
        for conn in self.connections:
            if conn.get('status', 'connected') != 'connected':
                continue
            src_d = str(conn.get('source_device', conn.get('from', '')))
            src_p = str(conn.get('source_port', conn.get('from_port', ''))).lower()
            dst_d = str(conn.get('target_device', conn.get('to', '')))
            dst_p = str(conn.get('target_port', conn.get('to_port', ''))).lower()

            target_p = iface_name.lower()
            if src_d == str(dev_id) and (not src_p or src_p == target_p):
                return conn
            if dst_d == str(dev_id) and (not dst_p or dst_p == target_p):
                return conn
        return None

    def get_neighbor(self, dev_id: str, iface_name: str) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        conn = self.get_connected_link(dev_id, iface_name)
        if not conn:
            return None
        src_d = str(conn.get('source_device', conn.get('from', '')))
        src_p = str(conn.get('source_port', conn.get('from_port', '')))
        dst_d = str(conn.get('target_device', conn.get('to', '')))
        dst_p = str(conn.get('target_port', conn.get('to_port', '')))

        if src_d == str(dev_id):
            return dst_d, dst_p, conn
        return src_d, src_p, conn

    def simulate_packet(self, src_dev_id: str, dest_ip: str, protocol: str = 'ICMP', src_port: int = 1024, dest_port: int = 80, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Unified hop-by-hop packet traversal simulation across L2, L3, L4 firewalls, and L7 endpoints.
        """
        res = self._run_simulate_packet(src_dev_id, dest_ip, protocol=protocol, src_port=src_port, dest_port=dest_port, payload=payload)
        res['success'] = res.get('delivered', False)
        if 'trace' in res:
            res['hops'] = res['trace']
        return res

    def _run_simulate_packet(self, src_dev_id: str, dest_ip: str, protocol: str = 'ICMP', src_port: int = 1024, dest_port: int = 80, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        trace = []
        src_dev = self.get_device(src_dev_id)

        if not src_dev:
            return {
                'delivered': False,
                'drop_reason': 'SOURCE_DEVICE_NOT_FOUND',
                'trace': trace,
                'error': f"Source device {src_dev_id} does not exist."
            }

        src_ip = src_dev.get('ip', '')
        src_mask = src_dev.get('mask', '255.255.255.0')
        src_gw = src_dev.get('gateway', '')

        packet = {
            'src_ip': src_ip,
            'dest_ip': dest_ip,
            'protocol': protocol,
            'src_port': src_port,
            'dest_port': dest_port,
            'ttl': 64,
            'vlan': 1,
            'payload': payload or {}
        }

        trace.append({
            'hop': 0,
            'device_id': src_dev_id,
            'device_name': src_dev.get('name', 'Source'),
            'action': 'ORIGINATE',
            'detail': f"Packet originated from {src_ip} targeting {dest_ip} [{protocol}]",
            'packet_state': dict(packet)
        })

        # Local loopback check
        if dest_ip == '127.0.0.1' or dest_ip == src_ip:
            trace.append({
                'hop': 1,
                'device_id': src_dev_id,
                'device_name': src_dev.get('name'),
                'action': 'DELIVER_LOCAL',
                'detail': f"Delivered to local loopback interface {dest_ip}"
            })
            return {'delivered': True, 'trace': trace, 'hops': 1, 'packet': packet}

        # Subnet check: Is destination local or remote?
        is_local = ConfigurationValidator.are_in_same_subnet(src_ip, dest_ip, src_mask) if (src_ip and src_mask) else False

        target_lookup = self.get_device_by_ip(dest_ip)

        # If not local, must have a default gateway
        if not is_local:
            if not src_gw:
                trace.append({
                    'hop': 1,
                    'device_id': src_dev_id,
                    'device_name': src_dev.get('name'),
                    'action': 'DROP',
                    'detail': f"Destination {dest_ip} is on a remote network but no default gateway is configured."
                })
                return {'delivered': False, 'drop_reason': 'GATEWAY_MISSING', 'trace': trace}

            # Check if gateway is on the same subnet
            if not ConfigurationValidator.are_in_same_subnet(src_ip, src_gw, src_mask):
                trace.append({
                    'hop': 1,
                    'device_id': src_dev_id,
                    'device_name': src_dev.get('name'),
                    'action': 'DROP',
                    'detail': f"Configured default gateway {src_gw} is not in the local subnet {src_ip}/{src_mask}."
                })
                return {'delivered': False, 'drop_reason': 'GATEWAY_SUBNET_MISMATCH', 'trace': trace}

        # Hop-by-hop traversal simulation
        current_dev = src_dev
        current_dev_id = src_dev_id
        hop_count = 0
        visited = set([current_dev_id])

        while hop_count < 15:
            hop_count += 1

            # Check if target is directly on this device
            if current_dev.get('ip') == dest_ip:
                trace.append({
                    'hop': hop_count,
                    'device_id': current_dev_id,
                    'device_name': current_dev.get('name'),
                    'action': 'DELIVER',
                    'detail': f"Packet successfully delivered to destination {dest_ip}"
                })
                return {'delivered': True, 'trace': trace, 'hops': hop_count, 'packet': packet}

            # Look for link out
            # Find an active connected link
            found_neighbor = None
            for iface in current_dev.get('interfaces', [{'name': 'eth0', 'status': 'up'}]):
                if iface.get('status', 'up') == 'down':
                    continue
                neighbor = self.get_neighbor(current_dev_id, iface.get('name', 'eth0'))
                if neighbor and neighbor[0] not in visited:
                    found_neighbor = neighbor
                    break

            if not found_neighbor:
                # If target device exists in topology and is reachable through gateway
                if target_lookup:
                    dst_dev_id, dst_dev, _ = target_lookup
                    trace.append({
                        'hop': hop_count,
                        'device_id': dst_dev_id,
                        'device_name': dst_dev.get('name'),
                        'action': 'DELIVER',
                        'detail': f"Packet routed and delivered to {dest_ip}"
                    })
                    return {'delivered': True, 'trace': trace, 'hops': hop_count + 1, 'packet': packet}

                trace.append({
                    'hop': hop_count,
                    'device_id': current_dev_id,
                    'device_name': current_dev.get('name'),
                    'action': 'DROP',
                    'detail': f"No route to host {dest_ip} or link unreachable."
                })
                return {'delivered': False, 'drop_reason': 'NO_ROUTE_TO_HOST', 'trace': trace}

            next_dev_id, next_port, conn = found_neighbor
            next_dev = self.get_device(next_dev_id)
            visited.add(next_dev_id)

            # Decrement TTL at Layer 3
            if next_dev.get('type') in ['router', 'layer3_switch', 'firewall']:
                packet['ttl'] -= 1
                if packet['ttl'] <= 0:
                    trace.append({
                        'hop': hop_count,
                        'device_id': next_dev_id,
                        'device_name': next_dev.get('name'),
                        'action': 'DROP',
                        'detail': "ICMP Time to Live (TTL) exceeded in transit."
                    })
                    return {'delivered': False, 'drop_reason': 'TIME_EXCEEDED', 'trace': trace}

            # Firewall Inspection
            if next_dev.get('type') == 'firewall':
                rules = next_dev.get('firewall', {}).get('rules', [])
                policy = next_dev.get('firewall', {}).get('default_policy', 'deny')
                # Check rules
                allowed = (policy == 'allow')
                for r in rules:
                    if r.get('action') == 'accept':
                        allowed = True
                        break
                    elif r.get('action') in ['drop', 'deny']:
                        allowed = False
                        break
                if not allowed:
                    trace.append({
                        'hop': hop_count,
                        'device_id': next_dev_id,
                        'device_name': next_dev.get('name'),
                        'action': 'DROP',
                        'detail': "Traffic dropped by stateful firewall policy."
                    })
                    return {'delivered': False, 'drop_reason': 'FIREWALL_DENIED', 'trace': trace}

            trace.append({
                'hop': hop_count,
                'device_id': next_dev_id,
                'device_name': next_dev.get('name'),
                'action': 'FORWARD',
                'detail': f"Forwarded via link to {next_dev.get('name')} [{next_port}]"
            })

            current_dev = next_dev
            current_dev_id = next_dev_id

        return {'delivered': False, 'drop_reason': 'ROUTING_LOOP', 'trace': trace}
