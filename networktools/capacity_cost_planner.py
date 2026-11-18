"""
Ramonet Core - Network Capacity & Budgetary Cost Planner Subsystem
Calculates switch port density, PoE power budgets, rack U sizing, thermal BTU heat loads,
UPS runtime capacity, surveillance storage requirements, and categorized Bill of Materials (BOM).
"""
from typing import Dict, List, Any

class CapacityCostPlanner:
    """
    Enterprise infrastructure planning calculator.
    Clearly distinguishes estimated costs from vendor quotations.
    """

    UNIT_ESTIMATES = {
        'router_enterprise': 1450.0,
        'switch_48p_poe': 1850.0,
        'switch_24p_poe': 1100.0,
        'access_point_wifi6': 320.0,
        'patch_panel_24p': 75.0,
        'cat6_box_1000ft': 180.0,
        'rack_enclosure_42u': 950.0,
        'rack_enclosure_24u': 620.0,
        'ups_3000va_rack': 1400.0,
        'ups_1500va_rack': 780.0,
        'nvr_storage_server_tb': 35.0 # per TB
    }

    @classmethod
    def calculate_plan(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes complete infrastructure capacity and budgetary BOM.
        """
        workstations = int(params.get('workstations', 80))
        voip_phones = int(params.get('voip_phones', 60))
        cameras = int(params.get('cameras', 30))
        access_points = int(params.get('access_points', 12))
        servers = int(params.get('servers', 6))
        retention_days = int(params.get('retention_days', 30))
        ups_backup_mins = int(params.get('ups_backup_mins', 30))

        # 1. Port Density
        total_endpoints = workstations + voip_phones + cameras + access_points + servers
        growth_margin_pct = 25
        total_ports_needed = int(round(total_endpoints * (1 + growth_margin_pct / 100)))

        # Recommended switch distribution (prefer 48-port switches)
        switches_48p = total_ports_needed // 48
        remainder = total_ports_needed % 48
        switches_24p = 1 if remainder > 0 else 0
        total_switches = max(1, switches_48p + switches_24p)
        total_switch_ports = (switches_48p * 48) + (switches_24p * 24)

        # 2. PoE Power Budget
        # VoIP (802.3af 12W average), Cameras (802.3at 18W average), APs (802.3at 22W average)
        poe_watts_voip = voip_phones * 12.0
        poe_watts_cctv = cameras * 18.0
        poe_watts_ap = access_points * 22.0
        total_poe_watts = poe_watts_voip + poe_watts_cctv + poe_watts_ap
        poe_budget_with_margin = round(total_poe_watts * 1.20, 1)

        # 3. Rack Units (U)
        patch_panels_needed = (total_switch_ports + 23) // 24
        wire_managers = total_switches
        rack_u_switches = total_switches
        rack_u_servers = servers * 2
        rack_u_ups = 3
        total_rack_u = rack_u_switches + patch_panels_needed + wire_managers + rack_u_servers + rack_u_ups + 2 # PDU & shelf
        recommended_rack = '42U Standard Server Enclosure' if total_rack_u > 24 else '24U Mid-Depth Enclosure'

        # 4. Thermal & Heat Dissipation
        total_system_watts = total_poe_watts + (total_switches * 80.0) + (servers * 250.0) + 150.0 # baseline router & PDU
        total_btu_hr = round(total_system_watts * 3.412142, 1)

        # 5. UPS Sizing
        total_va = round(total_system_watts / 0.8 * 1.25, 0) # 0.8 PF + 25% safety
        recommended_ups = '3000VA / 2700W On-Line Double Conversion' if total_va > 1500 else '1500VA Line-Interactive'

        # 6. Surveillance Storage
        # 5 Mbps stream per camera * 86400s / 8 bits / 1024 / 1024 = GB/day
        gb_per_camera_day = (5.0 * 86400) / (8 * 1024) # ~52.7 GB/day
        total_cctv_tb = round((cameras * gb_per_camera_day * retention_days) / 1024 * 1.25, 1) # 25% RAID overhead

        # 7. Bill of Materials (BOM) & Budgetary Cost
        bom = []
        bom.append({'item': 'Enterprise Core/Edge Router', 'qty': 1, 'unit_cost': cls.UNIT_ESTIMATES['router_enterprise'], 'total': cls.UNIT_ESTIMATES['router_enterprise']})
        if switches_48p > 0:
            bom.append({'item': '48-Port Managed PoE+ Switch', 'qty': switches_48p, 'unit_cost': cls.UNIT_ESTIMATES['switch_48p_poe'], 'total': switches_48p * cls.UNIT_ESTIMATES['switch_48p_poe']})
        if switches_24p > 0:
            bom.append({'item': '24-Port Managed PoE+ Switch', 'qty': switches_24p, 'unit_cost': cls.UNIT_ESTIMATES['switch_24p_poe'], 'total': switches_24p * cls.UNIT_ESTIMATES['switch_24p_poe']})
        if access_points > 0:
            bom.append({'item': 'Enterprise Wi-Fi 6 Access Point', 'qty': access_points, 'unit_cost': cls.UNIT_ESTIMATES['access_point_wifi6'], 'total': access_points * cls.UNIT_ESTIMATES['access_point_wifi6']})
        if patch_panels_needed > 0:
            bom.append({'item': 'Cat6 24-Port 1U Patch Panel', 'qty': patch_panels_needed, 'unit_cost': cls.UNIT_ESTIMATES['patch_panel_24p'], 'total': patch_panels_needed * cls.UNIT_ESTIMATES['patch_panel_24p']})
        
        cable_boxes = max(2, (total_endpoints + 9) // 10)
        bom.append({'item': 'Cat6 UTP 1000ft Bulk Cable Spool', 'qty': cable_boxes, 'unit_cost': cls.UNIT_ESTIMATES['cat6_box_1000ft'], 'total': cable_boxes * cls.UNIT_ESTIMATES['cat6_box_1000ft']})

        rack_cost = cls.UNIT_ESTIMATES['rack_enclosure_42u'] if '42U' in recommended_rack else cls.UNIT_ESTIMATES['rack_enclosure_24u']
        bom.append({'item': recommended_rack, 'qty': 1, 'unit_cost': rack_cost, 'total': rack_cost})

        ups_cost = cls.UNIT_ESTIMATES['ups_3000va_rack'] if '3000VA' in recommended_ups else cls.UNIT_ESTIMATES['ups_1500va_rack']
        bom.append({'item': recommended_ups, 'qty': 1, 'unit_cost': ups_cost, 'total': ups_cost})

        storage_cost = round(total_cctv_tb * cls.UNIT_ESTIMATES['nvr_storage_server_tb'], 2)
        bom.append({'item': f"Surveillance Enterprise Storage ({total_cctv_tb} TB RAID)", 'qty': 1, 'unit_cost': storage_cost, 'total': storage_cost})

        total_capex = round(sum(b['total'] for b in bom), 2)

        return {
            'inputs': {
                'total_endpoints': total_endpoints,
                'workstations': workstations,
                'voip_phones': voip_phones,
                'cameras': cameras,
                'access_points': access_points,
                'servers': servers,
                'retention_days': retention_days
            },
            'port_density': {
                'ports_needed_with_growth': total_ports_needed,
                'total_switch_ports_provisioned': total_switch_ports,
                'spare_ports': total_switch_ports - total_endpoints,
                'switches_48p': switches_48p,
                'switches_24p': switches_24p,
                'total_switches': total_switches
            },
            'poe_budget': {
                'total_watts_required': total_poe_watts,
                'recommended_psu_watts': poe_budget_with_margin,
                'voip_watts': poe_watts_voip,
                'cctv_watts': poe_watts_cctv,
                'ap_watts': poe_watts_ap
            },
            'rack_thermal': {
                'total_rack_u_occupied': total_rack_u,
                'recommended_rack': recommended_rack,
                'total_system_watts': round(total_system_watts, 1),
                'total_btu_hr': total_btu_hr
            },
            'ups_storage': {
                'recommended_va': total_va,
                'recommended_ups': recommended_ups,
                'cctv_storage_tb': total_cctv_tb
            },
            'budgetary_bom': {
                'items': bom,
                'total_estimated_capex': total_capex,
                'disclaimer': 'DISCLAIMER: All pricing figures are budgetary planning estimates. Actual vendor quotations, licensing, tax, shipping, and installation labor will vary based on geographic region and procurement agreements.'
            }
        }
