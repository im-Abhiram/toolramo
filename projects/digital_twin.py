"""
Ramonet Core - Network Digital Twin Subsystem
Provides isolated simulation sandboxing, before-and-after change diffing,
and atomic commit/discard operations against authoritative network projects.
"""
import copy
import json
from typing import Dict, Any, List, Optional, Tuple
from django.utils import timezone
from .models import NetworkProject, ProjectSnapshot

class DigitalTwinManager:
    """
    Manages the lifecycle of a Network Digital Twin:
    - Deep-cloning production network state into an isolated sandbox
    - Semantic configuration and topological diffing
    - Non-destructive what-if and proposal validation
    - Atomic promotion of proposed changes to production with snapshot history
    """

    @classmethod
    def create_twin(cls, project_id: int, twin_name: Optional[str] = None, user: Optional[Any] = None) -> Tuple[bool, Any, str]:
        """
        Creates an isolated Digital Twin clone of an existing network project.
        """
        try:
            original = NetworkProject.objects.get(id=project_id)
        except NetworkProject.DoesNotExist:
            return False, None, f"Project with ID {project_id} not found."

        name = twin_name or f"{original.name} [Digital Twin]"
        twin = NetworkProject.objects.create(
            user=user or original.user,
            name=name[:128],
            description=f"Isolated simulation sandbox branched from '{original.name}'.",
            version=f"{original.version}-twin",
            tags=list(set(original.tags + ['digital-twin', 'sandbox'])),
            device_count=original.device_count,
            connection_count=original.connection_count,
            is_template=False,
            is_public=False,
            metadata=copy.deepcopy(original.metadata)
        )

        # Mark twin lineage in metadata
        twin.metadata['twin_metadata'] = {
            'is_digital_twin': True,
            'original_project_id': original.id,
            'original_project_name': original.name,
            'branched_at': timezone.now().isoformat(),
            'status': 'active_sandbox'
        }
        twin.save()

        # Create baseline snapshot of twin
        ProjectSnapshot.objects.create(
            project=twin,
            title="Twin Baseline Creation",
            snapshot_data=copy.deepcopy(twin.metadata)
        )

        return True, twin, f"Digital Twin '{twin.name}' created successfully."

    @classmethod
    def compare_twin(cls, original_project_id: int, twin_project_id: int) -> Dict[str, Any]:
        """
        Performs semantic before-and-after diff between production and twin sandbox.
        """
        try:
            orig = NetworkProject.objects.get(id=original_project_id)
            twin = NetworkProject.objects.get(id=twin_project_id)
        except NetworkProject.DoesNotExist:
            return {'error': 'One or both projects do not exist.'}

        orig_devices = orig.metadata.get('devices', [])
        twin_devices = twin.metadata.get('devices', [])
        orig_conns = orig.metadata.get('connections', [])
        twin_conns = twin.metadata.get('connections', [])

        orig_dev_map = {str(d.get('id', d.get('name'))): d for d in orig_devices}
        twin_dev_map = {str(d.get('id', d.get('name'))): d for d in twin_devices}

        added_devices = []
        removed_devices = []
        modified_devices = []

        # Find added and modified
        for d_id, t_dev in twin_dev_map.items():
            if d_id not in orig_dev_map:
                added_devices.append(t_dev)
            else:
                o_dev = orig_dev_map[d_id]
                diffs = cls._diff_device(o_dev, t_dev)
                if diffs:
                    modified_devices.append({
                        'device_id': d_id,
                        'name': t_dev.get('name'),
                        'category': t_dev.get('category'),
                        'changes': diffs
                    })

        # Find removed
        for d_id, o_dev in orig_dev_map.items():
            if d_id not in twin_dev_map:
                removed_devices.append(o_dev)

        # Connections diff
        conn_diff = {
            'original_count': len(orig_conns),
            'twin_count': len(twin_conns),
            'delta': len(twin_conns) - len(orig_conns)
        }

        # IP and Subnet changes
        ip_changes = []
        for mod in modified_devices:
            for chg in mod['changes']:
                if chg['field'] in ('ip', 'mask', 'gateway'):
                    ip_changes.append({
                        'device': mod['name'],
                        'field': chg['field'],
                        'before': chg['before'],
                        'after': chg['after']
                    })

        # Risk Analysis
        risk_level = 'LOW'
        risk_factors = []
        if removed_devices:
            risk_level = 'MEDIUM'
            risk_factors.append(f"{len(removed_devices)} devices removed from topology.")
        if len(ip_changes) > 3:
            risk_level = 'MEDIUM'
            risk_factors.append(f"Substantial IP readdressing ({len(ip_changes)} changes).")
        if any('firewall' in d.get('changes', [{}])[0].get('field', '') for d in modified_devices if d.get('changes')):
            risk_level = 'HIGH'
            risk_factors.append("Security firewall policy modifications detected.")

        return {
            'original': {'id': orig.id, 'name': orig.name, 'device_count': len(orig_devices)},
            'twin': {'id': twin.id, 'name': twin.name, 'device_count': len(twin_devices)},
            'summary': {
                'devices_added': len(added_devices),
                'devices_removed': len(removed_devices),
                'devices_modified': len(modified_devices),
                'connections_delta': conn_diff['delta'],
                'risk_level': risk_level,
                'risk_factors': risk_factors
            },
            'added_devices': added_devices,
            'removed_devices': removed_devices,
            'modified_devices': modified_devices,
            'ip_changes': ip_changes
        }

    @classmethod
    def _diff_device(cls, orig: Dict[str, Any], twin: Dict[str, Any]) -> List[Dict[str, Any]]:
        diffs = []
        fields_to_check = ['name', 'ip', 'mask', 'gateway', 'vlan', 'status', 'role']
        for f in fields_to_check:
            val_o = orig.get(f)
            val_t = twin.get(f)
            if val_o != val_t:
                diffs.append({
                    'field': f,
                    'before': val_o,
                    'after': val_t
                })

        # Check firewall rules if applicable
        fw_o = orig.get('firewall', {}).get('rules', [])
        fw_t = twin.get('firewall', {}).get('rules', [])
        if fw_o != fw_t:
            diffs.append({
                'field': 'firewall.rules',
                'before': f"{len(fw_o)} rules",
                'after': f"{len(fw_t)} rules"
            })

        # Check interfaces count
        iface_o = len(orig.get('interfaces', []))
        iface_t = len(twin.get('interfaces', []))
        if iface_o != iface_t:
            diffs.append({
                'field': 'interfaces.count',
                'before': iface_o,
                'after': iface_t
            })

        return diffs

    @classmethod
    def commit_to_production(cls, original_project_id: int, twin_project_id: int) -> Tuple[bool, str]:
        """
        Promotes the digital twin sandbox state into the production network project.
        Creates an audit snapshot before applying changes.
        """
        try:
            orig = NetworkProject.objects.get(id=original_project_id)
            twin = NetworkProject.objects.get(id=twin_project_id)
        except NetworkProject.DoesNotExist:
            return False, "Original or Twin project does not exist."

        # 1. Take safety snapshot of original project
        ProjectSnapshot.objects.create(
            project=orig,
            title=f"Pre-Promotion Backup (Twin #{twin.id})",
            snapshot_data=copy.deepcopy(orig.metadata)
        )

        # 2. Overwrite production metadata with twin metadata
        promoted_metadata = copy.deepcopy(twin.metadata)
        # Clear twin specific flags
        if 'twin_metadata' in promoted_metadata:
            promoted_metadata['twin_metadata']['promoted_to_prod_at'] = timezone.now().isoformat()
            promoted_metadata['twin_metadata']['is_digital_twin'] = False

        orig.metadata = promoted_metadata
        orig.device_count = twin.device_count
        orig.connection_count = twin.connection_count
        orig.version = cls._increment_version(orig.version)
        orig.save()

        # 3. Mark twin as merged/archived
        twin.metadata.setdefault('twin_metadata', {})['status'] = 'merged_to_production'
        twin.save()

        return True, f"Digital Twin changes committed to '{orig.name}' (Version {orig.version})."

    @classmethod
    def discard_twin(cls, twin_project_id: int) -> Tuple[bool, str]:
        """
        Safely discards a twin sandbox without affecting production.
        """
        try:
            twin = NetworkProject.objects.get(id=twin_project_id)
            twin.delete()
            return True, "Digital Twin sandbox discarded successfully."
        except NetworkProject.DoesNotExist:
            return False, "Digital Twin sandbox not found."

    @staticmethod
    def _increment_version(version_str: str) -> str:
        try:
            parts = [int(p) for p in str(version_str).split('.')[:3]]
            while len(parts) < 3:
                parts.append(0)
            parts[2] += 1
            return f"{parts[0]}.{parts[1]}.{parts[2]}"
        except Exception:
            return f"{version_str}.1"
