/**
 * Ramonet Interactive Multi-Platform CLI Terminal
 * Handles Cisco IOS, Linux Shell, Windows Command Prompt, and Appliance interactions.
 * Features stateful interactive sessions, device switching, and real-time topology mutation.
 */

class RamonetTerminal {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.currentDevice = null;
        this.deviceSessions = {}; // Keyed by device.id -> { mode, current_interface, current_vlan, ... }
        this.history = [];
        this.historyIndex = -1;
        this.prompt = 'Device> ';
        this.mode = 'user_exec';

        this.initDOM();
        this.bindEvents();
    }

    initDOM() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="ramonet-terminal-container">
                <div class="terminal-header">
                    <div class="terminal-title d-flex align-items-center gap-2">
                        <i class="fa-solid fa-terminal text-info"></i>
                        <span id="term-device-name" class="fw-semibold">No Device Selected</span>
                        <span class="badge bg-secondary" id="term-platform-badge">None</span>
                    </div>
                    <div class="d-flex align-items-center gap-2 ms-auto">
                        <label for="term-device-selector" class="small text-secondary mb-0 d-none d-md-inline" style="font-size:0.75rem;">Device:</label>
                        <select id="term-device-selector" class="form-select form-select-sm py-0 px-2 bg-dark text-white border-secondary" style="max-width:200px; font-size:0.75rem;" title="Select active terminal device">
                            <option value="">Select Device...</option>
                        </select>
                        <button class="btn btn-sm btn-outline-secondary py-0 px-2" id="term-btn-clear" title="Clear Screen"><i class="fa-solid fa-eraser"></i> Clear</button>
                        <button class="btn btn-sm btn-outline-secondary py-0 px-2" id="term-btn-help" title="Command Help"><i class="fa-solid fa-question"></i> Help</button>
                    </div>
                </div>
                <div class="terminal-screen" id="term-screen">
                    <div class="term-cisco-banner" id="term-banner">
                        Ramonet Interactive Network Terminal [Kernel v2.0]<br>
                        Type '?' or 'help' for available commands. Use 'enable' for privileged mode.
                    </div>
                    <div id="term-output-lines"></div>
                    <div class="terminal-prompt-line">
                        <span class="terminal-prompt-label" id="term-prompt-label">${this.prompt}</span>
                        <input type="text" class="terminal-input" id="term-input" autocomplete="off" spellcheck="false" autofocus />
                    </div>
                </div>
            </div>
        `;

        this.screenEl = document.getElementById('term-screen');
        this.outputEl = document.getElementById('term-output-lines');
        this.inputEl = document.getElementById('term-input');
        this.promptLabelEl = document.getElementById('term-prompt-label');
        this.devNameEl = document.getElementById('term-device-name');
        this.platformBadgeEl = document.getElementById('term-platform-badge');
        this.devSelectorEl = document.getElementById('term-device-selector');
    }

    bindEvents() {
        if (!this.inputEl) return;

        this.inputEl.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter') {
                const cmd = this.inputEl.value;
                this.inputEl.value = '';
                await this.executeCommand(cmd);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (this.history.length > 0) {
                    if (this.historyIndex === -1) this.historyIndex = this.history.length - 1;
                    else if (this.historyIndex > 0) this.historyIndex--;
                    this.inputEl.value = this.history[this.historyIndex] || '';
                }
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (this.history.length > 0) {
                    if (this.historyIndex < this.history.length - 1) {
                        this.historyIndex++;
                        this.inputEl.value = this.history[this.historyIndex] || '';
                    } else {
                        this.historyIndex = -1;
                        this.inputEl.value = '';
                    }
                }
            } else if (e.key === 'Tab') {
                e.preventDefault();
                this.handleTabAutocomplete();
            } else if (e.key === '?' && this.inputEl.value.trim() === '') {
                e.preventDefault();
                await this.executeCommand('?');
            }
        });

        // Click on terminal focuses input
        this.screenEl?.addEventListener('click', () => {
            this.inputEl?.focus();
        });

        document.getElementById('term-btn-clear')?.addEventListener('click', () => {
            if (this.outputEl) this.outputEl.innerHTML = '';
        });

        document.getElementById('term-btn-help')?.addEventListener('click', async () => {
            await this.executeCommand('?');
        });

        // Device Dropdown Change
        this.devSelectorEl?.addEventListener('change', (e) => {
            const devId = e.target.value;
            if (!devId) {
                this.attachDevice(null);
                return;
            }
            const found = window.ramonetCanvas?.project?.devices?.find(d => String(d.id) === String(devId));
            if (found) {
                this.attachDevice(found);
                window.ramonetCanvas?.selectDevice(found.id);
            }
        });
    }

    syncDeviceSelector() {
        if (!this.devSelectorEl) return;
        const devices = window.ramonetCanvas?.project?.devices || [];
        const currentId = this.currentDevice?.id || '';

        let html = '<option value="">Select Device...</option>';
        devices.forEach(d => {
            const isSelected = String(d.id) === String(currentId) ? 'selected' : '';
            html += `<option value="${d.id}" ${isSelected}>${d.name} (${d.model_name || d.category})</option>`;
        });
        this.devSelectorEl.innerHTML = html;
        if (currentId) {
            this.devSelectorEl.value = currentId;
        }
    }

    getSessionState() {
        const devState = this.currentDevice?.cli_session_state || (this.currentDevice?.id && this.deviceSessions[this.currentDevice.id]) || {};
        const activeMode = this.mode || devState.mode || 'user_exec';
        return {
            current_interface: null,
            current_vlan: null,
            current_router_proto: null,
            ...devState,
            mode: activeMode,
            prompt: this.prompt
        };
    }

    setSessionState(state) {
        if (!state) return;
        this.mode = state.mode || this.mode;
        const updated = {
            mode: this.mode,
            current_interface: state.current_interface !== undefined ? state.current_interface : null,
            current_vlan: state.current_vlan !== undefined ? state.current_vlan : null,
            current_router_proto: state.current_router_proto !== undefined ? state.current_router_proto : null,
            working_dir: state.working_dir || null
        };
        if (this.currentDevice) {
            this.currentDevice.cli_session_state = {
                ...(this.currentDevice.cli_session_state || {}),
                ...updated
            };
            if (this.currentDevice.id) {
                this.deviceSessions[this.currentDevice.id] = {
                    ...(this.deviceSessions[this.currentDevice.id] || {}),
                    ...updated
                };
            }
        }
    }

    attachDevice(device) {
        this.currentDevice = device;
        this.syncDeviceSelector();

        if (!device) {
            // Check if there is an active device on canvas to fallback to
            const firstDev = window.ramonetCanvas?.project?.devices?.[0];
            if (firstDev) {
                return this.attachDevice(firstDev);
            }
            if (this.devNameEl) this.devNameEl.textContent = 'No Device Selected';
            if (this.platformBadgeEl) this.platformBadgeEl.textContent = 'None';
            this.setPrompt('Device> ');
            return;
        }

        const platform = device.cli_platform || 'cisco_ios';
        if (this.devNameEl) this.devNameEl.textContent = `${device.name}`;
        if (this.platformBadgeEl) this.platformBadgeEl.textContent = platform.replace('_', ' ').toUpperCase();

        // Restore or initialize session state
        const savedSession = device.cli_session_state || (device.id && this.deviceSessions[device.id]);
        if (savedSession) {
            this.mode = savedSession.mode || 'user_exec';
            if (device.id) {
                this.deviceSessions[device.id] = { ...savedSession };
            }
            device.cli_session_state = { ...savedSession };
            if (savedSession.prompt) {
                this.setPrompt(savedSession.prompt);
            } else {
                this.computeDefaultPrompt(device, platform);
            }
        } else {
            this.mode = 'user_exec';
            const initSession = { mode: 'user_exec' };
            if (device.id) {
                this.deviceSessions[device.id] = initSession;
            }
            device.cli_session_state = initSession;
            this.computeDefaultPrompt(device, platform);
        }

        this.appendLine(`<div class="text-info small my-1">*** Connected to <strong>${this.escapeHtml(device.name)}</strong> [${platform}] ***</div>`);
        this.inputEl?.focus();
    }

    computeDefaultPrompt(device, platform) {
        const hostname = device.name || 'Device';
        if (platform === 'cisco_ios') {
            const suffix = this.mode === 'priv_exec' ? '#' : (this.mode === 'global_config' ? '(config)#' : '>');
            this.setPrompt(`${hostname}${suffix} `);
        } else if (platform === 'linux_shell') {
            this.setPrompt(`admin@${hostname.toLowerCase()}:~$ `);
        } else if (platform === 'windows_cmd') {
            this.setPrompt(`C:\\Users\\Admin> `);
        } else {
            this.setPrompt(`${hostname}# `);
        }
    }

    setPrompt(promptStr) {
        if (!promptStr) promptStr = 'Device> ';
        this.prompt = promptStr.trimEnd() + ' ';
        if (this.promptLabelEl) {
            this.promptLabelEl.textContent = this.prompt;
        }
        if (this.currentDevice) {
            this.currentDevice.cli_session_state = this.currentDevice.cli_session_state || {};
            this.currentDevice.cli_session_state.prompt = this.prompt;
            this.currentDevice.cli_session_state.mode = this.mode;
            if (this.currentDevice.id) {
                this.deviceSessions[this.currentDevice.id] = this.deviceSessions[this.currentDevice.id] || {};
                this.deviceSessions[this.currentDevice.id].prompt = this.prompt;
                this.deviceSessions[this.currentDevice.id].mode = this.mode;
            }
        }
    }

    appendLine(htmlContent) {
        if (!this.outputEl) return;
        const line = document.createElement('div');
        line.className = 'terminal-output-line';
        line.innerHTML = htmlContent;
        this.outputEl.appendChild(line);
        this.scrollToBottom();
    }

    scrollToBottom() {
        if (this.screenEl) {
            this.screenEl.scrollTop = this.screenEl.scrollHeight;
        }
    }

    async executeCommand(rawCmd) {
        const cmd = rawCmd.trim();
        if (!cmd) {
            this.appendLine(`<div><span class="terminal-prompt-label">${this.prompt}</span></div>`);
            return;
        }

        // Add to history
        this.history.push(cmd);
        this.historyIndex = -1;
        window.RamonetPrefs?.addRecentCommand?.(cmd);

        // Echo command
        this.appendLine(`<div><span class="terminal-prompt-label">${this.prompt}</span><span class="text-white">${this.escapeHtml(cmd)}</span></div>`);

        // Client-side quick clear
        if (cmd.toLowerCase() === 'clear' || cmd.toLowerCase() === 'cls') {
            if (this.outputEl) this.outputEl.innerHTML = '';
            return;
        }

        // Auto-attach if none selected but devices exist
        if (!this.currentDevice) {
            const firstDev = window.ramonetCanvas?.project?.devices?.[0];
            if (firstDev) {
                this.attachDevice(firstDev);
            } else {
                this.appendLine(`<div class="text-warning small">% No device on canvas. Place a device on the canvas first to execute commands.</div>`);
                return;
            }
        }

        const activeSession = this.getSessionState();

        // Call backend CLI execute endpoint
        try {
            const resp = await fetch('/api/commands/execute/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    command: cmd,
                    device: this.currentDevice,
                    topology: window.ramonetCanvas?.project,
                    session_state: activeSession
                })
            });

            if (resp.ok) {
                const data = await resp.json();
                if (data.output) {
                    this.appendLine(`<div class="font-monospace" style="white-space: pre-wrap;">${this.escapeHtml(data.output)}</div>`);
                }
                if (data.mode) {
                    this.mode = data.mode;
                }
                if (data.session_state) {
                    this.setSessionState(data.session_state);
                }
                if (data.prompt) {
                    this.setPrompt(data.prompt);
                }
                if (data.device && this.currentDevice) {
                    const oldName = this.currentDevice.name;
                    Object.assign(this.currentDevice, data.device);
                    if (data.session_state) {
                        this.currentDevice.cli_session_state = { ...data.session_state, mode: this.mode };
                    }
                    if (this.currentDevice.id) {
                        this.deviceSessions[this.currentDevice.id] = {
                            ...(this.deviceSessions[this.currentDevice.id] || {}),
                            mode: this.mode,
                            prompt: this.prompt
                        };
                    }
                    
                    // Update canvas UI
                    window.ramonetCanvas?.renderDeviceNode(this.currentDevice);
                    window.ramonetCanvas?.triggerChange(`CLI: ${cmd}`);

                    // If hostname changed, update terminal title & dropdown
                    if (oldName !== this.currentDevice.name) {
                        if (this.devNameEl) this.devNameEl.textContent = this.currentDevice.name;
                        this.syncDeviceSelector();
                    }
                }
            } else {
                throw new Error('HTTP ' + resp.status);
            }
        } catch (err) {
            console.warn('CLI backend request error, invoking fallback:', err);
            this.executeLocalFallback(cmd);
        }
    }

    executeLocalFallback(cmd) {
        const parts = cmd.split(' ').filter(p => p.trim());
        if (!parts.length) return;
        const first = parts[0].toLowerCase();
        const dev = this.currentDevice;
        const devName = dev?.name || 'Device';
        const platform = dev?.cli_platform || 'cisco_ios';

        // 1. Context Sensitive Help
        if (cmd === '?' || first === 'help' || first === '?') {
            if (platform === 'windows_cmd') {
                this.appendLine("<div class='text-muted small'>Available Windows Commands:<br>&nbsp;&nbsp;ipconfig [/all]&nbsp;&nbsp;&nbsp;&nbsp;Display IP adapter configuration<br>&nbsp;&nbsp;ping &lt;destination&gt;&nbsp;&nbsp;Test ICMP connectivity<br>&nbsp;&nbsp;tracert &lt;dest&gt;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Trace route hops<br>&nbsp;&nbsp;arp -a&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display ARP cache<br>&nbsp;&nbsp;route print&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Display routing table<br>&nbsp;&nbsp;cls / clear&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Clear terminal screen</div>");
            } else if (this.mode === 'user_exec') {
                this.appendLine("<div class='text-muted small'>Exec commands:<br>&nbsp;&nbsp;enable&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Turn on privileged commands<br>&nbsp;&nbsp;ping&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Send ICMP echo messages<br>&nbsp;&nbsp;show&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Show running system information<br>&nbsp;&nbsp;traceroute&nbsp;&nbsp;Trace route to destination<br>&nbsp;&nbsp;exit&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Exit from the EXEC</div>");
            } else if (this.mode === 'priv_exec') {
                this.appendLine("<div class='text-muted small'>Exec commands:<br>&nbsp;&nbsp;configure&nbsp;&nbsp;&nbsp;Enter configuration mode<br>&nbsp;&nbsp;disable&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Turn off privileged commands<br>&nbsp;&nbsp;ping&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Send ICMP echo messages<br>&nbsp;&nbsp;show&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Show running system information<br>&nbsp;&nbsp;traceroute&nbsp;&nbsp;Trace route to destination<br>&nbsp;&nbsp;write&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Write running configuration to memory<br>&nbsp;&nbsp;exit&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Exit from the EXEC</div>");
            } else if (this.mode === 'global_config') {
                this.appendLine("<div class='text-muted small'>Configure commands:<br>&nbsp;&nbsp;hostname&nbsp;&nbsp;&nbsp;&nbsp;Set system network name<br>&nbsp;&nbsp;interface&nbsp;&nbsp;&nbsp;Select an interface to configure<br>&nbsp;&nbsp;ip&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Global IP configuration subcommands<br>&nbsp;&nbsp;vlan&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VLAN configuration<br>&nbsp;&nbsp;do&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Execute an EXEC-level command<br>&nbsp;&nbsp;exit&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Exit from configure mode<br>&nbsp;&nbsp;end&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Exit to privileged EXEC</div>");
            } else if (this.mode === 'interface_config') {
                this.appendLine("<div class='text-muted small'>Interface configuration commands:<br>&nbsp;&nbsp;ip address&nbsp;&nbsp;Set IP address and subnet mask<br>&nbsp;&nbsp;no shutdown Enable interface<br>&nbsp;&nbsp;shutdown&nbsp;&nbsp;&nbsp;&nbsp;Disable interface<br>&nbsp;&nbsp;switchport&nbsp;&nbsp;Set access or trunk VLAN mode<br>&nbsp;&nbsp;exit&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Exit to global configure mode</div>");
            }
            return;
        }

        // 2. Mode Navigation
        if (first === 'enable' || first === 'en') {
            this.mode = 'priv_exec';
            this.setSessionState({ mode: 'priv_exec' });
            this.setPrompt(`${devName}# `);
            return;
        }
        if (first === 'disable') {
            this.mode = 'user_exec';
            this.setSessionState({ mode: 'user_exec' });
            this.setPrompt(`${devName}> `);
            return;
        }
        if (['configure', 'conf', 'config'].includes(first)) {
            if (this.mode === 'user_exec') {
                this.appendLine("<div class='text-warning small'>% Command requires privileged mode. Type 'enable' first.</div>");
                return;
            }
            this.mode = 'global_config';
            this.setSessionState({ mode: 'global_config' });
            this.setPrompt(`${devName}(config)# `);
            this.appendLine("<div class='text-muted small'>Enter configuration commands, one per line. End with CNTL/Z or 'end'.</div>");
            return;
        }
        if (first === 'end') {
            if (this.mode !== 'user_exec') {
                this.mode = 'priv_exec';
                this.setSessionState({ mode: 'priv_exec', current_interface: null });
                this.setPrompt(`${devName}# `);
            }
            return;
        }
        if (first === 'exit' || first === 'quit') {
            if (this.mode === 'interface_config' || this.mode === 'vlan_config') {
                this.mode = 'global_config';
                this.setSessionState({ mode: 'global_config', current_interface: null });
                this.setPrompt(`${devName}(config)# `);
            } else if (this.mode === 'global_config') {
                this.mode = 'priv_exec';
                this.setSessionState({ mode: 'priv_exec' });
                this.setPrompt(`${devName}# `);
            } else {
                this.mode = 'user_exec';
                this.setSessionState({ mode: 'user_exec' });
                this.setPrompt(`${devName}> `);
            }
            return;
        }

        // 3. Global Config Commands
        if (this.mode === 'global_config') {
            if (first === 'hostname' && parts[1]) {
                const newName = parts[1];
                dev.name = newName;
                if (this.devNameEl) this.devNameEl.textContent = newName;
                this.syncDeviceSelector();
                this.setPrompt(`${newName}(config)# `);
                window.ramonetCanvas?.renderDeviceNode(dev);
                window.ramonetCanvas?.triggerChange(`Renamed to ${newName}`);
                return;
            }
            if (['interface', 'int'].includes(first) && parts.length > 1) {
                const ifcName = parts.slice(1).join('');
                this.mode = 'interface_config';
                this.setSessionState({ mode: 'interface_config', current_interface: ifcName });
                this.setPrompt(`${devName}(config-if)# `);
                return;
            }
            if (first === 'ip' && parts[1] === 'default-gateway' && parts[2]) {
                dev.gateway = parts[2];
                window.ramonetCanvas?.triggerChange('Set default gateway');
                return;
            }
        }

        // 4. Interface Config Commands
        if (this.mode === 'interface_config') {
            const activeIfc = this.getSessionState()?.current_interface || 'eth0';
            if (first === 'ip' && ['address', 'addr', 'add'].includes(parts[1]?.toLowerCase()) && parts[2]) {
                let ipVal = parts[2];
                let maskVal = parts[3] || '255.255.255.0';
                if (ipVal.includes('/')) {
                    const sp = ipVal.split('/');
                    ipVal = sp[0];
                    maskVal = sp[1] === '24' ? '255.255.255.0' : (sp[1] === '16' ? '255.255.0.0' : '255.0.0.0');
                }
                dev.ip = ipVal;
                dev.subnet_mask = maskVal;
                if (dev.interfaces && dev.interfaces.length > 0) {
                    const match = dev.interfaces.find(i => (typeof i === 'object' && i.name?.toLowerCase() === activeIfc.toLowerCase()));
                    if (match) {
                        match.ip = ipVal;
                        match.mask = maskVal;
                    } else if (typeof dev.interfaces[0] === 'object') {
                        dev.interfaces[0].ip = ipVal;
                        dev.interfaces[0].mask = maskVal;
                    }
                }
                window.ramonetCanvas?.renderDeviceNode(dev);
                window.ramonetCanvas?.triggerChange(`Configured IP on ${activeIfc}`);
                return;
            }
            if (first === 'no' && ['shutdown', 'shut', 'sh'].includes(parts[1]?.toLowerCase())) {
                this.appendLine(`<div class="text-success small">% Interface ${activeIfc}, changed state to up<br>% LINEPROTO-5-UPDOWN: Line protocol on Interface ${activeIfc}, changed state to up</div>`);
                return;
            }
            if (['shutdown', 'shut'].includes(first)) {
                this.appendLine(`<div class="text-warning small">% Interface ${activeIfc}, changed state to administratively down</div>`);
                return;
            }
        }

        // 5. Show Commands
        if (['show', 'sh'].includes(first)) {
            const sub = parts.slice(1).join(' ').toLowerCase();
            if (['ip interface brief', 'ip int br', 'ip int brief', 'ip int', 'int br'].some(k => sub.includes(k))) {
                let out = "<pre class='mb-0 text-cyan'>Interface              IP-Address      OK? Method Status                Protocol\n--------------------------------------------------------------------------------\n";
                const ifcs = dev.interfaces || [{ name: 'eth0', ip: dev.ip, status: 'up' }];
                ifcs.forEach(i => {
                    const n = (typeof i === 'string' ? i : i.name).padEnd(22);
                    const ip = ((typeof i === 'object' ? i.ip : '') || dev.ip || 'unassigned').padEnd(15);
                    out += `${n} ${ip} YES manual up                    up\n`;
                });
                out += "</pre>";
                this.appendLine(out);
                return;
            }
            if (sub.includes('run') || sub.includes('running-config')) {
                let out = `<pre class='mb-0 text-cyan'>! Running configuration of ${devName}\nhostname ${devName}\n!\n`;
                (dev.interfaces || []).forEach(i => {
                    const n = typeof i === 'string' ? i : i.name;
                    const ip = (typeof i === 'object' ? i.ip : '') || dev.ip;
                    out += `interface ${n}\n`;
                    if (ip) out += ` ip address ${ip} ${dev.subnet_mask || '255.255.255.0'}\n`;
                    out += " no shutdown\n!\n";
                });
                out += "end</pre>";
                this.appendLine(out);
                return;
            }
            if (sub.includes('vlan')) {
                this.appendLine("<pre class='mb-0 text-cyan'>VLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4\n10   DATA                             active    Fa0/5, Fa0/6\n20   VOICE                            active    Fa0/7, Fa0/8</pre>");
                return;
            }
            if (sub.includes('version')) {
                this.appendLine(`<pre class='mb-0 text-cyan'>Cisco IOS Software, RAMONET-SIM Version 15.7(3)M4\nTechnical Support: https://github.com/im-Abhiram/toolramo\nDevice Model: ${dev.model_name || dev.category || 'Cisco Catalyst'}</pre>`);
                return;
            }
            if (sub.includes('route') || sub.includes('ro')) {
                this.appendLine(`<pre class='mb-0 text-cyan'>Codes: C - connected, S - static\nGateway of last resort is ${dev.gateway || 'not set'}\n\nC    ${dev.ip ? dev.ip + '/24' : '192.168.1.0/24'} is directly connected, eth0</pre>`);
                return;
            }
        }

        // 6. Windows Commands
        if (first === 'ipconfig') {
            let out = `<pre class='mb-0 text-cyan'>Windows IP Configuration\n\nEthernet adapter Ethernet0:\n   Connection-specific DNS Suffix  . : localdomain\n   IPv4 Address. . . . . . . . . . . : ${dev.ip || '192.168.1.50'}\n   Subnet Mask . . . . . . . . . . . : ${dev.subnet_mask || '255.255.255.0'}\n   Default Gateway . . . . . . . . . : ${dev.gateway || '192.168.1.1'}</pre>`;
            this.appendLine(out);
            return;
        }
        if (first === 'route' && parts[1]?.toLowerCase() === 'print') {
            this.appendLine(`<pre class='mb-0 text-cyan'>IPv4 Route Table\n===========================================================================\nActive Routes:\nNetwork Destination        Netmask          Gateway       Interface  Metric\n          0.0.0.0          0.0.0.0      ${dev.gateway || '192.168.1.1'}    ${dev.ip || '192.168.1.50'}     25\n      192.168.1.0    255.255.255.0         On-link     ${dev.ip || '192.168.1.50'}    281</pre>`);
            return;
        }
        if (first === 'arp' && parts.includes('-a')) {
            this.appendLine(`<pre class='mb-0 text-cyan'>Interface: ${dev.ip || '192.168.1.50'} --- 0xb\n  Internet Address      Physical Address      Type\n  ${dev.gateway || '192.168.1.1'}         00-1a-2b-3c-4d-5e     dynamic</pre>`);
            return;
        }

        // 7. Ping Command
        if (first === 'ping' && parts[1]) {
            const target = parts[1];
            this.appendLine(`<div class="text-cyan small font-monospace">Sending 5, 100-byte ICMP Echos to ${target}, timeout is 2 seconds:<br>!!!!!<br>Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms</div>`);
            window.ramonetVisualizer?.tracePacket(dev.id, target, 'ICMP');
            return;
        }

        // 8. Write Memory
        if (['write', 'wr'].includes(first)) {
            this.appendLine("<div class='text-muted small'>Building configuration...<br>[OK]<br>Configuration saved to NVRAM.</div>");
            return;
        }

        this.appendLine(`<span class='text-secondary small'>% Command acknowledged: '${cmd}'. Type '?' for available commands.</span>`);
    }

    handleTabAutocomplete() {
        const currentInput = this.inputEl.value.trim().toLowerCase();
        const commonCisco = [
            'show ip interface brief', 'show ip route', 'show running-config', 'show vlan brief',
            'show mac address-table', 'show version', 'configure terminal', 'interface',
            'ip address', 'no shutdown', 'switchport mode trunk', 'switchport mode access',
            'switchport access vlan', 'ping', 'traceroute', 'write memory', 'exit', 'end'
        ];

        const match = commonCisco.find(c => c.startsWith(currentInput));
        if (match) {
            this.inputEl.value = match + ' ';
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getCSRFToken() {
        const fromInput = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
        if (fromInput) return fromInput;
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, val] = cookie.trim().split('=');
            if (name === 'csrftoken') return val;
        }
        return '';
    }
}

window.RamonetTerminal = RamonetTerminal;
