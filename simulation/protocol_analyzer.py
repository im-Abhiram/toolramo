"""
Ramonet Core - Packet Capture & Protocol Analyzer Subsystem
Provides deep packet inspection, Wireshark-style protocol dissection,
layered OSI model analysis, and Wireshark-syntax packet filtering.
"""
import time
import random
from typing import Dict, List, Any, Optional

class ProtocolAnalyzerEngine:
    """
    Simulates packet-level captures and provides full OSI layer dissection.
    Supports Ethernet II, 802.1Q, ARP, IPv4, IPv6, ICMP, TCP, UDP, DNS, DHCP, and HTTP.
    """

    @classmethod
    def generate_capture(cls, scenario: str, topology_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generates realistic, dissected packet traces for the requested network interaction.
        Scenarios: 'dns_query', 'dhcp_dora', 'http_session', 'arp_resolution', 'icmp_ping', 'vlan_trunk'
        """
        ctx = topology_context or {}
        src_ip = ctx.get('src_ip', '192.168.1.105')
        dst_ip = ctx.get('dst_ip', '192.168.1.1')
        src_mac = ctx.get('src_mac', '52:54:00:12:34:56')
        dst_mac = ctx.get('dst_mac', '52:54:00:ab:cd:ef')
        bcast_mac = 'ff:ff:ff:ff:ff:ff'
        vlan_id = int(ctx.get('vlan_id', 10))

        packets = []
        base_time = 0.000000

        if scenario == 'arp_resolution':
            # Packet 1: ARP Request (Broadcast)
            p1 = cls._build_packet(
                pkt_id=1, rel_time=base_time,
                src_mac=src_mac, dst_mac=bcast_mac,
                eth_type='0x0806 (ARP)', vlan=vlan_id,
                l3_proto='ARP',
                src_ip=src_ip, dst_ip=dst_ip,
                l4_proto=None, src_port=None, dst_port=None,
                length=64, info=f"Who has {dst_ip}? Tell {src_ip}",
                device='Workstation-01', iface='eth0',
                action='BROADCAST', drop_reason=None,
                arp_data={'opcode': 1, 'op_name': 'Request', 'sender_mac': src_mac, 'sender_ip': src_ip, 'target_mac': '00:00:00:00:00:00', 'target_ip': dst_ip}
            )
            packets.append(p1)

            # Packet 2: ARP Reply (Unicast)
            p2 = cls._build_packet(
                pkt_id=2, rel_time=base_time + 0.001420,
                src_mac=dst_mac, dst_mac=src_mac,
                eth_type='0x0806 (ARP)', vlan=vlan_id,
                l3_proto='ARP',
                src_ip=dst_ip, dst_ip=src_ip,
                l4_proto=None, src_port=None, dst_port=None,
                length=64, info=f"{dst_ip} is at {dst_mac}",
                device='Core-Switch-01', iface='Gi0/1',
                action='FORWARD', drop_reason=None,
                arp_data={'opcode': 2, 'op_name': 'Reply', 'sender_mac': dst_mac, 'sender_ip': dst_ip, 'target_mac': src_mac, 'target_ip': src_ip}
            )
            packets.append(p2)

        elif scenario == 'dhcp_dora':
            # 1. DHCP Discover
            p1 = cls._build_packet(
                pkt_id=1, rel_time=base_time,
                src_mac=src_mac, dst_mac=bcast_mac,
                eth_type='0x0800 (IPv4)', vlan=1,
                l3_proto='IPv4', src_ip='0.0.0.0', dst_ip='255.255.255.255',
                l4_proto='UDP', src_port=68, dst_port=67,
                length=342, info="DHCP Discover - Transaction ID 0x3d1a8f02",
                device='Client-Laptop', iface='eth0', action='BROADCAST', drop_reason=None,
                dhcp_data={'msg_type': 'DHCP DISCOVER', 'xid': '0x3d1a8f02', 'ciaddr': '0.0.0.0', 'yiaddr': '0.0.0.0', 'chaddr': src_mac}
            )
            packets.append(p1)

            # 2. DHCP Offer
            p2 = cls._build_packet(
                pkt_id=2, rel_time=base_time + 0.004812,
                src_mac=dst_mac, dst_mac=src_mac,
                eth_type='0x0800 (IPv4)', vlan=1,
                l3_proto='IPv4', src_ip='192.168.1.1', dst_ip='192.168.1.150',
                l4_proto='UDP', src_port=67, dst_port=68,
                length=342, info="DHCP Offer - Offered IP: 192.168.1.150",
                device='DHCP-Server', iface='eth0', action='FORWARD', drop_reason=None,
                dhcp_data={'msg_type': 'DHCP OFFER', 'xid': '0x3d1a8f02', 'ciaddr': '0.0.0.0', 'yiaddr': '192.168.1.150', 'siaddr': '192.168.1.1', 'lease_time': 86400}
            )
            packets.append(p2)

            # 3. DHCP Request
            p3 = cls._build_packet(
                pkt_id=3, rel_time=base_time + 0.006120,
                src_mac=src_mac, dst_mac=bcast_mac,
                eth_type='0x0800 (IPv4)', vlan=1,
                l3_proto='IPv4', src_ip='0.0.0.0', dst_ip='255.255.255.255',
                l4_proto='UDP', src_port=68, dst_port=67,
                length=342, info="DHCP Request - Requested: 192.168.1.150",
                device='Client-Laptop', iface='eth0', action='BROADCAST', drop_reason=None,
                dhcp_data={'msg_type': 'DHCP REQUEST', 'xid': '0x3d1a8f02', 'ciaddr': '0.0.0.0', 'yiaddr': '192.168.1.150', 'server_id': '192.168.1.1'}
            )
            packets.append(p3)

            # 4. DHCP ACK
            p4 = cls._build_packet(
                pkt_id=4, rel_time=base_time + 0.009450,
                src_mac=dst_mac, dst_mac=src_mac,
                eth_type='0x0800 (IPv4)', vlan=1,
                l3_proto='IPv4', src_ip='192.168.1.1', dst_ip='192.168.1.150',
                l4_proto='UDP', src_port=67, dst_port=68,
                length=342, info="DHCP ACK - Lease granted for 192.168.1.150 (24h)",
                device='DHCP-Server', iface='eth0', action='DELIVER', drop_reason=None,
                dhcp_data={'msg_type': 'DHCP ACK', 'xid': '0x3d1a8f02', 'ciaddr': '0.0.0.0', 'yiaddr': '192.168.1.150', 'dns': '1.1.1.1', 'router': '192.168.1.1'}
            )
            packets.append(p4)

        elif scenario == 'dns_query':
            # 1. Standard DNS Query (UDP 53)
            p1 = cls._build_packet(
                pkt_id=1, rel_time=base_time,
                src_mac=src_mac, dst_mac=dst_mac,
                eth_type='0x0800 (IPv4)', vlan=vlan_id,
                l3_proto='IPv4', src_ip=src_ip, dst_ip='8.8.8.8',
                l4_proto='UDP', src_port=53241, dst_port=53,
                length=74, info="Standard query 0x1f4a A api.ramonet.internal",
                device='Client-PC', iface='eth0', action='FORWARD', drop_reason=None,
                dns_data={'xid': '0x1f4a', 'flags': '0x0100 (Standard query)', 'query': 'api.ramonet.internal', 'qtype': 'A (IPv4 Address)'}
            )
            packets.append(p1)

            # 2. DNS Response
            p2 = cls._build_packet(
                pkt_id=2, rel_time=base_time + 0.014230,
                src_mac=dst_mac, dst_mac=src_mac,
                eth_type='0x0800 (IPv4)', vlan=vlan_id,
                l3_proto='IPv4', src_ip='8.8.8.8', dst_ip=src_ip,
                l4_proto='UDP', src_port=53, dst_port=53241,
                length=90, info="Standard query response 0x1f4a A api.ramonet.internal -> 10.20.0.15",
                device='Gateway-Router', iface='Gi0/0', action='DELIVER', drop_reason=None,
                dns_data={'xid': '0x1f4a', 'flags': '0x8180 (Standard query response, No error)', 'query': 'api.ramonet.internal', 'answers': [{'name': 'api.ramonet.internal', 'type': 'A', 'addr': '10.20.0.15', 'ttl': 300}]}
            )
            packets.append(p2)

        elif scenario == 'http_session':
            # TCP 3-Way Handshake: SYN -> SYN-ACK -> ACK
            # 1. SYN
            packets.append(cls._build_packet(
                pkt_id=1, rel_time=base_time,
                src_mac=src_mac, dst_mac=dst_mac,
                eth_type='0x0800 (IPv4)', vlan=vlan_id,
                l3_proto='IPv4', src_ip=src_ip, dst_ip='10.0.0.50',
                l4_proto='TCP', src_port=49210, dst_port=80,
                length=66, info="49210 -> 80 [SYN] Seq=0 Win=64240 Len=0 MSS=1460",
                device='Workstation-01', iface='eth0', action='FORWARD', drop_reason=None,
                tcp_data={'flags': 'SYN', 'seq': 0, 'ack': 0, 'win': 64240}
            ))

            # 2. SYN-ACK
            packets.append(cls._build_packet(
                pkt_id=2, rel_time=base_time + 0.008450,
                src_mac=dst_mac, dst_mac=src_mac,
                eth_type='0x0800 (IPv4)', vlan=vlan_id,
                l3_proto='IPv4', src_ip='10.0.0.50', dst_ip=src_ip,
                l4_proto='TCP', src_port=80, dst_port=49210,
                length=66, info="80 -> 49210 [SYN, ACK] Seq=0 Ack=1 Win=65535 Len=0",
                device='Web-Server-01', iface='eth0', action='FORWARD', drop_reason=None,
                tcp_data={'flags': 'SYN, ACK', 'seq': 0, 'ack': 1, 'win': 65535}
            ))

            # 3. ACK
            packets.append(cls._build_packet(
                pkt_id=3, rel_time=base_time + 0.009100,
                src_mac=src_mac, dst_mac=dst_mac,
                eth_type='0x0800 (IPv4)', vlan=vlan_id,
                l3_proto='IPv4', src_ip=src_ip, dst_ip='10.0.0.50',
                l4_proto='TCP', src_port=49210, dst_port=80,
                length=54, info="49210 -> 80 [ACK] Seq=1 Ack=1 Win=64240 Len=0",
                device='Workstation-01', iface='eth0', action='FORWARD', drop_reason=None,
                tcp_data={'flags': 'ACK', 'seq': 1, 'ack': 1, 'win': 64240}
            ))

            # 4. HTTP GET
            packets.append(cls._build_packet(
                pkt_id=4, rel_time=base_time + 0.010240,
                src_mac=src_mac, dst_mac=dst_mac,
                eth_type='0x0800 (IPv4)', vlan=vlan_id,
                l3_proto='IPv4', src_ip=src_ip, dst_ip='10.0.0.50',
                l4_proto='TCP', src_port=49210, dst_port=80,
                length=248, info="GET /index.html HTTP/1.1",
                device='Workstation-01', iface='eth0', action='FORWARD', drop_reason=None,
                tcp_data={'flags': 'PSH, ACK', 'seq': 1, 'ack': 1, 'win': 64240},
                http_data={'method': 'GET', 'uri': '/index.html', 'version': 'HTTP/1.1', 'host': '10.0.0.50', 'user_agent': 'Mozilla/5.0 (Ramonet Simulator 2.0)'}
            ))

            # 5. HTTP 200 OK Response
            packets.append(cls._build_packet(
                pkt_id=5, rel_time=base_time + 0.018940,
                src_mac=dst_mac, dst_mac=src_mac,
                eth_type='0x0800 (IPv4)', vlan=vlan_id,
                l3_proto='IPv4', src_ip='10.0.0.50', dst_ip=src_ip,
                l4_proto='TCP', src_port=80, dst_port=49210,
                length=584, info="HTTP/1.1 200 OK (text/html)",
                device='Web-Server-01', iface='eth0', action='DELIVER', drop_reason=None,
                tcp_data={'flags': 'PSH, ACK', 'seq': 1, 'ack': 195, 'win': 65340},
                http_data={'status_code': 200, 'phrase': 'OK', 'server': 'Apache/2.4 (Debian)', 'content_type': 'text/html; charset=UTF-8', 'content_length': 312}
            ))

        elif scenario == 'vlan_trunk':
            # 802.1Q Encapsulated Frame across Switch Trunk
            p1 = cls._build_packet(
                pkt_id=1, rel_time=base_time,
                src_mac='52:54:00:aa:11:22', dst_mac='52:54:00:bb:33:44',
                eth_type='0x8100 (802.1Q)', vlan=20,
                l3_proto='IPv4', src_ip='10.20.0.10', dst_ip='10.20.0.50',
                l4_proto='TCP', src_port=58120, dst_port=443,
                length=1518, info="802.1Q VLAN 20: 10.20.0.10 -> 10.20.0.50 [ACK] Ingress Trunk Gi0/24",
                device='Distribution-SW', iface='Gi0/24', action='FORWARD', drop_reason=None,
                vlan_data={'vlan_id': 20, 'priority_pcp': 3, 'dei': 0, 'encapsulated_proto': '0x0800 (IPv4)'}
            )
            packets.append(p1)

        else:  # default 'icmp_ping'
            # Echo Request
            packets.append(cls._build_packet(
                pkt_id=1, rel_time=base_time,
                src_mac=src_mac, dst_mac=dst_mac,
                eth_type='0x0800 (IPv4)', vlan=vlan_id,
                l3_proto='IPv4', src_ip=src_ip, dst_ip=dst_ip,
                l4_proto='ICMP', src_port=None, dst_port=None,
                length=98, info=f"Echo (ping) request id=0x1a2b, seq=1, ttl=64",
                device='Source-Host', iface='eth0', action='FORWARD', drop_reason=None,
                icmp_data={'type': 8, 'type_str': 'Echo Request', 'code': 0, 'checksum': '0x4d5e', 'seq': 1, 'ttl': 64}
            ))
            # Echo Reply
            packets.append(cls._build_packet(
                pkt_id=2, rel_time=base_time + 0.003180,
                src_mac=dst_mac, dst_mac=src_mac,
                eth_type='0x0800 (IPv4)', vlan=vlan_id,
                l3_proto='IPv4', src_ip=dst_ip, dst_ip=src_ip,
                l4_proto='ICMP', src_port=None, dst_port=None,
                length=98, info=f"Echo (ping) reply id=0x1a2b, seq=1, ttl=64 (time=3.18ms)",
                device='Target-Host', iface='eth0', action='DELIVER', drop_reason=None,
                icmp_data={'type': 0, 'type_str': 'Echo Reply', 'code': 0, 'checksum': '0x556e', 'seq': 1, 'ttl': 64}
            ))

        return packets

    @classmethod
    def _build_packet(cls, pkt_id: int, rel_time: float, src_mac: str, dst_mac: str, eth_type: str,
                      vlan: int, l3_proto: str, src_ip: str, dst_ip: str,
                      l4_proto: Optional[str], src_port: Optional[int], dst_port: Optional[int],
                      length: int, info: str, device: str, iface: str, action: str,
                      drop_reason: Optional[str] = None, **extra_layers) -> Dict[str, Any]:

        # OSI Layer Structured Dissection Tree
        osi_layers = {
            'layer_1_physical': {
                'title': 'Layer 1: Physical Interface',
                'device': device,
                'interface': iface,
                'medium': '1000Base-T (Cat6 UTP)' if 'Gi' in iface or 'eth' in iface else '10GBase-LR (Single-mode Fiber)',
                'speed': '1 Gbps Full-Duplex',
                'frame_size': f"{length} bytes on wire ({length * 8} bits)"
            },
            'layer_2_datalink': {
                'title': f'Layer 2: Ethernet II (Dst: {dst_mac}, Src: {src_mac})',
                'destination_mac': dst_mac,
                'source_mac': src_mac,
                'ethertype': eth_type,
                'vlan_802_1q': {
                    'vlan_id': vlan,
                    'priority': 0,
                    'tpid': '0x8100'
                } if vlan > 1 else 'Untagged (VLAN 1 Access)'
            },
            'layer_3_network': {
                'title': f'Layer 3: {l3_proto} (Src: {src_ip}, Dst: {dst_ip})',
                'protocol': l3_proto,
                'source_ip': src_ip,
                'destination_ip': dst_ip,
                'ttl': 64,
                'identification': hex(random.randint(4000, 65000))
            }
        }

        if l4_proto:
            osi_layers['layer_4_transport'] = {
                'title': f'Layer 4: {l4_proto} (Src Port: {src_port}, Dst Port: {dst_port})',
                'protocol': l4_proto,
                'source_port': src_port,
                'destination_port': dst_port,
                'details': extra_layers.get('tcp_data') or extra_layers.get('udp_data') or {}
            }

        if 'dns_data' in extra_layers:
            osi_layers['layer_7_application'] = {
                'title': 'Layer 7: Domain Name System (DNS)',
                'details': extra_layers['dns_data']
            }
        elif 'dhcp_data' in extra_layers:
            osi_layers['layer_7_application'] = {
                'title': 'Layer 7: Dynamic Host Configuration Protocol (DHCP)',
                'details': extra_layers['dhcp_data']
            }
        elif 'http_data' in extra_layers:
            osi_layers['layer_7_application'] = {
                'title': 'Layer 7: Hypertext Transfer Protocol (HTTP)',
                'details': extra_layers['http_data']
            }
        elif 'arp_data' in extra_layers:
            osi_layers['layer_3_network']['title'] = 'Layer 3: Address Resolution Protocol (ARP)'
            osi_layers['layer_3_network']['details'] = extra_layers['arp_data']
        elif 'icmp_data' in extra_layers:
            osi_layers['layer_4_transport'] = {
                'title': 'Layer 4: Internet Control Message Protocol (ICMP)',
                'details': extra_layers['icmp_data']
            }

        # Simulated Hex Dump (32 bytes sample)
        hex_lines = [
            f"0000   {dst_mac.replace(':', ' ')} {src_mac.replace(':', ' ')} 08 00",
            f"0010   45 00 00 {length:02x} 1a 2b 40 00 40 {0x06 if l4_proto=='TCP' else 0x11:02x} 7c 4a c0 a8 01 69",
            f"0020   c0 a8 01 01 {src_port or 0:04x} {dst_port or 0:04x} 00 00 00 00 00 00"
        ]

        return {
            'number': pkt_id,
            'time': f"{rel_time:.6f}",
            'source_mac': src_mac,
            'dest_mac': dst_mac,
            'source_ip': src_ip,
            'dest_ip': dst_ip,
            'protocol': l4_proto or l3_proto,
            'length': length,
            'vlan': vlan,
            'src_port': src_port,
            'dest_port': dst_port,
            'device': device,
            'interface': iface,
            'action': action,
            'drop_reason': drop_reason,
            'info': info,
            'osi_layers': osi_layers,
            'hex_dump': "\n".join(hex_lines)
        }

    @classmethod
    def filter_packets(cls, packets: List[Dict[str, Any]], filter_query: str) -> List[Dict[str, Any]]:
        """
        Applies Wireshark-syntax filter expressions to packet captures.
        Supports:
          - 'dns', 'http', 'arp', 'icmp', 'tcp', 'udp'
          - 'ip.src == "..."', 'ip.dst == "..."'
          - 'tcp.port == 80', 'vlan == 10'
          - 'action == "DROP"'
        """
        if not filter_query or not filter_query.strip():
            return packets

        q = filter_query.strip().lower()
        filtered = []

        for p in packets:
            proto = p['protocol'].lower()
            if q in ('dns', 'http', 'arp', 'icmp', 'tcp', 'udp'):
                if proto == q or (q == 'http' and 'http' in p['info'].lower()):
                    filtered.append(p)
                continue

            if 'ip.src' in q:
                target_ip = q.split('==')[-1].replace('"', '').replace("'", "").strip()
                if p['source_ip'] == target_ip:
                    filtered.append(p)
                continue

            if 'ip.dst' in q:
                target_ip = q.split('==')[-1].replace('"', '').replace("'", "").strip()
                if p['dest_ip'] == target_ip:
                    filtered.append(p)
                continue

            if 'vlan' in q:
                try:
                    target_vlan = int(q.split('==')[-1].strip())
                    if p.get('vlan') == target_vlan:
                        filtered.append(p)
                except ValueError:
                    pass
                continue

            if 'action' in q:
                target_act = q.split('==')[-1].replace('"', '').replace("'", "").strip().upper()
                if p.get('action') == target_act:
                    filtered.append(p)
                continue

            # Fallback text substring search
            if q in p['info'].lower() or q in p['source_ip'] or q in p['dest_ip'] or q in p['device'].lower():
                filtered.append(p)

        return filtered
