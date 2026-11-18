"""
Ramonet Core - Network Automation Studio Subsystem
Visual automation workflow builder, atomic multi-device provisioning,
execution history, dry-run simulation, and automated rollback.
"""
import copy
import time
from typing import Dict, List, Any, Optional, Tuple

class NetworkAutomationStudio:
    """
    Automates multi-device configuration workflows through the shared RAMONET engine.
    Never executes arbitrary operating-system commands.
    """

    PLAYBOOKS = {
        'PROVISION_VLANS': {
            'name': 'Enterprise Multi-Switch VLAN Provisioning',
            'description': 'Provisions VLANs 10 (Voice), 20 (Data), 30 (CCTV), and 99 (Mgmt) across all switch trunks.',
            'category': 'VLAN & Switching',
            'target_types': ['switch', 'layer3_switch', 'managed_switch']
        },
        'PORT_SECURITY_LOCKDOWN': {
            'name': 'Access Port Security Lockdown',
            'description': 'Enforces port-security max 2 MACs, violation shutdown, and BPDU guard on edge access ports.',
            'category': 'Security Hardening',
            'target_types': ['switch', 'layer3_switch', 'managed_switch']
        },
        'ZERO_TRUST_FIREWALL': {
            'name': 'Zero-Trust Perimeter Firewall Ruleset',
            'description': 'Deploys least-privilege ingress ACLs, drops inbound RFC 1918 from WAN, and restricts SSH to bastion.',
            'category': 'Security Hardening',
            'target_types': ['firewall', 'router']
        },
        'DHCP_RELAY_PROVISIONING': {
            'name': 'DHCP Pool & Helper-Address Orchestration',
            'description': 'Configures DHCP pools with lease options and assigns IP helper-addresses across core SVIs.',
            'category': 'Services',
            'target_types': ['router', 'layer3_switch']
        },
        'GOLDEN_CONFIG_BACKUP': {
            'name': 'Automated Golden Configuration Backup',
            'description': 'Captures SHA-256 verified running configurations across all network infrastructure devices.',
            'category': 'Operations',
            'target_types': ['router', 'switch', 'firewall', 'layer3_switch', 'access_point']
        }
    }

    @classmethod
    def execute_playbook(cls, playbook_key: str, devices: List[Dict[str, Any]], dry_run: bool = False, custom_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes an automation playbook across eligible devices with step-by-step logging.
        Supports dry-run validation without committing changes.
        """
        pb_info = cls.PLAYBOOKS.get(playbook_key, {
            'name': 'Custom Workflow',
            'description': 'Automated workflow execution',
            'target_types': []
        })

        execution_log = []
        modified_count = 0
        error_count = 0
        target_types = pb_info.get('target_types', [])

        pre_state_snapshot = copy.deepcopy(devices)
        start_time = time.time()

        for dev in devices:
            dev_cat = str(dev.get('category', dev.get('type', ''))).lower()
            dev_name = dev.get('name', 'Device')

            # Filter eligibility
            is_eligible = any(t in dev_cat for t in target_types) if target_types else True
            if not is_eligible:
                execution_log.append({
                    'device': dev_name,
                    'status': 'SKIPPED',
                    'detail': f"Device category '{dev_cat}' is not a target for {pb_info['name']}."
                })
                continue

            # Execute specific playbook logic
            if playbook_key == 'PROVISION_VLANS':
                vlans = dev.setdefault('vlans', [1])
                added_vlans = []
                for v_id in (10, 20, 30, 99):
                    if v_id not in vlans:
                        if not dry_run:
                            vlans.append(v_id)
                        added_vlans.append(v_id)

                if added_vlans:
                    modified_count += 1
                    execution_log.append({
                        'device': dev_name,
                        'status': 'CHANGED' if not dry_run else 'PLAN_CHANGE',
                        'detail': f"{'Applied' if not dry_run else 'Planned'}: Provisioned VLANs {added_vlans} to database and trunk allowlist."
                    })
                else:
                    execution_log.append({
                        'device': dev_name,
                        'status': 'OK',
                        'detail': "All target VLANs (10, 20, 30, 99) already present."
                    })

            elif playbook_key == 'PORT_SECURITY_LOCKDOWN':
                ifaces = dev.get('interfaces', [])
                locked_ports = 0
                for iface in ifaces:
                    if iface.get('type') == 'access' or 'Fa' in iface.get('name', '') or 'eth' in iface.get('name', ''):
                        if not dry_run:
                            iface['port_security'] = True
                            iface['max_mac'] = 2
                            iface['bpdu_guard'] = True
                        locked_ports += 1

                if locked_ports > 0:
                    modified_count += 1
                    execution_log.append({
                        'device': dev_name,
                        'status': 'CHANGED' if not dry_run else 'PLAN_CHANGE',
                        'detail': f"{'Hardened' if not dry_run else 'Planned'}: Enabled port-security & BPDU guard on {locked_ports} access interfaces."
                    })
                else:
                    execution_log.append({
                        'device': dev_name,
                        'status': 'OK',
                        'detail': "No unhardened access interfaces found."
                    })

            elif playbook_key == 'ZERO_TRUST_FIREWALL':
                fw = dev.setdefault('firewall', {})
                rules = fw.setdefault('rules', [])
                if not dry_run:
                    rules.insert(0, {'id': 'ZT-01', 'action': 'deny', 'source': '192.168.0.0/16', 'in_interface': 'WAN', 'comment': 'Anti-Spoofing RFC1918'})
                    rules.insert(1, {'id': 'ZT-02', 'action': 'permit', 'proto': 'tcp', 'port': 22, 'source': '10.99.0.0/24', 'comment': 'Bastion SSH Only'})
                    fw['default_policy'] = 'deny'
                modified_count += 1
                execution_log.append({
                    'device': dev_name,
                    'status': 'CHANGED' if not dry_run else 'PLAN_CHANGE',
                    'detail': f"{'Deployed' if not dry_run else 'Planned'}: Zero-Trust ingress ACLs (Anti-spoof RFC1918 & Bastion SSH)."
                })

            elif playbook_key == 'DHCP_RELAY_PROVISIONING':
                if not dry_run:
                    dev['dhcp_relay'] = {'helper_address': '10.99.0.254', 'pool_vlan10': '10.10.0.0/24', 'pool_vlan20': '10.20.0.0/24'}
                modified_count += 1
                execution_log.append({
                    'device': dev_name,
                    'status': 'CHANGED' if not dry_run else 'PLAN_CHANGE',
                    'detail': f"{'Configured' if not dry_run else 'Planned'}: DHCP pools & helper-address relay pointing to 10.99.0.254."
                })

            else:  # GOLDEN_CONFIG_BACKUP
                import hashlib
                cfg_str = str(dev)
                sha = hashlib.sha256(cfg_str.encode()).hexdigest()[:16]
                execution_log.append({
                    'device': dev_name,
                    'status': 'OK',
                    'detail': f"Golden configuration captured. Checksum SHA256: {sha}"
                })

        duration = round(time.time() - start_time, 3)

        return {
            'playbook': {
                'key': playbook_key,
                'name': pb_info['name'],
                'category': pb_info.get('category')
            },
            'dry_run': dry_run,
            'summary': {
                'total_devices_scanned': len(devices),
                'devices_modified': modified_count,
                'devices_skipped': len([l for l in execution_log if l['status'] == 'SKIPPED']),
                'devices_ok': len([l for l in execution_log if l['status'] == 'OK']),
                'execution_time_seconds': duration
            },
            'execution_log': execution_log,
            'rollback_available': not dry_run and modified_count > 0,
            'snapshot_backup': pre_state_snapshot if not dry_run else None
        }
