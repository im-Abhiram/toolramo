"""
Ramonet Network Simulation Engine
A modular Python-based simulation engine for Layer 2 through Layer 7 networking.
Operates without Docker or physical networking hardware.
"""
import ipaddress
import time
from typing import Dict, List, Any, Optional, Tuple

class NetworkSimulationEngine:
    def __init__(self, topology_data: Optional[Dict[str, Any]] = None):
        """
        Initialize simulation engine with a topology dict containing:
        - devices: list or dict of device objects
        - connections: list of link objects
        """
        self.devices: Dict[str, Dict[str, Any]] = {}
        self.connections: List[Dict[str, Any]] = []
        self.mac_tables: Dict[str, Dict[str, str]] = {}  # device_id -> {mac: interface_name}
        self.arp_tables: Dict[str, Dict[str, str]] = {}  # device_id -> {ip: mac}
        self.nat_tables: Dict[str, List[Dict[str, Any]]] = {} # device_id -> list of translations
        self.conntrack_tables: Dict[str, List[Dict[str, Any]]] = {} # firewall connection tracking
        
        if topology_data:
            self.load_topology(topology_data)

    def load_topology(self, topology_data: Dict[str, Any]):
        devices_raw = topology_data.get('devices', [])
        if isinstance(devices_raw, list):
            for d in devices_raw:
                dev_id = str(d.get('id') or d.get('name') or '')
                self.devices[dev_id] = d
        elif isinstance(devices_raw, dict):
            self.devices = {str(k): v for k, v in devices_raw.items()}

        # Normalize devices: interfaces, IDs, categories
        for dev_id, dev in list(self.devices.items()):
            if 'id' not in dev:
                dev['id'] = dev_id
            if 'category' not in dev and 'type' in dev:
                dev['category'] = dev['type']
            elif 'type' not in dev and 'category' in dev:
                dev['type'] = dev['category']

            raw_ifaces = dev.get('interfaces')
            normalized_ifaces = []
            if raw_ifaces is None:
                # Default interfaces based on device type
                dtype = (dev.get('type') or dev.get('category') or '').lower()
                if 'switch' in dtype:
                    normalized_ifaces = [{'name': f'Fa0/{i}', 'status': 'up'} for i in range(1, 25)] + [{'name': 'Gi0/1', 'status': 'up'}, {'name': 'Gi0/2', 'status': 'up'}]
                elif 'router' in dtype:
                    normalized_ifaces = [
                        {'name': 'g0/0', 'status': 'up', 'ip': dev.get('ip', ''), 'mask': dev.get('mask') or dev.get('subnet_mask', '255.255.255.0')},
                        {'name': 'g0/1', 'status': 'up'},
                        {'name': 'g0/2', 'status': 'up'}
                    ]
                else:
                    normalized_ifaces = [{'name': 'eth0', 'status': 'up', 'ip': dev.get('ip', ''), 'mask': dev.get('mask') or dev.get('subnet_mask', '255.255.255.0')}]
            elif isinstance(raw_ifaces, list):
                for ifc in raw_ifaces:
                    if isinstance(ifc, str):
                        normalized_ifaces.append({'name': ifc, 'status': 'up', 'ip': dev.get('ip', '') if ifc in ('g0/0', 'eth0', 'Fa0/1') else '', 'mask': dev.get('mask', '255.255.255.0')})
                    elif isinstance(ifc, dict):
                        d = dict(ifc)
                        d.setdefault('status', 'up')
                        d.setdefault('name', 'eth0')
                        normalized_ifaces.append(d)
            elif isinstance(raw_ifaces, dict):
                for ifc_name, ifc_data in raw_ifaces.items():
                    if isinstance(ifc_data, dict):
                        d = dict(ifc_data)
                        d.setdefault('name', ifc_name)
                        d.setdefault('status', 'up')
                        normalized_ifaces.append(d)
                    else:
                        normalized_ifaces.append({'name': ifc_name, 'status': 'up'})
            dev['interfaces'] = normalized_ifaces

        # Normalize connections: support both links & connections, from/to and source_device/target_device
        conns_raw = topology_data.get('connections') or topology_data.get('links') or []
        self.connections = []
        for c in conns_raw:
            if not isinstance(c, dict):
                continue
            src_dev = str(c.get('source_device') or c.get('source') or c.get('from') or c.get('from_device') or '')
            tgt_dev = str(c.get('target_device') or c.get('target') or c.get('to') or c.get('to_device') or '')
            src_port = str(c.get('source_port') or c.get('from_port') or c.get('sourcePort') or '')
            tgt_port = str(c.get('target_port') or c.get('to_port') or c.get('targetPort') or '')
            status = c.get('status', 'connected')
            cable_type = c.get('type') or c.get('cable') or c.get('cable_type') or 'copper_straight'
            self.connections.append({
                'source_device': src_dev,
                'target_device': tgt_dev,
                'source_port': src_port,
                'target_port': tgt_port,
                'from': src_dev,
                'to': tgt_dev,
                'from_port': src_port,
                'to_port': tgt_port,
                'status': status,
                'type': cable_type,
                'cable': cable_type
            })
        
        # Initialize device state tables
        for dev_id, dev in self.devices.items():
            if dev_id not in self.mac_tables:
                self.mac_tables[dev_id] = {}
            if dev_id not in self.arp_tables:
                self.arp_tables[dev_id] = {}
            if dev_id not in self.nat_tables:
                self.nat_tables[dev_id] = []
            if dev_id not in self.conntrack_tables:
                self.conntrack_tables[dev_id] = []

    def get_device_by_ip(self, ip_str: str) -> Optional[Tuple[str, Dict[str, Any], str]]:
        """
        Find device and interface matching the given IP address.
        Returns: (device_id, device, interface_name)
        """
        ip_str = ip_str.strip()
        for dev_id, dev in self.devices.items():
            # Check management or primary IP
            if dev.get('ip') == ip_str:
                return dev_id, dev, 'primary'
            
            # Check interfaces
            interfaces = dev.get('interfaces', [])
            for iface in interfaces:
                if isinstance(iface, dict) and iface.get('ip') == ip_str:
                    return dev_id, dev, iface.get('name', 'eth0')
                elif isinstance(iface, str) and iface == ip_str:
                    return dev_id, dev, iface
        return None

    def get_device(self, dev_id_or_name: str) -> Optional[Dict[str, Any]]:
        dev_id_or_name = str(dev_id_or_name).strip()
        if dev_id_or_name in self.devices:
            return self.devices[dev_id_or_name]
        for d_id, d in self.devices.items():
            if d.get('name', '').lower() == dev_id_or_name.lower():
                return d
        return None

    def get_interface(self, dev: Dict[str, Any], iface_name: str) -> Optional[Dict[str, Any]]:
        for iface in dev.get('interfaces', []):
            if isinstance(iface, dict):
                if iface.get('name', '').lower() == iface_name.lower():
                    return iface
            elif isinstance(iface, str):
                if iface.lower() == iface_name.lower():
                    return {'name': iface, 'status': 'up'}
        return None

    def get_connected_link(self, dev_id: str, iface_name: str = '') -> Optional[Dict[str, Any]]:
        dev_id_str = str(dev_id).strip().lower()
        dev_obj = self.get_device(dev_id)
        dev_name = (dev_obj.get('name', '') if dev_obj else '').strip().lower()

        iface_str = str(iface_name or '').strip().lower()

        for conn in self.connections:
            if conn.get('status') == 'down' or conn.get('disabled'):
                continue
            src_id = str(conn.get('source_device', '')).strip().lower()
            tgt_id = str(conn.get('target_device', '')).strip().lower()
            src_p = str(conn.get('source_port', '')).strip().lower()
            tgt_p = str(conn.get('target_port', '')).strip().lower()

            # Port alias matching helper (e.g. g0/0 vs gigabitethernet0/0, fa0/1 vs fastethernet0/1)
            def ports_match(p_conn: str, p_req: str) -> bool:
                if not p_req or not p_conn:
                    return True
                p_c = p_conn.replace('gigabitethernet', 'g').replace('fastethernet', 'fa').replace('ethernet', 'eth')
                p_r = p_req.replace('gigabitethernet', 'g').replace('fastethernet', 'fa').replace('ethernet', 'eth')
                return p_c == p_r or p_conn == p_req

            if (src_id in (dev_id_str, dev_name)) and (not iface_str or ports_match(src_p, iface_str)):
                return conn
            if (tgt_id in (dev_id_str, dev_name)) and (not iface_str or ports_match(tgt_p, iface_str)):
                return conn

        # Fallback: if specific port not found, match any link connected to this device
        if iface_str:
            for conn in self.connections:
                if conn.get('status') == 'down' or conn.get('disabled'):
                    continue
                src_id = str(conn.get('source_device', '')).strip().lower()
                tgt_id = str(conn.get('target_device', '')).strip().lower()
                if src_id in (dev_id_str, dev_name) or tgt_id in (dev_id_str, dev_name):
                    return conn

        return None

    def get_neighbor(self, dev_id: str, iface_name: str = '') -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """
        Find peer device and interface connected on a given interface.
        Returns: (neighbor_dev_id, neighbor_iface_name, connection_info)
        """
        conn = self.get_connected_link(dev_id, iface_name)
        if not conn:
            return None
        dev_id_str = str(dev_id).strip().lower()
        dev_obj = self.get_device(dev_id)
        dev_name = (dev_obj.get('name', '') if dev_obj else '').strip().lower()

        src_id = str(conn.get('source_device', '')).strip().lower()
        if src_id in (dev_id_str, dev_name):
            return str(conn.get('target_device')), conn.get('target_port', ''), conn
        else:
            return str(conn.get('source_device')), conn.get('source_port', ''), conn

    def is_in_same_subnet(self, ip1_str: str, ip2_str: str, netmask_str: str) -> bool:
        try:
            net1 = ipaddress.IPv4Network(f"{ip1_str}/{netmask_str}", strict=False)
            net2 = ipaddress.IPv4Network(f"{ip2_str}/{netmask_str}", strict=False)
            return net1 == net2
        except Exception:
            return False

    def route_lookup(self, router_dev: Dict[str, Any], dest_ip: str) -> Optional[Dict[str, Any]]:
        """
        Longest Prefix Match routing table lookup on a router / L3 switch.
        Returns matching route: {'network': '...', 'mask': '...', 'gateway': '...', 'interface': '...'}
        """
        dest = ipaddress.IPv4Address(dest_ip)
        routes = router_dev.get('routes', [])
        best_match = None
        best_prefix_len = -1

        # First check directly connected interfaces
        for iface in router_dev.get('interfaces', []):
            if not isinstance(iface, dict):
                continue
            if iface.get('ip') and iface.get('mask'):
                try:
                    net = ipaddress.IPv4Network(f"{iface['ip']}/{iface['mask']}", strict=False)
                    if dest in net:
                        prefix_len = net.prefixlen
                        if prefix_len > best_prefix_len:
                            best_prefix_len = prefix_len
                            best_match = {
                                'network': str(net.network_address),
                                'mask': str(net.netmask),
                                'prefixlen': prefix_len,
                                'gateway': 'directly_connected',
                                'interface': iface.get('name', 'g0/0'),
                                'type': 'connected'
                            }
                except Exception:
                    pass

        # Also check router primary IP
        if router_dev.get('ip'):
            try:
                r_mask = router_dev.get('mask') or router_dev.get('subnet_mask') or '255.255.255.0'
                net = ipaddress.IPv4Network(f"{router_dev['ip']}/{r_mask}", strict=False)
                if dest in net:
                    prefix_len = net.prefixlen
                    if prefix_len > best_prefix_len:
                        best_prefix_len = prefix_len
                        best_match = {
                            'network': str(net.network_address),
                            'mask': str(net.netmask),
                            'prefixlen': prefix_len,
                            'gateway': 'directly_connected',
                            'interface': router_dev.get('interfaces', [{}])[0].get('name', 'g0/0') if router_dev.get('interfaces') else 'g0/0',
                            'type': 'connected'
                        }
            except Exception:
                pass

        # Then check static and dynamic routes
        for r in routes:
            try:
                net_str = r.get('network')
                mask_str = r.get('mask', '255.255.255.0')
                if '/' in net_str:
                    net = ipaddress.IPv4Network(net_str, strict=False)
                else:
                    net = ipaddress.IPv4Network(f"{net_str}/{mask_str}", strict=False)
                if dest in net:
                    if net.prefixlen > best_prefix_len:
                        best_prefix_len = net.prefixlen
                        best_match = {
                            'network': str(net.network_address),
                            'mask': str(net.netmask),
                            'prefixlen': net.prefixlen,
                            'gateway': r.get('gateway', r.get('next_hop', '')),
                            'interface': r.get('interface', ''),
                            'type': r.get('type', 'static')
                        }
            except Exception:
                pass

        # Check default gateway if no specific route matched
        if not best_match and router_dev.get('default_gateway'):
            best_match = {
                'network': '0.0.0.0',
                'mask': '0.0.0.0',
                'prefixlen': 0,
                'gateway': router_dev.get('default_gateway'),
                'interface': router_dev.get('gateway_interface', ''),
                'type': 'default'
            }

        return best_match

    def check_firewall(self, fw_dev: Dict[str, Any], src_ip: str, dest_ip: str, 
                       protocol: str, src_port: int, dest_port: int) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Evaluate firewall rules (Stateful & Packet filtering).
        Returns: (allowed: bool, reason: str, matched_rule: dict)
        """
        rules = fw_dev.get('firewall_rules', [])
        dev_id = str(fw_dev.get('id', ''))
        
        # 1. Check stateful connection tracking table
        for conn in self.conntrack_tables.get(dev_id, []):
            if (conn['src_ip'] == dest_ip and conn['dest_ip'] == src_ip and 
                conn['dest_port'] == src_port and conn['src_port'] == dest_port and
                conn['protocol'].lower() == protocol.lower()):
                return True, "ESTABLISHED state match (conntrack allowed)", {'action': 'allow', 'state': 'ESTABLISHED'}

        # 2. Iterate rules by order/priority
        for rule in rules:
            if not rule.get('enabled', True):
                continue
            
            # Protocol check
            rule_proto = rule.get('protocol', 'any').lower()
            if rule_proto != 'any' and rule_proto != protocol.lower():
                continue
            
            # Source IP check
            rule_src = rule.get('src_ip', 'any').lower()
            if rule_src != 'any':
                try:
                    if '/' not in rule_src and rule_src.count('.') == 3:
                        rule_src += '/32'
                    src_net = ipaddress.IPv4Network(rule_src, strict=False)
                    if ipaddress.IPv4Address(src_ip) not in src_net:
                        continue
                except Exception:
                    pass

            # Dest IP check
            rule_dest = rule.get('dest_ip', 'any').lower()
            if rule_dest != 'any':
                try:
                    if '/' not in rule_dest and rule_dest.count('.') == 3:
                        rule_dest += '/32'
                    dest_net = ipaddress.IPv4Network(rule_dest, strict=False)
                    if ipaddress.IPv4Address(dest_ip) not in dest_net:
                        continue
                except Exception:
                    pass

            # Port check
            rule_port = str(rule.get('port', 'any')).lower()
            if rule_port != 'any' and rule_port != '*':
                try:
                    if int(rule_port) != int(dest_port):
                        continue
                except Exception:
                    pass

            action = rule.get('action', 'deny').lower()
            if action == 'allow':
                # Track in conntrack for stateful return traffic
                self.conntrack_tables[dev_id].append({
                    'src_ip': src_ip,
                    'dest_ip': dest_ip,
                    'src_port': src_port,
                    'dest_port': dest_port,
                    'protocol': protocol,
                    'created_at': time.time()
                })
                return True, f"Matched firewall rule #{rule.get('id', 'N')}: ALLOW", rule
            else:
                return False, f"Matched firewall rule #{rule.get('id', 'N')}: DENY", rule

        # Default policy: if no rules matched
        default_policy = fw_dev.get('default_policy', 'deny').lower()
        if default_policy == 'allow':
            return True, "Default policy: ALLOW", {'action': 'allow', 'is_default': True}
        else:
            return False, "Default policy: DENY (no matching allow rule)", {'action': 'deny', 'is_default': True}

    def simulate_packet(self, src_dev_id: str, dest_ip: str, protocol: str = 'ICMP', 
                        dest_port: int = 80, src_port: int = 49152) -> Dict[str, Any]:
        """
        Trace packet forwarding through the network topology.
        Returns a rich execution trace dict with detailed hop diagnostics.
        """
        src_dev = self.get_device(src_dev_id)
        if not src_dev:
            return {
                'success': False,
                'drop_reason': 'SOURCE_DEVICE_NOT_FOUND',
                'details': f"Source device ID '{src_dev_id}' does not exist in the network topology.",
                'hops': []
            }

        src_ip = src_dev.get('ip') or ''
        src_mask = src_dev.get('subnet_mask') or src_dev.get('mask') or '255.255.255.0'
        src_mac = src_dev.get('mac') or '00:11:22:33:44:01'
        src_gw = src_dev.get('gateway') or src_dev.get('default_gateway') or ''
        
        # If source has no IP configured
        if not src_ip and protocol != 'DHCP':
            return {
                'success': False,
                'drop_reason': 'SOURCE_NO_IP',
                'details': f"Source device '{src_dev.get('name')}' has no IP address configured.",
                'hops': []
            }

        hops: List[Dict[str, Any]] = []
        current_dev = src_dev
        current_dev_id = str(src_dev.get('id', src_dev_id))
        ttl = 64
        current_src_ip = src_ip
        current_dest_ip = dest_ip
        current_vlan = 1

        # Hop 0: Source Device Origin
        hops.append({
            'step': 1,
            'device_id': current_dev_id,
            'device_name': current_dev.get('name'),
            'device_type': current_dev.get('type') or current_dev.get('category'),
            'interface': 'lo0' if current_src_ip == current_dest_ip else 'eth0',
            'action': 'ORIGINATE_PACKET',
            'details': f"Originated {protocol} packet from {current_src_ip}:{src_port} to {current_dest_ip}:{dest_port} (TTL={ttl})",
            'src_ip': current_src_ip,
            'dest_ip': current_dest_ip,
            'vlan': current_vlan
        })

        # Self-ping / loopback test
        if current_src_ip == current_dest_ip:
            hops.append({
                'step': 2,
                'device_id': current_dev_id,
                'device_name': current_dev.get('name'),
                'device_type': current_dev.get('type'),
                'interface': 'lo0',
                'action': 'LOOPBACK_DELIVERED',
                'details': "Delivered to local loopback interface.",
                'src_ip': current_src_ip,
                'dest_ip': current_dest_ip
            })
            return {'success': True, 'delivered': True, 'hops': hops, 'status': 'DELIVERED', 'summary': 'Packet delivered to local host'}

        visited = set()
        max_hops = 20

        while len(hops) < max_hops:
            visited.add(current_dev_id)
            dev_type = (current_dev.get('category') or current_dev.get('type') or '').lower()

            # Check if current device is the final destination (primary IP or any interface IP)
            is_dest = (current_dev.get('ip') == current_dest_ip)
            if not is_dest:
                for ifc in current_dev.get('interfaces', []):
                    if isinstance(ifc, dict) and ifc.get('ip') == current_dest_ip:
                        is_dest = True
                        break

            if is_dest:
                hops.append({
                    'step': len(hops) + 1,
                    'device_id': current_dev_id,
                    'device_name': current_dev.get('name'),
                    'device_type': dev_type,
                    'interface': 'rx',
                    'action': 'PACKET_RECEIVED_BY_DESTINATION',
                    'details': f"Packet successfully arrived at destination {current_dev.get('name')} ({current_dest_ip})",
                    'src_ip': current_src_ip,
                    'dest_ip': current_dest_ip
                })
                return {
                    'success': True,
                    'delivered': True,
                    'hops': hops,
                    'status': 'DELIVERED',
                    'summary': f"Successfully reached destination {current_dev.get('name')} in {len(hops)} hops."
                }

            # Check interfaces on current device to find outbound interface
            out_iface = None
            next_hop_ip = None

            if 'switch' in dev_type:
                # Layer 2 Switch forwarding: MAC learning and VLAN lookup
                # MAC learning on incoming
                self.mac_tables[current_dev_id][src_mac] = 'inbound'
                
                # Check target destination device connected to this switch
                found_egress = False
                for iface in current_dev.get('interfaces', []):
                    iface_name = iface.get('name') if isinstance(iface, dict) else str(iface)
                    neighbor = self.get_neighbor(current_dev_id, iface_name)
                    if neighbor:
                        nbr_id, nbr_port, conn = neighbor
                        nbr_dev = self.get_device(nbr_id)
                        if nbr_dev:
                            # If neighbor is destination or neighbor is a gateway towards destination
                            if nbr_dev.get('ip') == current_dest_ip:
                                out_iface = iface_name
                                found_egress = True
                                break
                            # Check if neighbor has interface with dest IP
                            for n_ifc in nbr_dev.get('interfaces', []):
                                if isinstance(n_ifc, dict) and n_ifc.get('ip') == current_dest_ip:
                                    out_iface = iface_name
                                    found_egress = True
                                    break
                            if found_egress:
                                break
                            # Or if neighbor is a router
                            nbr_type = (nbr_dev.get('category') or nbr_dev.get('type') or '').lower()
                            if 'router' in nbr_type or 'firewall' in nbr_type or 'switch' in nbr_type:
                                if nbr_id not in visited:
                                    out_iface = iface_name
                                    found_egress = True
                                    break
                
                if not found_egress:
                    # Broadcast / flood to connected ports
                    for iface in current_dev.get('interfaces', []):
                        iface_name = iface.get('name') if isinstance(iface, dict) else str(iface)
                        neighbor = self.get_neighbor(current_dev_id, iface_name)
                        if neighbor and neighbor[0] not in visited:
                            out_iface = iface_name
                            break

                if not out_iface:
                    return {
                        'success': False,
                        'delivered': False,
                        'drop_reason': 'SWITCH_NO_OUTBOUND_PORT',
                        'details': f"Switch '{current_dev.get('name')}' has no forward path to reach {current_dest_ip}.",
                        'hops': hops
                    }

            elif 'router' in dev_type or 'firewall' in dev_type or current_dev.get('is_layer3'):
                # Layer 3 Routing Lookup
                if 'firewall' in dev_type:
                    # Firewall inspection
                    allowed, reason, rule = self.check_firewall(
                        current_dev, current_src_ip, current_dest_ip, protocol, src_port, dest_port
                    )
                    hops.append({
                        'step': len(hops) + 1,
                        'device_id': current_dev_id,
                        'device_name': current_dev.get('name'),
                        'device_type': dev_type,
                        'action': 'FIREWALL_INSPECTION',
                        'allowed': allowed,
                        'details': f"Firewall policy check: {reason}",
                        'rule': rule
                    })
                    if not allowed:
                        return {
                            'success': False,
                            'drop_reason': 'FIREWALL_DENY',
                            'details': f"Firewall '{current_dev.get('name')}' dropped packet: {reason}",
                            'hops': hops
                        }

                # Decrement TTL
                ttl -= 1
                if ttl <= 0:
                    return {
                        'success': False,
                        'drop_reason': 'TTL_EXPIRED',
                        'details': "Time To Live (TTL) expired in transit (routing loop detected).",
                        'hops': hops
                    }

                # Route lookup
                route = self.route_lookup(current_dev, current_dest_ip)
                if not route:
                    return {
                        'success': False,
                        'drop_reason': 'NO_ROUTE_TO_HOST',
                        'details': f"Router '{current_dev.get('name')}' has no route to destination network {current_dest_ip}.",
                        'hops': hops
                    }

                out_iface = route.get('interface')
                next_hop_ip = route.get('gateway')

                hops.append({
                    'step': len(hops) + 1,
                    'device_id': current_dev_id,
                    'device_name': current_dev.get('name'),
                    'device_type': dev_type,
                    'interface': out_iface,
                    'action': 'ROUTE_FORWARD',
                    'details': f"Routing match: {route.get('network')}/{route.get('prefixlen')} via {next_hop_ip or 'direct'} on {out_iface}",
                    'route': route
                })

                # NAT check
                if current_dev.get('nat_enabled'):
                    nat_pool = current_dev.get('nat_public_ip') or current_dev.get('ip')
                    if nat_pool:
                        old_ip = current_src_ip
                        current_src_ip = nat_pool
                        hops.append({
                            'step': len(hops) + 1,
                            'device_id': current_dev_id,
                            'device_name': current_dev.get('name'),
                            'device_type': dev_type,
                            'action': 'NAT_TRANSLATION',
                            'details': f"Source NAT applied: {old_ip} -> {current_src_ip}"
                        })

            else:
                # End host / Server / PC / Camera / Printer
                # Check if destination is in same subnet
                same_subnet = self.is_in_same_subnet(current_src_ip, current_dest_ip, src_mask)
                if same_subnet:
                    # Direct ARP resolution to destination on local link
                    out_iface = 'eth0'
                else:
                    # Send to default gateway
                    if not src_gw:
                        return {
                            'success': False,
                            'drop_reason': 'GATEWAY_MISSING',
                            'details': f"Device '{current_dev.get('name')}' has no default gateway configured for destination {current_dest_ip}.",
                            'hops': hops
                        }
                    # Check if gateway is on the same subnet as host IP
                    if not self.is_in_same_subnet(current_src_ip, src_gw, src_mask):
                        return {
                            'success': False,
                            'drop_reason': 'GATEWAY_SUBNET_MISMATCH',
                            'details': f"Configured default gateway {src_gw} is not in the same subnet as host IP {current_src_ip} (mask {src_mask}).",
                            'hops': hops
                        }
                    # Check if a gateway device with this IP exists
                    gw_lookup = self.get_device_by_ip(src_gw)
                    if not gw_lookup:
                        return {
                            'success': False,
                            'drop_reason': 'GATEWAY_UNREACHABLE',
                            'details': f"ARP resolution for default gateway {src_gw} failed. Gateway is unreachable.",
                            'hops': hops
                        }
                    next_hop_ip = src_gw
                    out_iface = 'eth0'

            # If out_iface not specified, pick first connected interface
            if not out_iface and current_dev.get('interfaces'):
                first_ifc = current_dev['interfaces'][0]
                out_iface = first_ifc.get('name') if isinstance(first_ifc, dict) else str(first_ifc)

            # Find connected link from out_iface
            neighbor_info = self.get_neighbor(current_dev_id, out_iface) if out_iface else None
            if not neighbor_info:
                # If no connection found on that interface, try any connected port
                for ifc in current_dev.get('interfaces', []):
                    ifc_name = ifc.get('name') if isinstance(ifc, dict) else str(ifc)
                    n_info = self.get_neighbor(current_dev_id, ifc_name)
                    if n_info and n_info[0] not in visited:
                        neighbor_info = n_info
                        out_iface = ifc_name
                        break

            if not neighbor_info:
                return {
                    'success': False,
                    'delivered': False,
                    'drop_reason': 'CABLE_DISCONNECTED',
                    'details': f"Interface '{out_iface or 'unassigned'}' on device '{current_dev.get('name')}' is not connected to any cable.",
                    'hops': hops
                }

            nbr_id, nbr_port, conn_info = neighbor_info
            nbr_dev = self.get_device(nbr_id)
            if not nbr_dev:
                return {
                    'success': False,
                    'drop_reason': 'PEER_DEVICE_NOT_FOUND',
                    'details': f"Target device {nbr_id} does not exist.",
                    'hops': hops
                }

            # Check link status
            if conn_info.get('status') == 'down' or conn_info.get('disabled'):
                return {
                    'success': False,
                    'drop_reason': 'LINK_DOWN',
                    'details': f"Cable link between {current_dev.get('name')} and {nbr_dev.get('name')} is in DOWN state.",
                    'hops': hops
                }

            # Hop across the cable
            hops.append({
                'step': len(hops) + 1,
                'device_id': nbr_id,
                'device_name': nbr_dev.get('name'),
                'device_type': nbr_dev.get('type') or nbr_dev.get('category'),
                'interface': nbr_port,
                'action': 'FRAME_TRANSIT',
                'details': f"Frame traversed link [{current_dev.get('name')}:{out_iface} -> {nbr_dev.get('name')}:{nbr_port}] ({conn_info.get('type', 'copper_straight')})",
                'cable_type': conn_info.get('type', 'copper_straight'),
                'src_ip': current_src_ip,
                'dest_ip': current_dest_ip
            })

            # Advance to neighbor
            current_dev = nbr_dev
            current_dev_id = nbr_id

        return {
            'success': False,
            'drop_reason': 'HOP_LIMIT_EXCEEDED',
            'details': "Packet exceeded maximum hop count without reaching destination.",
            'hops': hops
        }
