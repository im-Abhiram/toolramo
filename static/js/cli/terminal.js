/**
 * Ramonet Interactive Multi-Platform CLI Terminal
 * Handles Cisco IOS, Linux Shell, and Windows Command Prompt interactions.
 */

class RamonetTerminal {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.currentDevice = null;
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
                    <div class="terminal-title">
                        <i class="fa-solid fa-terminal text-info me-1"></i>
                        <span id="term-device-name">No Device Selected</span>
                        <span class="badge bg-secondary ms-2" id="term-platform-badge">IOS</span>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <button class="btn btn-sm btn-outline-secondary py-0 px-2" id="term-btn-clear" title="Clear Screen"><i class="fa-solid fa-eraser"></i> Clear</button>
                        <button class="btn btn-sm btn-outline-secondary py-0 px-2" id="term-btn-help" title="Command Help"><i class="fa-solid fa-question"></i> Help</button>
                    </div>
                </div>
                <div class="terminal-screen" id="term-screen">
                    <div class="term-cisco-banner" id="term-banner">
                        Ramonet Interactive Network Terminal [Version 2.0.0]<br>
                        Type '?' or 'help' for a list of available commands. Type 'enable' to enter privileged mode.
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
    }

    attachDevice(device) {
        this.currentDevice = device;
        if (!device) {
            this.devNameEl.textContent = 'No Device Selected';
            this.platformBadgeEl.textContent = 'None';
            this.setPrompt('Device> ');
            return;
        }

        this.devNameEl.textContent = `${device.name} (${device.model_name || device.category})`;
        const platform = device.cli_platform || 'cisco_ios';
        this.platformBadgeEl.textContent = platform.replace('_', ' ').toUpperCase();

        if (platform === 'cisco_ios') {
            this.setPrompt(`${device.name}> `);
        } else if (platform === 'linux_shell') {
            this.setPrompt(`admin@${device.name.toLowerCase()}:~$ `);
        } else if (platform === 'windows_cmd') {
            this.setPrompt(`C:\\Users\\Admin> `);
        } else {
            this.setPrompt(`${device.name}# `);
        }

        this.appendLine(`<span class="text-info">*** Attached terminal to ${device.name} [${platform}] ***</span>`);
    }

    setPrompt(promptStr) {
        this.prompt = promptStr;
        if (this.promptLabelEl) {
            this.promptLabelEl.textContent = this.prompt;
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
        window.RamonetPrefs?.addRecentCommand(cmd);

        // Echo command
        this.appendLine(`<div><span class="terminal-prompt-label">${this.prompt}</span><span class="text-white">${this.escapeHtml(cmd)}</span></div>`);

        if (cmd.toLowerCase() === 'clear') {
            if (this.outputEl) this.outputEl.innerHTML = '';
            return;
        }

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
                    device: this.currentDevice || { name: 'Device', cli_platform: 'cisco_ios' },
                    topology: window.ramonetCanvas?.project
                })
            });

            if (resp.ok) {
                const data = await resp.json();
                if (data.output) {
                    this.appendLine(`<div class="font-monospace">${this.escapeHtml(data.output)}</div>`);
                }
                if (data.prompt) {
                    this.setPrompt(data.prompt);
                }
                if (data.device && this.currentDevice) {
                    // Apply real state changes back to canvas device object!
                    Object.assign(this.currentDevice, data.device);
                    window.ramonetCanvas?.renderDeviceNode(this.currentDevice);
                    window.ramonetCanvas?.triggerChange(`CLI config: ${cmd}`);
                }
            } else {
                throw new Error('API error: ' + resp.status);
            }
        } catch (err) {
            // Local fallback simulator
            this.executeLocalFallback(cmd);
        }
    }

    executeLocalFallback(cmd) {
        const parts = cmd.split(' ');
        const first = parts[0].toLowerCase();

        if (first === 'help' || first === '?') {
            this.appendLine("<div class='text-muted'>Available commands: enable, configure terminal, interface, ip address, no shutdown, show ip interface brief, show ip route, ping, traceroute, exit</div>");
        } else if (first === 'enable' || first === 'en') {
            this.setPrompt(`${this.currentDevice?.name || 'Router'}# `);
        } else if (first === 'exit') {
            this.setPrompt(`${this.currentDevice?.name || 'Router'}> `);
        } else if (first === 'ping' && parts[1]) {
            this.appendLine(`Sending 5, 100-byte ICMP Echos to ${parts[1]}:\n!!!!!\nSuccess rate is 100 percent (5/5)`);
        } else {
            this.appendLine(`<span class='term-error'>% Command acknowledged: '${cmd}'</span>`);
        }
    }

    handleTabAutocomplete() {
        const currentInput = this.inputEl.value.trim().toLowerCase();
        const commonCisco = [
            'show ip interface brief', 'show ip route', 'show running-config', 'show vlan brief',
            'configure terminal', 'interface', 'ip address', 'no shutdown', 'switchport mode trunk',
            'switchport mode access', 'switchport access vlan', 'ping', 'traceroute'
        ];

        const match = commonCisco.find(c => c.startsWith(currentInput));
        if (match) {
            this.inputEl.value = match + ' ';
        }
    }

    escapeHtml(text) {
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
