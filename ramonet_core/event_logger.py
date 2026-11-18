"""
Ramonet Core - Unified Event & Alert Logger
Central notification and event dispatcher across the platform.
"""
from typing import Dict, List, Any, Optional
import time

class EventSeverity:
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'

class EventCategory:
    INTERFACE = 'interface'
    ROUTING = 'routing'
    SECURITY = 'security'
    POE = 'poe'
    CCTV = 'cctv'
    STORAGE = 'storage'
    IPAM = 'ipam'
    SYSTEM = 'system'

class EventLogger:
    """In-memory and persistent event tracking."""
    _events: List[Dict[str, Any]] = []

    def __init__(self):
        pass

    @classmethod
    def emit_event(cls, category: str, severity: str, title: str, description: str, device_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        event = {
            'id': len(cls._events) + 1,
            'timestamp': time.time(),
            'formatted_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'category': category,
            'severity': severity,
            'title': title,
            'description': description,
            'device_id': device_id,
            'metadata': metadata or {},
            'status': 'active'  # 'active', 'acknowledged', 'resolved'
        }
        cls._events.append(event)
        return event

    def log(self, severity: str, category: str, message: str, device_id: Optional[str] = None) -> Dict[str, Any]:
        return self.emit_event(category=category, severity=severity, title=category, description=message, device_id=device_id)

    @classmethod
    def get_events(cls, severity: Optional[str] = None, category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        results = cls._events
        if severity:
            results = [e for e in results if e['severity'] == severity]
        if category:
            results = [e for e in results if e['category'] == category]
        return list(reversed(results))[:limit]

    @classmethod
    def get_active_alerts(cls) -> List[Dict[str, Any]]:
        return [e for e in cls._events if e['status'] == 'active' and e['severity'] in ['warning', 'critical']]

    @classmethod
    def acknowledge_alert(cls, alert_id: int) -> bool:
        for e in cls._events:
            if e['id'] == alert_id:
                e['status'] = 'acknowledged'
                return True
        return False

    @classmethod
    def resolve_alert(cls, alert_id: int) -> bool:
        for e in cls._events:
            if e['id'] == alert_id:
                e['status'] = 'resolved'
                return True
        return False

    @classmethod
    def clear_events(cls) -> None:
        cls._events.clear()
