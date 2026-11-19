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
        if (this.currentDevice?.cli_session_state) {
            return { ...this.currentDevice.cli_session_state };
        }
        if (this.currentDevice?.id && this.deviceSessions[this.currentDevice.id]) {
            return { ...this.deviceSessions[this.currentDevice.id] };
        }
        return {
            mode: this.mode || 'user_exec',
            current_interface: null,
            current_vlan: null,
            current_router_proto: null
        };
    }

    setSessionState(state) {
        if (!state) return;
        this.mode = state.mode || this.mode;
        if (this.currentDevice) {
            this.currentDevice.cli_session_state = {
                ...(this.currentDevice.cli_session_state || {}),
                ...state
            };
            if (this.currentDevice.id) {
                this.deviceSessions[this.currentDevice.id] = {
                    ...(this.deviceSessions[this.currentDevice.id] || {}),
                    ...state
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
        this.prompt = promptStr;
        if (this.promptLabelEl) {
            this.promptLabelEl.textContent = this.prompt;
        }
        if (this.currentDevice?.id) {
            this.deviceSessions[this.currentDevice.id] = this.deviceSessions[this.currentDevice.id] || {};
            this.deviceSessions[this.currentDevice.id].prompt = promptStr;
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
                if (data.prompt) {
                    this.setPrompt(data.prompt);
                }
                if (data.session_state) {
                    this.setSessionState(data.session_state);
                }
                if (data.device && this.currentDevice) {
                    const oldName = this.currentDevice.name;
                    Object.assign(this.currentDevice, data.device);
                    if (data.session_state) {
                        this.currentDevice.cli_session_state = { ...data.session_state };
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
        const parts = cmd.split(' ');
        const first = parts[0].toLowerCase();
        const devName = this.currentDevice?.name || 'Device';

        if (first === 'help' || first === '?') {
            this.appendLine("<div class='text-muted'>Available commands: enable, configure terminal, interface, ip address, no shutdown, show ip interface brief, show ip route, ping, traceroute, exit</div>");
        } else if (first === 'enable' || first === 'en') {
            this.mode = 'priv_exec';
            this.setPrompt(`${devName}# `);
        } else if (['configure', 'conf', 'config'].includes(first)) {
            this.mode = 'global_config';
            this.setPrompt(`${devName}(config)# `);
        } else if (first === 'exit') {
            if (this.mode === 'global_config') {
                this.mode = 'priv_exec';
                this.setPrompt(`${devName}# `);
            } else {
                this.mode = 'user_exec';
                this.setPrompt(`${devName}> `);
            }
        } else if (first === 'ping' && parts[1]) {
            this.appendLine(`Sending 5, 100-byte ICMP Echos to ${parts[1]}:\n!!!!!\nSuccess rate is 100 percent (5/5)`);
        } else {
            this.appendLine(`<span class='text-secondary small'>% Command acknowledged: '${cmd}'</span>`);
        }
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
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, val] = cookie.trim().split('=');
            if (name === 'csrftoken') return val;
        }
        return '';
    }
}

window.RamonetTerminal = RamonetTerminal;
