"""
Ramonet Core - High Availability & Redundancy Lab Subsystem
Simulates Spanning Tree (STP/RSTP), VRRP/HSRP First-Hop Redundancy,
and LACP/EtherChannel link aggregation failover.
"""
from typing import Dict, List, Any, Optional

class HighAvailabilityEngine:
    """
    Simulates enterprise redundancy mechanisms and failover behaviors.
    """

    @classmethod
    def simulate_ha_scenario(cls, proto: str, fault_injected: bool = False) -> Dict[str, Any]:
        """
        Simulates STP loop-free convergence, VRRP virtual gateway failover, or LACP trunk resilience.
        """
        proto = proto.upper()

        if proto == 'VRRP':
            return cls._simulate_vrrp(fault_injected)
        elif proto == 'LACP':
            return cls._simulate_lacp(fault_injected)
        else: # default STP
            return cls._simulate_stp(fault_injected)

    @classmethod
    def _simulate_stp(cls, fault_injected: bool) -> Dict[str, Any]:
        # Triangle topology: SW1 (Root), SW2 (Distribution), SW3 (Access)
        sw1 = {'name': 'SW1-Core', 'priority': 4096, 'mac': '00:1a:2b:3c:4d:01', 'is_root': True}
        sw2 = {'name': 'SW2-Dist', 'priority': 32768, 'mac': '00:1a:2b:3c:4d:02', 'is_root': False}
        sw3 = {'name': 'SW3-Access', 'priority': 32768, 'mac': '00:1a:2b:3c:4d:03', 'is_root': False}

        if not fault_injected:
            links = [
                {'from': 'SW1-Core', 'to': 'SW2-Dist', 'port_from': 'Gi0/1 (DP)', 'port_to': 'Gi0/1 (RP)', 'state': 'FORWARDING', 'cost': 4},
                {'from': 'SW1-Core', 'to': 'SW3-Access', 'port_from': 'Gi0/2 (DP)', 'port_to': 'Gi0/1 (RP)', 'state': 'FORWARDING', 'cost': 4},
                {'from': 'SW2-Dist', 'to': 'SW3-Access', 'port_from': 'Gi0/2 (DP)', 'port_to': 'Gi0/2 (AP/BLK)', 'state': 'BLOCKING', 'cost': 4}
            ]
            status_note = "STP loop prevention active: Link SW2-SW3 is in BLOCKING state (Discarding) to prevent broadcast storm."
            loop_prevented = True
            active_paths = 2
        else:
            # Fault: Link SW1-SW3 severed
            links = [
                {'from': 'SW1-Core', 'to': 'SW2-Dist', 'port_from': 'Gi0/1 (DP)', 'port_to': 'Gi0/1 (RP)', 'state': 'FORWARDING', 'cost': 4},
                {'from': 'SW1-Core', 'to': 'SW3-Access', 'port_from': 'Gi0/2 [DOWN]', 'port_to': 'Gi0/1 [DOWN]', 'state': 'SEVERED', 'cost': 999},
                {'from': 'SW2-Dist', 'to': 'SW3-Access', 'port_from': 'Gi0/2 (DP)', 'port_to': 'Gi0/2 (RP)', 'state': 'FORWARDING', 'cost': 8}
            ]
            status_note = "Failover occurred! Primary link SW1-SW3 was severed. RSTP detected BPDU timeout and unblocked SW2-SW3 within <1 second."
            loop_prevented = True
            active_paths = 2

        return {
            'protocol': 'STP / RSTP (IEEE 802.1w)',
            'fault_injected': fault_injected,
            'root_bridge': sw1,
            'switches': [sw1, sw2, sw3],
            'links': links,
            'convergence_time_ms': 45 if fault_injected else 0,
            'loop_prevented': loop_prevented,
            'status_note': status_note
        }

    @classmethod
    def _simulate_vrrp(cls, fault_injected: bool) -> Dict[str, Any]:
        virtual_ip = '192.168.1.1'
        virtual_mac = '00:00:5E:00:01:01'

        if not fault_injected:
            master = {'name': 'R1-Master', 'priority': 110, 'state': 'MASTER', 'physical_ip': '192.168.1.252', 'wan_link': 'UP'}
            backup = {'name': 'R2-Backup', 'priority': 100, 'state': 'BACKUP', 'physical_ip': '192.168.1.253', 'wan_link': 'UP'}
            active_gateway = 'R1-Master (192.168.1.252)'
            status_note = "VRRP Virtual IP 192.168.1.1 is serviced by R1 (Priority 110). R2 is in BACKUP standby listening for advertisements."
        else:
            # Fault: R1 WAN link severed, priority decremented by 20 -> 90 < 100
            master = {'name': 'R1-Master', 'priority': 90, 'state': 'BACKUP', 'physical_ip': '192.168.1.252', 'wan_link': 'DOWN'}
            backup = {'name': 'R2-Backup', 'priority': 100, 'state': 'MASTER', 'physical_ip': '192.168.1.253', 'wan_link': 'UP'}
            active_gateway = 'R2-Backup (192.168.1.253)'
            status_note = "WAN link failure on R1 detected! IP SLA tracked interface went DOWN. R2 preempted ownership of Virtual IP 192.168.1.1 with zero gateway downtime."

        return {
            'protocol': 'VRRP (RFC 5798) / HSRP',
            'fault_injected': fault_injected,
            'virtual_ip': virtual_ip,
            'virtual_mac': virtual_mac,
            'active_gateway': active_gateway,
            'routers': [master, backup],
            'failover_time_ms': 850 if fault_injected else 0,
            'status_note': status_note
        }

    @classmethod
    def _simulate_lacp(cls, fault_injected: bool) -> Dict[str, Any]:
        if not fault_injected:
            members = [
                {'port': 'Gi0/1', 'speed': '1 Gbps', 'state': 'BUNDLED (Active)', 'load_pct': 50},
                {'port': 'Gi0/2', 'speed': '1 Gbps', 'state': 'BUNDLED (Active)', 'load_pct': 50}
            ]
            total_bw = '2 Gbps Full-Duplex'
            status_note = "LACP 802.3ad Port-Channel 1 active. Traffic load-balanced across dual 1 Gbps physical member links."
        else:
            members = [
                {'port': 'Gi0/1', 'speed': '1 Gbps', 'state': 'LINK_DOWN (Severed)', 'load_pct': 0},
                {'port': 'Gi0/2', 'speed': '1 Gbps', 'state': 'BUNDLED (Active)', 'load_pct': 100}
            ]
            total_bw = '1 Gbps Full-Duplex (Degraded)'
            status_note = "Physical link Gi0/1 cut! LACP maintained session persistence on Gi0/2. Zero packet loss or STP topology change."

        return {
            'protocol': 'LACP (IEEE 802.3ad) / EtherChannel',
            'fault_injected': fault_injected,
            'channel_group': 'Port-Channel 1 (Po1)',
            'aggregated_bandwidth': total_bw,
            'member_links': members,
            'status_note': status_note
        }
