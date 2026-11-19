"""
Ramonet Multi-Platform CLI Simulation Engine
Executes commands against simulated device state, mutating configuration in real-time.
Maintains stateful interactive sessions across Cisco IOS, Windows CMD, Linux Shell, and MikroTik.
"""
import re
import ipaddress
from typing import Dict, Any, Tuple, List, Optional
from simulation.engine import NetworkSimulationEngine


def normalize_interface_name(name: str) -> str:
    """Normalize user interface shorthand like g0/0 -> GigabitEthernet0/0, fa0/1 -> FastEthernet0/1."""
    n = name.strip()
    low = n.lower()
    if low.startswith(('gigabitethernet', 'gig', 'gi')):
        suffix = re.sub(r'^[a-z]+', '', low)
        return f"GigabitEthernet{suffix}"
    elif low.startswith(('fastethernet', 'fa')):
        suffix = re.sub(r'^[a-z]+', '', low)
        return f"FastEthernet{suffix}"
    elif low.startswith(('ethernet', 'eth')):
        suffix = re.sub(r'^[a-z]+', '', low)
        return f"Ethernet{suffix}"
    elif low.startswith(('serial', 'se')):
        suffix = re.sub(r'^[a-z]+', '', low)
        return f"Serial{suffix}"
    elif low.startswith(('loopback', 'lo')):
        suffix = re.sub(r'^[a-z]+', '', low)
        return f"Loopback{suffix}"
    elif low.startswith('vlan'):
        suffix = re.sub(r'^[a-z]+', '', low)
        return f"Vlan{suffix}"
    return n


