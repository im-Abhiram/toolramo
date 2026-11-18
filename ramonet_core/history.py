"""
Ramonet Core - Configuration History & Change Management
Captures configuration snapshots, computes diffs, tracks authors and timestamps.
"""
from typing import Dict, List, Any, Optional
import json
import difflib
from datetime import datetime

class ConfigurationHistoryManager:
    """Manages versioned configuration snapshots and diff calculations."""

    @classmethod
    def compute_device_diff(cls, old_config: Dict[str, Any], new_config: Dict[str, Any]) -> Dict[str, Any]:
        """Compares two device configurations and returns structured added, removed, and modified fields."""
        added = {}
        removed = {}
        modified = {}

        all_keys = set(old_config.keys()).union(set(new_config.keys()))

        for k in all_keys:
            if k in ['x', 'y']:
                continue  # Skip visual coordinates in config diff
            val_old = old_config.get(k)
            val_new = new_config.get(k)

            if k not in old_config:
                added[k] = val_new
            elif k not in new_config:
                removed[k] = val_old
            elif val_old != val_new:
                modified[k] = {'old': val_old, 'new': val_new}

        return {
            'added': added,
            'removed': removed,
            'modified': modified,
            'has_changes': bool(added or removed or modified)
        }

    @classmethod
    def compute_running_config_diff(cls, old_text: str, new_text: str, fromfile: str = 'Previous Configuration', tofile: str = 'Active Configuration') -> List[str]:
        """Generates standard unified diff lines between two running configurations."""
        old_lines = (old_text or '').strip().splitlines(keepends=True)
        new_lines = (new_text or '').strip().splitlines(keepends=True)
        diff = difflib.unified_diff(
            old_lines, new_lines,
            fromfile=fromfile,
            tofile=tofile,
            n=2
        )
        return [line.rstrip() for line in diff]

    @classmethod
    def compute_unified_diff(cls, old_text: str, new_text: str, fromfile: str = 'Previous Configuration', tofile: str = 'Active Configuration') -> List[str]:
        """Alias for compute_running_config_diff."""
        return cls.compute_running_config_diff(old_text, new_text, fromfile=fromfile, tofile=tofile)
