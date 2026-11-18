"""
Ramonet Core - Unified Command Parser & Executor
Authoritative multi-platform CLI engine executing real mutations on the device configuration state.
"""
from typing import Dict, Any, Tuple, List, Optional
import re
from .device_config import DeviceConfigurationService

class CommandParser:
    """Parses and normalizes command strings across platforms."""

    @classmethod
    def tokenize(cls, command_str: str) -> List[str]:
        return [part for part in command_str.strip().split() if part]


class CommandExecutor:
    """Executes validated commands directly mutating the authoritative device state."""

    def __init__(self, device_data: Dict[str, Any], topology_data: Optional[Dict[str, Any]] = None, platform: Optional[str] = None):
        self.config_service = DeviceConfigurationService(device_data)
        self.device = self.config_service.device
        self.topology = topology_data or {'devices': [self.device], 'connections': []}
        self.platform = platform or self.device.get('cli_platform', 'cisco_ios')

        # Session mode state
        self.mode = 'priv_exec' if self.platform == 'cisco_ios' else 'user_exec'
        self.current_interface = None
        self.current_vlan = None

    def get_prompt(self) -> str:
        hostname = self.config_service.name

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
            return f"{hostname}#"
        elif self.platform == 'linux_shell':
            return f"admin@{hostname.lower()}:~$ "
        elif self.platform == 'windows_cmd':
            return r"C:\Users\Admin> "
        elif self.platform == 'mikrotik':
            return f"[{hostname}@MikroTik] > "
        return f"{hostname}> "

    @classmethod
    def execute(cls, *args, **kwargs) -> Dict[str, Any]:
        """
        Executes a command.
        Supports both instance call: `executor.execute('vlan 10')`
        and static/class call: `CommandExecutor.execute(device_dict, 'vlan 10', platform='cisco_ios')`.
        """
        if len(args) >= 1 and isinstance(args[0], CommandExecutor):
            executor = args[0]
            cmd_line = args[1] if len(args) > 1 else kwargs.get('cmd_line', '')
        else:
            # Called as CommandExecutor.execute(device_data, cmd_line, platform=...)
            device_data = args[0]
            cmd_line = args[1] if len(args) > 1 else kwargs.get('cmd_line', '')
            platform = kwargs.get('platform') or (args[2] if len(args) > 2 else None)
            executor = CommandExecutor(device_data, platform=platform)
            # Headless execution starts in global_config for instant syntax configuration
            executor.mode = 'global_config'

        raw_cmd = str(cmd_line).strip()
        if not raw_cmd:
            return {
                'success': True,
                'output': '',
                'prompt': executor.get_prompt(),
                'mode': executor.mode,
                'device': executor.device,
                'mutated': False
            }

        res = None
        if executor.platform == 'cisco_ios':
            res = executor._execute_cisco(raw_cmd)
        elif executor.platform == 'linux_shell':
            res = executor._execute_linux(raw_cmd)
        elif executor.platform == 'windows_cmd':
            res = executor._execute_windows(raw_cmd)
        elif executor.platform == 'mikrotik':
            res = executor._execute_mikrotik(raw_cmd)
        else:
            res = {
                'output': f"Unsupported CLI platform: {executor.platform}",
                'prompt': executor.get_prompt(),
                'mode': executor.mode,
                'device': executor.device,
                'mutated': False
            }

        out = res.get('output', '')
        success = not (out.startswith('%') or out.startswith('Error') or out.startswith('Invalid') or 'command not found' in out.lower())
        res['success'] = success
        return res

    def _execute_cisco(self, cmd: str) -> Dict[str, Any]:
        lower = cmd.lower()
        parts = cmd.split()

        # Mode transitions
        if lower in ['enable', 'en']:
            self.mode = 'priv_exec'
            return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
        elif lower in ['disable', 'exit'] and self.mode == 'priv_exec':
            self.mode = 'user_exec'
            return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
        elif lower in ['configure terminal', 'conf t', 'config t']:
            if self.mode != 'priv_exec':
                return {'output': '% Must be in privileged EXEC mode to enter configuration.', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
            self.mode = 'global_config'
            return {'output': 'Enter configuration commands, one per line. End with CNTL/Z.', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
        elif lower in ['exit', 'end']:
            if self.mode in ['interface_config', 'vlan_config']:
                self.mode = 'global_config'
                self.current_interface = None
                self.current_vlan = None
            elif self.mode == 'global_config':
                self.mode = 'priv_exec'
            return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}

        # Show commands
        if lower.startswith('show ') or lower == 'sh':
            return self._handle_cisco_show(cmd)

        # Global Config Commands
        if self.mode == 'global_config':
            if lower.startswith('hostname '):
                new_h = parts[1]
                self.config_service.set_hostname(self.device, new_h)
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}
            elif lower.startswith('interface ') or lower.startswith('int '):
                iface_name = parts[1]
                self.current_interface = iface_name
                self.mode = 'interface_config'
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
            elif lower.startswith('vlan '):
                try:
                    v_id = int(parts[1])
                    self.current_vlan = v_id
                    self.config_service.create_vlan(self.device, v_id)
                    self.mode = 'vlan_config'
                    return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}
                except ValueError:
                    return {'output': '% Invalid VLAN ID.', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
            elif lower.startswith('ip route '):
                if len(parts) >= 5:
                    dest = parts[2]
                    mask = parts[3]
                    nexthop = parts[4]
                    self.config_service.add_static_route(self.device, dest, mask, nexthop)
                    return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}

        # Interface Config Commands
        if self.mode in ['interface_config', 'global_config']:
            if lower.startswith('ip address ') or lower.startswith('ip add '):
                if len(parts) >= 4:
                    ip = parts[2]
                    mask = parts[3]
                    target_iface = self.current_interface or 'GigabitEthernet0/0'
                    self.config_service.set_interface_ip(self.device, target_iface, ip, mask)
                    return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}
            elif 'switchport mode access' in lower:
                target_iface = self.current_interface or 'FastEthernet0/1'
                self.config_service.set_port_mode(self.device, target_iface, 'access')
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}
            elif 'switchport access vlan' in lower:
                target_iface = self.current_interface or 'FastEthernet0/1'
                v_id = int(parts[-1])
                self.config_service.set_port_mode(self.device, target_iface, 'access', vlan=v_id)
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}
            elif 'switchport mode trunk' in lower:
                target_iface = self.current_interface or 'GigabitEthernet0/1'
                self.config_service.set_port_mode(self.device, target_iface, 'trunk')
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}
            elif lower in ['shutdown', 'shut']:
                target_iface = self.current_interface or 'FastEthernet0/1'
                self.config_service.set_interface_status(self.device, target_iface, 'down')
                return {'output': f'% Interface {target_iface} administratively down', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}
            elif lower in ['no shutdown', 'no shut']:
                target_iface = self.current_interface or 'FastEthernet0/1'
                self.config_service.set_interface_status(self.device, target_iface, 'up')
                return {'output': f'% Interface {target_iface} changed state to up', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}

        # VLAN Config Commands
        if self.mode == 'vlan_config':
            if lower.startswith('name '):
                name = parts[1]
                self.config_service.create_vlan(self.device, self.current_vlan, name)
                return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}

        return {'output': f"% Invalid command syntax: '{cmd}' at marker '^'", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}

    def _handle_cisco_show(self, cmd: str) -> Dict[str, Any]:
        lower = cmd.lower()
        if 'running-config' in lower or 'run' in lower:
            out = self.config_service.generate_running_config(self.device)
            return {'output': out, 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
        elif 'ip interface brief' in lower or 'ip int br' in lower:
            lines = ["Interface                  IP-Address      OK? Method Status                Protocol"]
            for iface in self.device.get('interfaces', []):
                ip = iface.get('ip') or 'unassigned'
                st = iface.get('status', 'up')
                stat_str = 'up                    up' if st == 'up' else 'administratively down down'
                lines.append(f"{iface.get('name', 'eth0'):<26} {ip:<15} YES manual {stat_str}")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
        elif 'vlan brief' in lower or 'vlan' in lower:
            lines = ["VLAN Name                             Status    Ports", "---- -------------------------------- --------- -------------------------------"]
            vlans = self.device.get('vlans', [1])
            if isinstance(vlans, dict):
                for v_id, v_data in vlans.items():
                    lines.append(f"{v_id:<4} {v_data.get('name', f'VLAN_{v_id}'):<32} active")
            else:
                for v in vlans:
                    lines.append(f"{v:<4} VLAN_{v:<27} active")
            return {'output': "\n".join(lines), 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
        return {'output': '% Incomplete or unrecognized show command.', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}

    def _execute_linux(self, cmd: str) -> Dict[str, Any]:
        lower = cmd.lower()
        if lower.startswith('ip addr') or lower.startswith('ifconfig'):
            return {'output': f"1: lo: <LOOPBACK,UP> mtu 65536\n2: eth0: <BROADCAST,MULTICAST,UP> inet {self.device.get('ip', '192.168.1.10')}/24", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
        elif lower.startswith('hostnamectl set-hostname '):
            new_h = cmd.split()[-1]
            self.config_service.set_hostname(self.device, new_h)
            return {'output': '', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': True}
        return {'output': f"bash: {cmd}: command not found", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}

    def _execute_windows(self, cmd: str) -> Dict[str, Any]:
        lower = cmd.lower()
        if 'ipconfig' in lower:
            return {'output': f"Ethernet adapter Ethernet0:\n   IPv4 Address. . . . . . . . . . . : {self.device.get('ip', '192.168.1.10')}\n   Subnet Mask . . . . . . . . . . . : {self.device.get('mask', '255.255.255.0')}", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
        return {'output': f"'{cmd}' is not recognized as an internal or external command.", 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}

    def _execute_mikrotik(self, cmd: str) -> Dict[str, Any]:
        return {'output': '[MikroTik RouterOS 7.12]', 'prompt': self.get_prompt(), 'mode': self.mode, 'device': self.device, 'mutated': False}
