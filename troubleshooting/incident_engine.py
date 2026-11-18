"""
Ramonet Core - Network Incident Response Simulator Subsystem
Interactive defensive security response lab covering rogue DHCP, ARP spoofing,
SYN flood DDoS, port scans, firewall exposure, C2 beaconing, and config tampering.
"""
from typing import Dict, List, Any, Optional

class IncidentResponseEngine:
    """
    Defensive network incident simulator with 4-phase incident handling:
    Triage -> Containment -> Eradication -> Post-Incident Report.
    """

    SCENARIOS = {
        'ROGUE_DHCP': {
            'title': 'Rogue DHCP Server & Man-in-the-Middle Poisoning',
            'severity': 'CRITICAL',
            'category': 'Layer 2 Attack',
            'description': 'An unauthorized personal laptop connected to switchport Gi0/14 is broadcasting fraudulent DHCP Offer messages with a malicious default gateway.',
            'indicator': 'Syslog: %DHCP_SNOOPING-4-ROGUE_OFFER: Received DHCP offer on untrusted port Gi0/14 offering gateway 192.168.1.250',
            'affected_node': 'Switchport Gi0/14 (Workstation-22)',
            'recommended_containment': 'Isolate Switchport Gi0/14 & Enable DHCP Snooping with Trust Port configuration.'
        },
        'ARP_SPOOFING': {
            'title': 'Dynamic ARP Inspection (DAI) / Gateway Cache Poisoning',
            'severity': 'HIGH',
            'category': 'Layer 2 Attack',
            'description': 'Gratuitous ARP replies originating from MAC 48:2a:e3:11:22:33 claiming ownership of Gateway IP 192.168.1.1.',
            'indicator': 'Syslog: %SEC-4-ARP_INSPECTION_DROP: Dropped invalid ARP reply for 192.168.1.1 on port Gi0/8',
            'affected_node': 'Switchport Gi0/8 (Compromised Node)',
            'recommended_containment': 'Quarantine port Gi0/8 and enforce Dynamic ARP Inspection (DAI).'
        },
        'SYN_FLOOD': {
            'title': 'TCP SYN Flood Volumetric Denial of Service',
            'severity': 'HIGH',
            'category': 'Perimeter Attack',
            'description': 'Perimeter firewall state table exhaustion caused by 85,000 half-open TCP SYN handshakes targeting DMZ web server.',
            'indicator': 'Firewall Alert: State table 94% full (94,210 concurrent connections). Dropping legitimate sessions.',
            'affected_node': 'Perimeter Firewall -> DMZ Web Server (10.0.0.50)',
            'recommended_containment': 'Deploy TCP SYN Cookies & apply rate-limiting policy on WAN interface.'
        },
        'C2_BEACONING': {
            'title': 'Command & Control (C2) Malware Beaconing',
            'severity': 'CRITICAL',
            'category': 'Endpoint Compromise',
            'description': 'Finance workstation PC-04 is initiating encrypted outbound beacon requests every 60 seconds to a known malicious IP.',
            'indicator': 'DNS Threat Alert: High-frequency domain generation algorithm (DGA) lookups from host 10.20.0.42 to external IP 198.51.100.99',
            'affected_node': 'Finance-PC-04 (IP: 10.20.0.42)',
            'recommended_containment': 'Move PC-04 to Quarantine VLAN 666 and block destination IP 198.51.100.99 at edge firewall.'
        },
        'CONFIG_TAMPERING': {
            'title': 'Unauthorized Privilege Escalation & Backdoor',
            'severity': 'CRITICAL',
            'category': 'Configuration Tampering',
            'description': 'A new privileged local user "backup_admin" was provisioned and SNMP community string was altered to "public".',
            'indicator': 'Audit Event: %SYS-5-CONFIG_I: Configured from console by root. User backup_admin created with privilege 15.',
            'affected_node': 'Core-Router-01 (Management Plane)',
            'recommended_containment': 'Delete unauthorized account, roll back to golden config baseline, and rotate all administrative keys.'
        }
    }

    @classmethod
    def get_scenario_details(cls, scenario_key: str) -> Dict[str, Any]:
        return cls.SCENARIOS.get(scenario_key, cls.SCENARIOS['ROGUE_DHCP'])

    @classmethod
    def execute_containment(cls, scenario_key: str, action: str) -> Dict[str, Any]:
        """
        Executes defensive containment action (quarantine port, block IP, apply ACL, restore config).
        """
        sc = cls.get_scenario_details(scenario_key)
        
        timeline = [
            {'time': 'T-00:04:12', 'event': 'Threat detected by SIEM / Syslog monitor.'},
            {'time': 'T-00:02:45', 'event': f'Telemetry correlated to affected asset: {sc["affected_node"]}'},
            {'time': 'T-00:00:01', 'event': f'Defensive containment action applied: {action}'},
            {'time': 'NOW', 'event': 'Asset isolated. Malicious telemetry dropped. Network restored to baseline.'}
        ]

        report = {
            'incident_id': f"INC-{abs(hash(scenario_key)) % 100000:05d}",
            'scenario_title': sc['title'],
            'severity': sc['severity'],
            'status': 'CONTAINED & MITIGATED',
            'affected_asset': sc['affected_node'],
            'root_cause': sc['description'],
            'action_taken': action,
            'timeline': timeline,
            'residual_risk': 'LOW',
            'follow_up_recommendations': [
                'Retain firewall and switch syslog telemetry for 90 days.',
                'Run automated Configuration Compliance Centre audit across all switches.',
                'Enforce 802.1X Network Access Control (NAC) on all physical access ports.'
            ]
        }

        return {
            'success': True,
            'message': f"Containment action '{action}' executed successfully. Threat neutralized.",
            'incident_report': report
        }