class DeviceCLISession:
    def __init__(self, device_data: Dict[str, Any], topology_data: Optional[Dict[str, Any]] = None, session_state: Optional[Dict[str, Any]] = None):
        self.device = device_data
        self.topology = topology_data or {'devices': [self.device], 'connections': []}
        self.platform = self.device.get('cli_platform', 'cisco_ios')
        
        # State tracking for Cisco IOS
        session_state = session_state or self.device.get('cli_session_state', {})
        self.mode = session_state.get('mode', 'user_exec')  # 'user_exec', 'priv_exec', 'global_config', 'interface_config', 'vlan_config', 'router_config'
        self.current_interface = session_state.get('current_interface')
        self.current_vlan = session_state.get('current_vlan')
        self.current_router_proto = session_state.get('current_router_proto')
        
        # Linux / Windows tracking
        self.working_dir = session_state.get('working_dir', '/home/admin' if self.platform == 'linux_shell' else r'C:\Users\Admin')

    def get_session_state(self) -> Dict[str, Any]:
        return {
            'mode': self.mode,
            'current_interface': self.current_interface,
            'current_vlan': self.current_vlan,
            'current_router_proto': self.current_router_proto,
            'working_dir': self.working_dir,
        }

    def get_prompt(self) -> str:
        hostname = self.device.get('name', 'Device')
        
        if self.platform == 'cisco_ios':
            if self.mode == 'user_exec':
                return f"{hostname}>"
            elif self.mode == 'priv_exec':
                return f"{hostname}#"
            elif self.mode == 'global_config':
                return f"{hostname}(config)#"
            elif self.mode == 'interface_config':
                return f"{hostname}(config-if)#{self.current_interface or ''}"
            elif self.mode == 'vlan_config':
                return f"{hostname}(config-vlan)#{self.current_vlan or ''}"
            elif self.mode == 'router_config':
                return f"{hostname}(config-router)#"
            return f"{hostname}#"
            
        elif self.platform == 'linux_shell':
            return f"admin@{hostname.lower()}:~$ "
            
        elif self.platform == 'windows_cmd':
            return rf"C:\Users\Admin> "
            
        elif self.platform == 'mikrotik':
            return f"[{self.device.get('name', 'admin')}@MikroTik] > "
            
        return f"{hostname}> "

    def execute(self, cmd_line: str) -> Dict[str, Any]:
        raw_cmd = cmd_line.strip()
        if not raw_cmd:
            return {
                'output': '',
                'prompt': self.get_prompt(),
                'mode': self.mode,
                'session_state': self.get_session_state(),
                'device': self.device
            }

        # Check platform
        if self.platform == 'cisco_ios':
            res = self._execute_cisco(raw_cmd)
        elif self.platform == 'linux_shell':
            res = self._execute_linux(raw_cmd)
        elif self.platform == 'windows_cmd':
            res = self._execute_windows(raw_cmd)
        elif self.platform == 'mikrotik':
            res = self._execute_mikrotik(raw_cmd)
        else:
            res = self._execute_web_gui(raw_cmd)

        res.setdefault('session_state', self.get_session_state())
        res.setdefault('mode', self.mode)
        res.setdefault('prompt', self.get_prompt())
        res.setdefault('device', self.device)
        return res

    # ================= CISCO IOS ENGINE =================
    def _execute_cisco(self, cmd: str) -> Dict[str, Any]:
        parts = cmd.split()
        first = parts[0].lower()
        output = ""

        # Context-sensitive help '?'
        if cmd == '?' or cmd.endswith('?'):
            return self._cisco_help(cmd)

        # Mode navigation: exit / end / disable / quit
        if first in ('exit', 'quit'):
            if self.mode in ('interface_config', 'vlan_config', 'router_config'):
                self.mode = 'global_config'
                self.current_interface = None
                self.current_vlan = None
            elif self.mode == 'global_config':
                self.mode = 'priv_exec'
            elif self.mode == 'priv_exec':
                self.mode = 'user_exec'
            return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'end':
            if self.mode != 'user_exec':
                self.mode = 'priv_exec'
                self.current_interface = None
                self.current_vlan = None
            return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first in ('enable', 'en'):
            self.mode = 'priv_exec'
            return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'disable':
            self.mode = 'user_exec'
            return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        # Handle 'do <command>' from config modes
        if first == 'do' and len(parts) > 1:
            sub_cmd = " ".join(parts[1:])
            saved_mode = self.mode
            self.mode = 'priv_exec'
            res = self._execute_cisco(sub_cmd)
            self.mode = saved_mode
            res['prompt'] = self.get_prompt()
            res['mode'] = self.mode
            res['session_state'] = self.get_session_state()
            return res

        # Configuration Mode Entry
        if first in ('configure', 'conf', 'config'):
            if len(parts) > 1 and parts[1].lower().startswith('t'):
                if self.mode in ('priv_exec', 'global_config', 'interface_config', 'vlan_config'):
                    self.mode = 'global_config'
                    output = "Enter configuration commands, one per line. End with CNTL/Z or 'end'."
                    return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}
                else:
                    return {'output': "% Command requires privileged mode.", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}
            elif self.mode in ('priv_exec', 'global_config'):
                self.mode = 'global_config'
                output = "Configuring from terminal, memory, or network [terminal]? \nEnter configuration commands, one per line. End with CNTL/Z or 'end'."
                return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        # Write memory / save config
        if first in ('write', 'wr') or (first == 'copy' and len(parts) >= 3 and parts[1].startswith('run') and parts[2].startswith('start')):
            output = "Building configuration...\n[OK]\nConfiguration saved to NVRAM."
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        # Global config commands
        if self.mode == 'global_config':
            if first in ('hostname', 'host') and len(parts) > 1:
                self.device['name'] = parts[1]
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

            if (first in ('interface', 'int')) and len(parts) > 1:
                iface_arg = parts[1]
                norm_name = normalize_interface_name(iface_arg)
                
                # Match or create interface
                match_iface = None
                for ifc in self.device.setdefault('interfaces', []):
                    if ifc.get('name', '').lower() == iface_arg.lower() or ifc.get('name', '').lower() == norm_name.lower():
                        match_iface = ifc
                        break
                if not match_iface:
                    match_iface = {'name': norm_name, 'status': 'up', 'ip': '', 'mask': ''}
                    self.device['interfaces'].append(match_iface)
                self.current_interface = match_iface['name']
                self.mode = 'interface_config'
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

            if first == 'vlan' and len(parts) > 1:
                vlan_id = parts[1]
                self.device.setdefault('vlans', {})
                if vlan_id not in self.device['vlans']:
                    self.device['vlans'][vlan_id] = {'name': f"VLAN{vlan_id}", 'ports': []}
                self.current_vlan = vlan_id
                self.mode = 'vlan_config'
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

            if first == 'ip' and len(parts) >= 4 and parts[1].lower() == 'route':
                net = parts[2]
                mask = parts[3]
                gw = parts[4] if len(parts) > 4 else ''
                self.device.setdefault('routes', [])
                self.device['routes'].append({'network': net, 'mask': mask, 'gateway': gw, 'type': 'static'})
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

            if first == 'no' and len(parts) >= 5 and parts[1].lower() == 'ip' and parts[2].lower() == 'route':
                net = parts[3]
                mask = parts[4]
                self.device['routes'] = [r for r in self.device.get('routes', []) if not (r.get('network') == net and r.get('mask') == mask)]
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

            if first == 'router' and len(parts) > 1:
                self.current_router_proto = " ".join(parts[1:])
                self.mode = 'router_config'
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        # Interface config commands
        if self.mode == 'interface_config':
            curr_iface = None
            for ifc in self.device.get('interfaces', []):
                if ifc.get('name') == self.current_interface:
                    curr_iface = ifc
                    break

            if curr_iface is not None:
                if first == 'ip' and len(parts) >= 4 and parts[1].lower() in ('address', 'addr'):
                    ip_val = parts[2]
                    mask_val = parts[3]
                    curr_iface['ip'] = ip_val
                    curr_iface['mask'] = mask_val
                    if not self.device.get('ip') or self.device.get('ip') == '0.0.0.0':
                        self.device['ip'] = ip_val
                        self.device['subnet_mask'] = mask_val
                    return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

                if first == 'no' and len(parts) > 1 and parts[1].lower() in ('shutdown', 'shut'):
                    curr_iface['status'] = 'up'
                    return {'output': f"% Interface {self.current_interface}, changed state to up\n% LINEPROTO-5-UPDOWN: Line protocol on Interface {self.current_interface}, changed state to up", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

                if first in ('shutdown', 'shut'):
                    curr_iface['status'] = 'administratively_down'
                    return {'output': f"% Interface {self.current_interface}, changed state to administratively down", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

                if first in ('description', 'desc') and len(parts) > 1:
                    curr_iface['description'] = " ".join(parts[1:])
                    return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

                if first == 'switchport':
                    if len(parts) >= 3 and parts[1].lower() == 'mode':
                        curr_iface['mode'] = parts[2].lower()
                        return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}
                    elif len(parts) >= 4 and parts[1].lower() == 'access' and parts[2].lower() == 'vlan':
                        curr_iface['vlan'] = int(parts[3])
                        return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}
                    elif len(parts) >= 5 and parts[1].lower() == 'trunk' and parts[2].lower() == 'allowed':
                        curr_iface['allowed_vlans'] = parts[4]
                        return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        # VLAN config mode
        if self.mode == 'vlan_config':
            if first == 'name' and len(parts) > 1:
                vlan_name = " ".join(parts[1:])
                if self.current_vlan and self.current_vlan in self.device.get('vlans', {}):
                    self.device['vlans'][self.current_vlan]['name'] = vlan_name
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        # Router config mode
        if self.mode == 'router_config':
            if first == 'network' and len(parts) >= 2:
                net_info = " ".join(parts[1:])
                self.device.setdefault('routing_protocols', {})
                self.device['routing_protocols'].setdefault(self.current_router_proto or 'ospf', []).append(net_info)
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}
            if first == 'version' and len(parts) > 1:
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        # Show commands (available in priv_exec and user_exec)
        if first in ('show', 'sh'):
            return self._cisco_show(parts)

        # Ping command
        if first == 'ping' and len(parts) > 1:
            target_ip = parts[1]
            return self._cisco_ping(target_ip)

        # Traceroute command
        if first in ('traceroute', 'tracert') and len(parts) > 1:
            target_ip = parts[1]
            return self._cisco_traceroute(target_ip)

        # Default fallback
        return {
            'output': f"% Invalid input detected at '{cmd}'. Type '?' for available commands.",
            'prompt': self.get_prompt(),
            'mode': self.mode,
            'device': self.device
        }

    def _cisco_show(self, parts: List[str]) -> Dict[str, Any]:
        sub = " ".join(parts[1:]).lower()
        hostname = self.device.get('name', 'Router')

        if any(k in sub for k in ('ip interface brief', 'ip int br', 'ip int brief')):
            lines = [
                "Interface              IP-Address      OK? Method Status                Protocol",
                "--------------------------------------------------------------------------------"
            ]
            for ifc in self.device.get('interfaces', []):
                name = ifc.get('name', 'eth0').ljust(22)
                ip = (ifc.get('ip') or 'unassigned').ljust(15)
                status = ifc.get('status', 'up')
                stat_str = "up".ljust(21) if status == 'up' else "administratively down"
                proto_str = "up" if status == 'up' else "down"
                lines.append(f"{name} {ip} YES manual {stat_str} {proto_str}")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if any(k in sub for k in ('ip route', 'ip ro')):
            lines = [
                "Codes: L - local, C - connected, S - static, R - RIP, O - OSPF, B - BGP",
                "Gateway of last resort is not set",
                ""
            ]
            for ifc in self.device.get('interfaces', []):
                if ifc.get('ip') and ifc.get('mask'):
                    try:
                        net = ipaddress.IPv4Network(f"{ifc['ip']}/{ifc['mask']}", strict=False)
                        lines.append(f"C    {net} is directly connected, {ifc.get('name')}")
                        lines.append(f"L    {ifc['ip']}/32 is directly connected, {ifc.get('name')}")
                    except Exception:
                        pass
            for r in self.device.get('routes', []):
                lines.append(f"S    {r.get('network')}/{r.get('mask')} [1/0] via {r.get('gateway', '0.0.0.0')}")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if 'vlan' in sub:
            lines = [
                "VLAN Name                             Status    Ports",
                "---- -------------------------------- --------- -------------------------------",
                "1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4"
            ]
            vlans = self.device.get('vlans', {})
            for vid, vinfo in vlans.items():
                vname = vinfo.get('name', f'VLAN{vid}').ljust(32)
                lines.append(f"{str(vid).ljust(4)} {vname} active    Fa0/5, Fa0/6")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if any(k in sub for k in ('mac address-table', 'mac-address-table', 'mac')):
            lines = [
                "          Mac Address Table",
                "-------------------------------------------",
                "Vlan    Mac Address       Type        Ports",
                "----    -----------       --------    -----",
                "   1    0014.2201.2341    DYNAMIC     Fa0/1",
                "   1    0014.2201.5582    DYNAMIC     Fa0/2"
            ]
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if any(k in sub for k in ('running-config', 'run')):
            lines = [
                f"! Running configuration of {hostname}",
                f"hostname {hostname}",
                "!"
            ]
            for ifc in self.device.get('interfaces', []):
                lines.append(f"interface {ifc.get('name')}")
                if ifc.get('ip') and ifc.get('mask'):
                    lines.append(f" ip address {ifc.get('ip')} {ifc.get('mask')}")
                if ifc.get('status') == 'administratively_down':
                    lines.append(" shutdown")
                else:
                    lines.append(" no shutdown")
                if ifc.get('mode'):
                    lines.append(f" switchport mode {ifc.get('mode')}")
                if ifc.get('vlan'):
                    lines.append(f" switchport access vlan {ifc.get('vlan')}")
                lines.append("!")
            for r in self.device.get('routes', []):
                lines.append(f"ip route {r.get('network')} {r.get('mask')} {r.get('gateway')}")
            lines.append("end")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if 'version' in sub:
            output = f"Cisco IOS Software, RAMONET-SIM Version 15.7(3)M4, RELEASE SOFTWARE (fc2)\nTechnical Support: https://github.com/im-Abhiram/toolramo\nSystem uptime is 14 days, 6 hours, 22 minutes\nModel: {self.device.get('model_name', 'Cisco Catalyst')}\nBase Ethernet MAC Address: 00:1A:E2:4B:92:00"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if 'interfaces' in sub or 'int' in sub:
            lines = []
            for ifc in self.device.get('interfaces', []):
                lines.append(f"{ifc.get('name')} is {ifc.get('status', 'up')}, line protocol is {ifc.get('status', 'up')}")
                lines.append(f"  Hardware is Built-in Ethernet, address is 001a.e24b.9201")
                if ifc.get('ip'):
                    lines.append(f"  Internet address is {ifc.get('ip')}/{ifc.get('mask', '24')}")
                lines.append(f"  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec")
                lines.append("")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        return {'output': f"% Unrecognized command 'show {sub}'", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

    def _cisco_ping(self, target_ip: str) -> Dict[str, Any]:
        engine = NetworkSimulationEngine(self.topology)
        dev_id = str(self.device.get('id', ''))
        result = engine.simulate_packet(dev_id, target_ip, protocol='ICMP')
        
        if result['success']:
            output = (
                f"Type escape sequence to abort.\n"
                f"Sending 5, 100-byte ICMP Echos to {target_ip}, timeout is 2 seconds:\n"
                f"!!!!!\n"
                f"Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms"
            )
        else:
            reason = result.get('drop_reason', 'DESTINATION_UNREACHABLE')
            details = result.get('details', '')
            output = (
                f"Type escape sequence to abort.\n"
                f"Sending 5, 100-byte ICMP Echos to {target_ip}, timeout is 2 seconds:\n"
                f".....\n"
                f"Success rate is 0 percent (0/5)\n"
                f"% Ping failed: {reason} {details}"
            )
        return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'simulation_result': result}

    def _cisco_traceroute(self, target_ip: str) -> Dict[str, Any]:
        engine = NetworkSimulationEngine(self.topology)
        dev_id = str(self.device.get('id', ''))
        result = engine.simulate_packet(dev_id, target_ip, protocol='ICMP')
        
        lines = [f"Type escape sequence to abort.\nTracing the route to {target_ip}"]
        hop_num = 1
        for h in result.get('hops', []):
            if h.get('action') in ('ROUTE_FORWARD', 'FRAME_TRANSIT', 'PACKET_RECEIVED_BY_DESTINATION'):
                dev_name = h.get('device_name', 'Hop')
                ip = h.get('dest_ip') or h.get('src_ip')
                lines.append(f"  {hop_num}  {dev_name} ({ip})  2 msec  2 msec  1 msec")
                hop_num += 1

        if not result['success']:
            lines.append(f"  {hop_num}  * * * Destination unreachable ({result.get('drop_reason')})")

        return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

    def _cisco_help(self, cmd: str) -> Dict[str, Any]:
        if self.mode == 'user_exec':
            help_text = (
                "Exec commands:\n"
                "  enable             Turn on privileged commands\n"
                "  ping               Send ICMP echo messages\n"
                "  show               Show running system information\n"
                "  traceroute         Trace route to destination\n"
                "  exit               Exit from the EXEC"
            )
        elif self.mode == 'priv_exec':
            help_text = (
                "Exec commands:\n"
                "  configure          Enter configuration mode\n"
                "  disable            Turn off privileged commands\n"
                "  ping               Send ICMP echo messages\n"
                "  show               Show running system information\n"
                "  traceroute         Trace route to destination\n"
                "  write              Write running configuration to memory\n"
                "  exit               Exit from the EXEC"
            )
        elif self.mode == 'global_config':
            help_text = (
                "Configure commands:\n"
                "  hostname           Set system network name\n"
                "  interface          Select an interface to configure\n"
                "  ip                 Global IP configuration subcommands\n"
                "  vlan               VLAN configuration\n"
                "  router             Enable a routing process (OSPF, RIP)\n"
                "  do                 Execute an EXEC-level command\n"
                "  end                Exit from configure mode\n"
                "  exit               Exit from configure mode"
            )
        elif self.mode == 'interface_config':
            help_text = (
                "Interface configuration commands:\n"
                "  ip address         Set for an interface an IP address\n"
                "  shutdown           Shut down the selected interface\n"
                "  no shutdown        Enable the selected interface\n"
                "  switchport mode    Set trunk or access mode for port\n"
                "  switchport access  Set VLAN for access port\n"
                "  description        Interface specific description\n"
                "  do                 Execute an EXEC-level command\n"
                "  exit               Exit from interface configuration mode"
            )
        else:
            help_text = "Commands: name, exit, end"

        return {'output': help_text, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

    # ================= LINUX ENGINE =================
    def _execute_linux(self, cmd: str) -> Dict[str, Any]:
        parts = cmd.split()
        first = parts[0].lower()
        
        if first in ('ip', 'ifconfig'):
            if first == 'ifconfig' or (len(parts) > 1 and parts[1] in ('a', 'addr', 'address')):
                lines = []
                for ifc in self.device.get('interfaces', []):
                    name = ifc.get('name', 'eth0')
                    ip = ifc.get('ip') or self.device.get('ip', '192.168.1.10')
                    mask = ifc.get('mask') or self.device.get('subnet_mask', '255.255.255.0')
                    lines.append(f"{name}: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500")
                    lines.append(f"        inet {ip}  netmask {mask}  broadcast 192.168.1.255")
                    lines.append(f"        ether 02:42:c0:a8:01:0a  txqueuelen 1000  (Ethernet)")
                    lines.append(f"        RX packets 1042  bytes 84520 (84.5 KB)")
                    lines.append(f"        TX packets 890  bytes 72100 (72.1 KB)")
                    lines.append("")
                return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}
            elif len(parts) > 1 and parts[1] == 'route':
                lines = [
                    f"default via {self.device.get('gateway', '192.168.1.1')} dev eth0 proto dhcp metric 100",
                    f"{self.device.get('ip', '192.168.1.0')}/24 dev eth0 proto kernel scope link src {self.device.get('ip', '192.168.1.10')} metric 100"
                ]
                return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'route':
            lines = [
                "Kernel IP routing table",
                "Destination     Gateway         Genmask         Flags Metric Ref    Use Iface",
                f"0.0.0.0         {self.device.get('gateway', '192.168.1.1')}     0.0.0.0         UG    100    0        0 eth0",
                f"192.168.1.0     0.0.0.0         255.255.255.0   U     100    0        0 eth0"
            ]
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'ping' and len(parts) > 1:
            target = parts[-1]
            engine = NetworkSimulationEngine(self.topology)
            res = engine.simulate_packet(str(self.device.get('id', '')), target, protocol='ICMP')
            if res['success']:
                output = (
                    f"PING {target} ({target}) 56(84) bytes of data.\n"
                    f"64 bytes from {target}: icmp_seq=1 ttl=64 time=0.452 ms\n"
                    f"64 bytes from {target}: icmp_seq=2 ttl=64 time=0.381 ms\n"
                    f"64 bytes from {target}: icmp_seq=3 ttl=64 time=0.410 ms\n"
                    f"--- {target} ping statistics ---\n"
                    f"3 packets transmitted, 3 received, 0% packet loss, time 2004ms"
                )
            else:
                output = f"PING {target} ({target}) 56(84) bytes of data.\nFrom {self.device.get('ip', 'host')} icmp_seq=1 Destination Host Unreachable: {res.get('drop_reason', 'UNREACHABLE')}"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first in ('traceroute', 'tracepath') and len(parts) > 1:
            target = parts[-1]
            engine = NetworkSimulationEngine(self.topology)
            res = engine.simulate_packet(str(self.device.get('id', '')), target, protocol='ICMP')
            lines = [f"traceroute to {target} ({target}), 30 hops max, 60 byte packets"]
            for idx, h in enumerate(res.get('hops', []), start=1):
                lines.append(f" {idx}  {h.get('device_name', 'node')} ({h.get('dest_ip', target)})  0.412 ms  0.380 ms")
            if not res['success']:
                lines.append(f" * * * Destination unreachable")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'arp' or (first == 'ip' and len(parts) > 1 and parts[1].startswith('n')):
            lines = [
                "Address                  HWtype  HWaddress           Flags Mask            Iface",
                f"{self.device.get('gateway', '192.168.1.1')}          ether   00:1a:2b:3c:4d:5e   C                     eth0"
            ]
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first in ('netstat', 'ss'):
            lines = [
                "Active Internet connections (only servers)",
                "Proto Recv-Q Send-Q Local Address           Foreign Address         State",
                "tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN",
                "tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN",
                "udp        0      0 0.0.0.0:68              0.0.0.0:*               "
            ]
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'hostname':
            return {'output': self.device.get('name', 'server'), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'uname':
            return {'output': 'Linux ramonet-node 5.15.0-generic #1 SMP x86_64 GNU/Linux', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'help':
            return {
                'output': "Available Linux commands: ip addr, ifconfig, ip route, ping, traceroute, arp, netstat, ss, hostname, uname, clear",
                'prompt': self.get_prompt(),
                'mode': self.mode,
                'device': self.device
            }

        return {'output': f"admin@server:~$ {cmd}: command executed.", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

    # ================= WINDOWS ENGINE =================
    def _execute_windows(self, cmd: str) -> Dict[str, Any]:
        parts = cmd.split()
        first = parts[0].lower()

        if first == 'ipconfig':
            is_all = '/all' in cmd.lower()
            lines = [
                "Windows IP Configuration",
                "",
                "Ethernet adapter Ethernet0:",
                "   Connection-specific DNS Suffix  . : localdomain",
                f"   IPv4 Address. . . . . . . . . . . : {self.device.get('ip', '192.168.1.50')}",
                f"   Subnet Mask . . . . . . . . . . . : {self.device.get('subnet_mask', '255.255.255.0')}",
                f"   Default Gateway . . . . . . . . . : {self.device.get('gateway', '192.168.1.1')}"
            ]
            if is_all:
                lines.insert(3, f"   Host Name . . . . . . . . . . . . : {self.device.get('name', 'PC-1')}")
                lines.insert(4, "   Primary Dns Suffix  . . . . . . . : ")
                lines.insert(5, "   Node Type . . . . . . . . . . . . : Hybrid")
                lines.append(f"   Physical Address. . . . . . . . . : 00-50-56-C0-00-08")
                lines.append(f"   DHCP Enabled. . . . . . . . . . . : {'No' if self.device.get('ip') else 'Yes'}")
                lines.append(f"   DNS Servers . . . . . . . . . . . : {self.device.get('dns', '8.8.8.8')}")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'ping' and len(parts) > 1:
            target = parts[1]
            engine = NetworkSimulationEngine(self.topology)
            res = engine.simulate_packet(str(self.device.get('id', '')), target, protocol='ICMP')
            if res['success']:
                output = (
                    f"Pinging {target} with 32 bytes of data:\n"
                    f"Reply from {target}: bytes=32 time<1ms TTL=128\n"
                    f"Reply from {target}: bytes=32 time=1ms TTL=128\n"
                    f"Reply from {target}: bytes=32 time=1ms TTL=128\n"
                    f"Reply from {target}: bytes=32 time=1ms TTL=128\n\n"
                    f"Ping statistics for {target}:\n"
                    f"    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),\n"
                    f"Approximate round trip times in milli-seconds:\n"
                    f"    Minimum = 0ms, Maximum = 1ms, Average = 0ms"
                )
            else:
                reason = res.get('drop_reason', 'Destination host unreachable')
                output = f"Pinging {target} with 32 bytes of data:\nReply from {self.device.get('ip', '127.0.0.1')}: Destination host unreachable ({reason}).\n\nPing statistics for {target}:\n    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first in ('tracert', 'traceroute') and len(parts) > 1:
            target = parts[1]
            engine = NetworkSimulationEngine(self.topology)
            res = engine.simulate_packet(str(self.device.get('id', '')), target, protocol='ICMP')
            lines = [
                f"Tracing route to {target} over a maximum of 30 hops:",
                ""
            ]
            for idx, h in enumerate(res.get('hops', []), start=1):
                lines.append(f"  {idx}     1 ms    <1 ms    <1 ms  {h.get('device_name', 'gateway')} [{h.get('dest_ip', target)}]")
            if not res['success']:
                lines.append(f"  *     *     *     Request timed out ({res.get('drop_reason', 'UNREACHABLE')}).")
            lines.append("\nTrace complete.")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'arp' and len(parts) > 1 and '-a' in parts:
            lines = [
                f"Interface: {self.device.get('ip', '192.168.1.50')} --- 0xb",
                "  Internet Address      Physical Address      Type",
                f"  {self.device.get('gateway', '192.168.1.1')}         00-1a-2b-3c-4d-5e     dynamic",
                "  192.168.1.255         ff-ff-ff-ff-ff-ff     static",
                "  224.0.0.22            01-00-5e-00-00-16     static"
            ]
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'route' and len(parts) > 1 and parts[1].lower() == 'print':
            lines = [
                "IPv4 Route Table",
                "===========================================================================",
                "Active Routes:",
                "Network Destination        Netmask          Gateway       Interface  Metric",
                f"          0.0.0.0          0.0.0.0      {self.device.get('gateway', '192.168.1.1')}    {self.device.get('ip', '192.168.1.50')}     25",
                f"      192.168.1.0    255.255.255.0         On-link     {self.device.get('ip', '192.168.1.50')}    281"
            ]
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'hostname':
            return {'output': self.device.get('name', 'PC-Workstation'), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first == 'nslookup' and len(parts) > 1:
            domain = parts[1]
            output = f"Server:  dns.google\nAddress:  {self.device.get('dns', '8.8.8.8')}\n\nNon-authoritative answer:\nName:    {domain}\nAddress: 93.184.216.34"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first in ('help', '?'):
            return {
                'output': "Available Windows Commands:\n  ipconfig [/all]     Display IP and network adapter configuration\n  ping <ip>           Verify network connectivity to destination\n  tracert <ip>        Trace network hops to destination\n  arp -a              Display ARP cache and MAC table\n  route print         Display local routing table\n  hostname            Print workstation name\n  nslookup <host>     Query DNS server\n  cls                 Clear screen",
                'prompt': self.get_prompt(),
                'mode': self.mode,
                'device': self.device
            }

        return {'output': f"'{cmd}' is recognized as an internal command.", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

    # ================= MIKROTIK ENGINE =================
    def _execute_mikrotik(self, cmd: str) -> Dict[str, Any]:
        if 'address print' in cmd:
            output = f"Flags: X - disabled, I - invalid, D - dynamic \n #   ADDRESS            NETWORK         INTERFACE\n 0   {self.device.get('ip', '192.168.88.1')}/24   192.168.88.0    ether1"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}
        if 'ping' in cmd:
            parts = cmd.split()
            target = parts[-1]
            engine = NetworkSimulationEngine(self.topology)
            res = engine.simulate_packet(str(self.device.get('id', '')), target, protocol='ICMP')
            output = f"  SEQ HOST                                     SIZE TTL TIME  STATUS\n    0 {target}                                 56  64 1ms\n    1 {target}                                 56  64 1ms\n    sent=2 received=2 packet-loss=0% min-rtt=1ms avg-rtt=1ms max-rtt=1ms" if res['success'] else f"  sent=2 received=0 packet-loss=100% ({res.get('drop_reason', 'timeout')})"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}
        return {'output': f"[MikroTik RouterOS] Command '{cmd}' executed.", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

    # ================= WEB GUI / GENERIC APPLIANCE SHELL =================
    def _execute_web_gui(self, cmd: str) -> Dict[str, Any]:
        parts = cmd.split()
        first = parts[0].lower()

        if first == 'ping' and len(parts) > 1:
            target = parts[1]
            engine = NetworkSimulationEngine(self.topology)
            res = engine.simulate_packet(str(self.device.get('id', '')), target, protocol='ICMP')
            status_text = "5 packets transmitted, 5 received, 0% packet loss" if res['success'] else f"5 packets transmitted, 0 received, 100% packet loss ({res.get('drop_reason')})"
            output = f"Diagnostics: PING {target}\n{status_text}"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first in ('status', 'info', 'show'):
            output = f"Device: {self.device.get('name')}\nModel: {self.device.get('model_name', 'Network Appliance')}\nManagement IP: {self.device.get('ip', '192.168.1.200')}\nSubnet: {self.device.get('subnet_mask', '255.255.255.0')}\nGateway: {self.device.get('gateway', '192.168.1.1')}\nState: Operational"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first in ('ipconfig', 'ifconfig'):
            output = f"Interface: eth0\n  IPv4: {self.device.get('ip', '192.168.1.200')}\n  Mask: {self.device.get('subnet_mask', '255.255.255.0')}\n  Gateway: {self.device.get('gateway', '192.168.1.1')}"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        if first in ('help', '?'):
            output = f"Appliance Management Console ({self.device.get('name')}):\n  status       Display device operational status and IP\n  ping <ip>    Test connectivity to another device\n  ipconfig     Display network parameters\n  reboot       Simulate appliance restart"
            return {'output': output, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device}

        return {
            'output': f"Appliance console: '{cmd}' executed. (Primary configuration is via Web Admin GUI). Type 'help' for diagnostics.",
            'prompt': self.get_prompt(),
            'mode': self.mode,
            'device': self.device
        }
