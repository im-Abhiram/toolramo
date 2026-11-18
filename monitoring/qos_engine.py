"""
Ramonet Core - QoS & Traffic Engineering Subsystem
Simulates traffic classification, DSCP/CoS marking, priority queuing (PQ/LLQ/CBWFQ),
traffic shaping, bottleneck congestion, latency, jitter, and packet loss modeling.
"""
from typing import Dict, List, Any

class QoSEngine:
    """
    Simulates network congestion and compares Best-Effort vs Enterprise QoS scheduling.
    """

    TRAFFIC_CLASSES = [
        {'name': 'Voice (VoIP / SIP)', 'dscp': 'EF (46)', 'cos': 5, 'rate_mbps': 1.5, 'type': 'strict_priority'},
        {'name': 'Video Conferencing', 'dscp': 'AF41 (34)', 'cos': 4, 'rate_mbps': 4.0, 'type': 'bandwidth_guaranteed'},
        {'name': 'CCTV Surveillance', 'dscp': 'AF31 (26)', 'cos': 3, 'rate_mbps': 3.5, 'type': 'bandwidth_guaranteed'},
        {'name': 'Business Critical (ERP)', 'dscp': 'AF21 (18)', 'cos': 2, 'rate_mbps': 2.5, 'type': 'bandwidth_guaranteed'},
        {'name': 'Best Effort (Web/Bulk)', 'dscp': 'BE (0)', 'cos': 0, 'rate_mbps': 3.5, 'type': 'default_queue'}
    ]

    @classmethod
    def simulate_qos_comparison(cls, qos_enabled: bool, bottleneck_capacity_mbps: float = 10.0) -> Dict[str, Any]:
        """
        Simulates link congestion with 15.0 Mbps offered load across a 10.0 Mbps bottleneck link.
        Calculates packet loss, queueing latency, and jitter for each traffic class.
        """
        total_offered = sum(c['rate_mbps'] for c in cls.TRAFFIC_CLASSES) # 15.0 Mbps
        congestion_ratio = total_offered / bottleneck_capacity_mbps # 1.5x overload

        class_results = []

        for c in cls.TRAFFIC_CLASSES:
            name = c['name']
            rate = c['rate_mbps']

            if not qos_enabled:
                # FIFO Tail Drop: Loss distributed across all streams proportionally
                loss_pct = round((1.0 - (bottleneck_capacity_mbps / total_offered)) * 100, 1) # ~33.3%
                latency_ms = 145.0 + (rate * 5.0)
                jitter_ms = 48.0
                delivered_mbps = round(rate * (1 - loss_pct / 100), 2)
                queue_status = 'FIFO Buffer Overrun (Tail Drop)'
            else:
                # LLQ / CBWFQ Active:
                if c['type'] == 'strict_priority':
                    loss_pct = 0.0
                    latency_ms = 8.5
                    jitter_ms = 2.1
                    delivered_mbps = rate
                    queue_status = 'Priority Queue (PQ) - Zero Drop'
                elif c['type'] == 'bandwidth_guaranteed':
                    loss_pct = 0.0
                    latency_ms = 24.0
                    jitter_ms = 6.4
                    delivered_mbps = rate
                    queue_status = 'CBWFQ Guaranteed Bandwidth'
                else: # Best Effort
                    # Best effort takes all the drop penalty
                    loss_pct = 68.5
                    latency_ms = 185.0
                    jitter_ms = 62.0
                    delivered_mbps = round(rate * (1 - loss_pct / 100), 2)
                    queue_status = 'Default Queue (WRED Active Drop)'

            class_results.append({
                'name': name,
                'dscp': c['dscp'],
                'cos': c['cos'],
                'offered_mbps': rate,
                'delivered_mbps': delivered_mbps,
                'loss_percentage': loss_pct,
                'latency_ms': latency_ms,
                'jitter_ms': jitter_ms,
                'queue_status': queue_status
            })

        return {
            'qos_enabled': qos_enabled,
            'bottleneck_capacity_mbps': bottleneck_capacity_mbps,
            'total_offered_load_mbps': total_offered,
            'total_delivered_mbps': sum(r['delivered_mbps'] for r in class_results),
            'congestion_level': '150% Overload' if congestion_ratio > 1 else 'Nominal',
            'classes': class_results
        }
