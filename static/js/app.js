/**
 * Ramonet Main Client Application Controller
 * Handles UI interactions, modals, drawers, toasts, templates, and global search.
 */

class RamonetUI {
    constructor() {
        this.selectedDevice = null;
        this.init();
    }

    init() {
        this.bindSidebar();
        this.bindGlobalSearch();
        this.bindWorkbench();
        this.bindModals();
        this.loadInitialPreferences();
    }

    bindSidebar() {
        const toggleBtn = document.getElementById('sidebar-toggle-btn');
        const sidebar = document.getElementById('ramonet-sidebar');
        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                const isCollapsed = sidebar.classList.contains('collapsed');
                window.RamonetPrefs?.set(window.RamonetPrefs.KEYS.SIDEBAR, isCollapsed);
            });
        }
    }

    loadInitialPreferences() {
        const isCollapsed = window.RamonetPrefs?.get(window.RamonetPrefs?.KEYS?.SIDEBAR, false);
        const sidebar = document.getElementById('ramonet-sidebar');
        if (isCollapsed && sidebar) {
            sidebar.classList.add('collapsed');
        }
    }

    bindWorkbench() {
        const drawer = document.getElementById('workbench-drawer');
        const toggleBtn = document.getElementById('workbench-toggle-btn');
        if (toggleBtn && drawer) {
            toggleBtn.addEventListener('click', () => {
                drawer.classList.toggle('minimized');
                toggleBtn.querySelector('i')?.classList.toggle('fa-chevron-down');
                toggleBtn.querySelector('i')?.classList.toggle('fa-chevron-up');
            });
        }

        // Tab Switching
        document.querySelectorAll('.workbench-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const target = btn.dataset.tab;
                this.showWorkbenchTab(target);
            });
        });
    }

    showWorkbenchTab(tabId) {
        document.querySelectorAll('.workbench-tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.workbench-tab-pane').forEach(p => p.classList.add('d-none'));

        const btn = document.querySelector(`.workbench-tab-btn[data-tab="${tabId}"]`);
        const pane = document.getElementById(`tab-pane-${tabId}`);
        if (btn) btn.classList.add('active');
        if (pane) pane.classList.remove('d-none');

        // Un-minimize drawer if minimized
        const drawer = document.getElementById('workbench-drawer');
        if (drawer && drawer.classList.contains('minimized')) {
            drawer.classList.remove('minimized');
        }

        if (tabId === 'device-web-gui') {
            const dev = window.ramonetCanvas?.selectedDevice || window.ramonetCanvas?.project?.devices?.[0];
            if (dev) {
                this.renderDeviceWebGUI(dev);
            }
        }
    }

    bindGlobalSearch() {
        const searchInput = document.getElementById('global-search-input');
        const resultsBox = document.getElementById('global-search-results');
        if (!searchInput || !resultsBox) return;

        let debounceTimer = null;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const q = e.target.value.trim();
            if (q.length < 2) {
                resultsBox.classList.add('d-none');
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const resp = await fetch(`/api/knowledgebase/search/?q=${encodeURIComponent(q)}`);
                    if (resp.ok) {
                        const items = await resp.json();
                        this.renderSearchResults(items, resultsBox);
                    }
                } catch (err) {
                    console.warn('Search failed:', err);
                }
            }, 300);
        });

        // Hide search when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !resultsBox.contains(e.target)) {
                resultsBox.classList.add('d-none');
            }
        });
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    renderSearchResults(items, container) {
        if (!items || items.length === 0) {
            container.innerHTML = '<div class="p-3 text-muted small">No matching commands or articles found.</div>';
            container.classList.remove('d-none');
            return;
        }

        let html = '';
        items.slice(0, 8).forEach(item => {
            const icon = item.type === 'command' ? 'fa-terminal text-info' : 'fa-book text-warning';
            const safeTitle = this.escapeHtml(item.title);
            const safeCategory = this.escapeHtml(item.category || item.type);
            const safeSub = this.escapeHtml(item.summary || item.syntax || '');
            const safeType = encodeURIComponent(item.type || '');
            const safeId = encodeURIComponent(item.id || item.slug || '');
            const safeTitleEnc = encodeURIComponent(item.title || '');

            html += `
                <div class="p-2 border-bottom border-secondary border-opacity-25 search-result-item" style="cursor:pointer;" onclick="window.ramonetUI.handleSearchItemClick('${safeType}', '${safeId}', '${safeTitleEnc}')">
                    <div class="d-flex align-items-center gap-2">
                        <i class="fa-solid ${icon}"></i>
                        <strong class="text-white small">${safeTitle}</strong>
                        <span class="badge bg-secondary ms-auto" style="font-size:0.65rem;">${safeCategory}</span>
                    </div>
                    <div class="text-secondary small font-monospace" style="font-size:0.75rem;">${safeSub}</div>
                </div>
            `;
        });

        container.innerHTML = html;
        container.classList.remove('d-none');
    }

    handleSearchItemClick(type, id, encodedTitle) {
        const title = decodeURIComponent(encodedTitle);
        document.getElementById('global-search-results')?.classList.add('d-none');
        if (type === 'command') {
            window.location.href = `/commands/?q=${encodeURIComponent(title)}`;
        } else {
            window.ramonetAssistant?.showDeviceGuide(title);
        }
    }

    bindModals() {
        // Wizard next button
        document.getElementById('wizNextBtn')?.addEventListener('click', () => {
            window.ramonetAssistant?.wizardNext();
        });
    }

    openDeviceInspector(device) {
        if (!device) return;
        this.updateSelectedDevice(device, true);
        const panel = document.getElementById('device-inspector-panel');
        if (panel) {
            panel.classList.remove('closed');
        }
    }

    updateSelectedDevice(device, openInspector = false) {
        this.selectedDevice = device;
        const panel = document.getElementById('device-inspector-panel');
        if (!panel) return;

        if (!device) {
            panel.classList.add('closed');
            window.ramonetTerminal?.attachDevice(null);
            return;
        }

        if (openInspector || !panel.classList.contains('closed')) {
            panel.classList.remove('closed');
        }
        window.ramonetTerminal?.attachDevice(device);

        // Populate inspector header & fields
        const nameEl = document.getElementById('inspector-dev-name');
        const modelEl = document.getElementById('inspector-dev-model');
        const hostnameInput = document.getElementById('inspector-dev-hostname');
        const categoryInput = document.getElementById('inspector-dev-category');
        const powerEl = document.getElementById('inspector-dev-power');
        const poeEl = document.getElementById('inspector-dev-poe');
        const ipInput = document.getElementById('inspector-dev-ip');
        const maskInput = document.getElementById('inspector-dev-mask');
        const gwInput = document.getElementById('inspector-dev-gw');
        const dnsInput = document.getElementById('inspector-dev-dns');
        const iconEl = document.getElementById('inspector-dev-icon');
        const ifcCountBadge = document.getElementById('inspector-ifc-count');
        const subnetSummary = document.getElementById('inspector-subnet-summary');

        if (nameEl) nameEl.textContent = device.name;
        if (modelEl) modelEl.textContent = device.model_name || device.category;
        if (hostnameInput) hostnameInput.value = device.name || '';
        
        let catDisplay = device.category || 'Endpoint';
        const dNameLow = (device.name || '').toLowerCase();
        const mNameLow = (device.model_name || '').toLowerCase();
        if (dNameLow.includes('nvr') || mNameLow.includes('nvr')) {
            catDisplay = 'NVR Surveillance Storage';
        } else if (dNameLow.includes('camera') || mNameLow.includes('camera') || device.category === 'cctv') {
            catDisplay = 'IP PoE Video Camera';
        } else if (device.category === 'switches') {
            catDisplay = device.is_layer3 ? 'Layer 3 Managed Switch' : 'Layer 2 Managed Switch';
        } else if (device.category === 'routers') {
            catDisplay = 'Enterprise Router';
        } else if (device.category === 'firewalls') {
            catDisplay = 'Next-Gen Stateful Firewall';
        } else if (device.category === 'servers') {
            catDisplay = 'Application & Network Server';
        } else if (device.category === 'storage') {
            catDisplay = 'Network Attached Storage (NAS)';
        } else if (device.category === 'printers') {
            catDisplay = 'Network Print Server';
        } else if (device.category === 'wireless') {
            catDisplay = 'Wireless Access Point (AP)';
        } else if (device.category === 'computers') {
            catDisplay = 'Endpoint Workstation';
        }
        if (categoryInput) categoryInput.value = catDisplay;
        if (powerEl) powerEl.textContent = `${device.power_watts || 25} W`;
        if (poeEl) poeEl.textContent = `${device.poe_budget_watts || 0} W`;
        if (ipInput) ipInput.value = device.ip || '';
        if (maskInput) maskInput.value = device.subnet_mask || '255.255.255.0';
        if (gwInput) gwInput.value = device.gateway || '';
        if (dnsInput) dnsInput.value = device.dns || '8.8.8.8';
        if (iconEl) iconEl.className = `fa-solid ${device.icon || 'fa-server'}`;

        const ifcCount = (device.interfaces || []).length;
        if (ifcCountBadge) ifcCountBadge.textContent = `${ifcCount} port${ifcCount === 1 ? '' : 's'}`;

        // Update inspector device picture
        const picEl = document.getElementById('inspector-dev-pic');
        if (picEl) {
            picEl.src = window.ramonetCanvas?.getDevicePic(device) || '/static/img/devices/switch.svg';
        }

        // If the Web GUI tab is active, update it in real-time
        const activeTabBtn = document.querySelector('.workbench-tab-btn.active');
        if (activeTabBtn && activeTabBtn.getAttribute('data-tab') === 'device-web-gui') {
            this.renderDeviceWebGUI(device);
        }

        if (subnetSummary) {
            const mask = device.subnet_mask || '255.255.255.0';
            let prefix = '/24';
            if (mask === '255.255.255.252') prefix = '/30 (2 Hosts)';
            else if (mask === '255.255.255.240') prefix = '/28 (14 Hosts)';
            else if (mask === '255.255.255.128') prefix = '/25 (126 Hosts)';
            else if (mask === '255.255.255.0') prefix = '/24 (254 Hosts)';
            else if (mask === '255.255.0.0') prefix = '/16 (65,534 Hosts)';
            else if (mask === '255.0.0.0') prefix = '/8 (16.7M Hosts)';
            subnetSummary.textContent = prefix;
        }

        // Populate Interfaces Tab
        this.renderInspectorInterfaces(device);
    }

    renderInspectorInterfaces(device) {
        const listEl = document.getElementById('inspector-interfaces-list');
        if (!listEl) return;

        let html = '';
        (device.interfaces || []).forEach(ifc => {
            const statusClass = ifc.status === 'up' ? 'text-success' : 'text-danger';
            html += `
                <div class="p-2 mb-2 bg-sidebar rounded border border-secondary border-opacity-25 d-flex align-items-center justify-content-between">
                    <div>
                        <strong class="text-white small font-monospace">${ifc.name}</strong>
                        <div class="text-muted" style="font-size:0.7rem;">${ifc.type || 'copper'} - ${ifc.speed || 1000} Mbps ${ifc.poe ? '(PoE)' : ''}</div>
                    </div>
                    <span class="badge ${ifc.status === 'up' ? 'bg-success' : 'bg-secondary'}">${ifc.status || 'up'}</span>
                </div>
            `;
        });
        listEl.innerHTML = html || '<div class="text-muted small">No interfaces available.</div>';
    }

    ensureConnectModalDOM() {
        let modalEl = document.getElementById('connectCableModal');
        if (!modalEl) {
            modalEl = document.createElement('div');
            modalEl.className = 'modal fade';
            modalEl.id = 'connectCableModal';
            modalEl.tabIndex = -1;
            modalEl.setAttribute('aria-labelledby', 'connectCableModalLabel');
            modalEl.setAttribute('aria-hidden', 'true');
            modalEl.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content bg-dark border border-cyan text-white shadow-lg">
                        <div class="modal-header border-secondary border-opacity-25 py-2">
                            <h6 class="modal-title fw-bold text-cyan" id="connectCableModalLabel">
                                <i class="fa-solid fa-ethernet me-2"></i>Connect Network Cable
                            </h6>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body py-3">
                            <div class="row g-3 mb-3">
                                <div class="col-6">
                                    <label class="form-label small text-secondary fw-semibold">Source Device</label>
                                    <div class="p-2 bg-sidebar rounded border border-secondary border-opacity-25 mb-2">
                                        <div class="text-white small fw-bold text-truncate" id="connect-src-name">Device A</div>
                                    </div>
                                    <label class="form-label small text-secondary" for="connect-src-port">Select Port</label>
                                    <select class="form-select form-select-sm bg-dark text-white border-secondary" id="connect-src-port">
                                    </select>
                                </div>
                                <div class="col-6">
                                    <label class="form-label small text-secondary fw-semibold">Destination Device</label>
                                    <div class="p-2 bg-sidebar rounded border border-secondary border-opacity-25 mb-2">
                                        <div class="text-white small fw-bold text-truncate" id="connect-dest-name">Device B</div>
                                    </div>
                                    <label class="form-label small text-secondary" for="connect-dest-port">Select Port</label>
                                    <select class="form-select form-select-sm bg-dark text-white border-secondary" id="connect-dest-port">
                                    </select>
                                </div>
                            </div>
                            <div class="mb-2">
                                <label class="form-label small text-secondary fw-semibold" for="connect-cable-type">Cable / Media Type</label>
                                <select class="form-select form-select-sm bg-dark text-white border-secondary" id="connect-cable-type">
                                    <option value="copper_straight">Copper Straight-Through (RJ45 Cat6)</option>
                                    <option value="copper_cross">Copper Crossover (RJ45)</option>
                                    <option value="fiber">Fiber Optic (LC-LC Singlemode)</option>
                                    <option value="serial">Serial WAN Cable (V.35 / Smart Serial)</option>
                                    <option value="console">Rollover / Console Cable (RJ45-to-DB9 / USB)</option>
                                </select>
                            </div>
                        </div>
                        <div class="modal-footer border-secondary border-opacity-25 py-2">
                            <button type="button" class="btn btn-sm btn-outline-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-sm btn-cyan px-3" id="btn-confirm-connect">
                                <i class="fa-solid fa-plug me-1"></i>Connect Devices
                            </button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modalEl);
        }
        return modalEl;
    }

    openConnectModal(srcDevice, destDevice, onConfirm) {
        const modalEl = this.ensureConnectModalDOM();
        if (!modalEl) return;

        document.getElementById('connect-src-name').textContent = srcDevice.name || 'Source Device';
        document.getElementById('connect-dest-name').textContent = destDevice.name || 'Target Device';

        // Find ports currently in use
        const connections = window.ramonetCanvas?.project?.connections || [];
        const getUsedPorts = (dev) => {
            const devId = String(dev?.id || '');
            const devName = String(dev?.name || '').toLowerCase();
            return connections
                .filter(c => {
                    const s = String(c.source_device || c.from || c.source || '');
                    const t = String(c.target_device || c.to || c.target || '');
                    return s === devId || s.toLowerCase() === devName || t === devId || t.toLowerCase() === devName;
                })
                .map(c => {
                    const s = String(c.source_device || c.from || c.source || '');
                    const isSrc = (s === devId || s.toLowerCase() === devName);
                    return isSrc ? (c.source_port || c.from_port || c.src_port) : (c.target_port || c.to_port || c.dest_port);
                });
        };

        const srcUsed = getUsedPorts(srcDevice);
        const destUsed = getUsedPorts(destDevice);

        // Helper to generate default interfaces if none defined
        const getOrGenerateInterfaces = (dev) => {
            let ifaces = [];
            if (dev.interfaces && dev.interfaces.length > 0) {
                ifaces = [...dev.interfaces];
            } else {
                const cat = (dev.category || '').toLowerCase();
                if (cat.includes('switch')) {
                    ifaces = Array.from({ length: 24 }, (_, i) => ({ name: `FastEthernet0/${i + 1}`, speed: 100 }));
                } else if (cat.includes('router') || cat.includes('firewall')) {
                    ifaces = [
                        { name: 'GigabitEthernet0/0', speed: 1000 },
                        { name: 'GigabitEthernet0/1', speed: 1000 },
                        { name: 'GigabitEthernet0/2', speed: 1000 }
                    ];
                } else {
                    ifaces = [{ name: 'eth0', speed: 1000 }, { name: 'eth1', speed: 1000 }];
                }
            }
            return ifaces.map(i => {
                if (typeof i === 'string') {
                    return { name: i, speed: 1000, status: 'up' };
                }
                return { name: i.name || 'eth0', speed: i.speed || 1000, status: i.status || 'up' };
            });
        };

        const srcIfaces = getOrGenerateInterfaces(srcDevice);
        const destIfaces = getOrGenerateInterfaces(destDevice);

        const srcPortSel = document.getElementById('connect-src-port');
        const destPortSel = document.getElementById('connect-dest-port');

        let firstFreeSrc = null;
        srcPortSel.innerHTML = srcIfaces.map(i => {
            const isUsed = srcUsed.includes(i.name);
            if (!isUsed && !firstFreeSrc) firstFreeSrc = i.name;
            return `<option value="${i.name}" ${isUsed ? 'disabled' : ''}>${i.name} ${isUsed ? '(in use)' : ''}</option>`;
        }).join('');
        if (firstFreeSrc) srcPortSel.value = firstFreeSrc;

        let firstFreeDest = null;
        destPortSel.innerHTML = destIfaces.map(i => {
            const isUsed = destUsed.includes(i.name);
            if (!isUsed && !firstFreeDest) firstFreeDest = i.name;
            return `<option value="${i.name}" ${isUsed ? 'disabled' : ''}>${i.name} ${isUsed ? '(in use)' : ''}</option>`;
        }).join('');
        if (firstFreeDest) destPortSel.value = firstFreeDest;

        // Auto-recommend cable type based on device types
        const cableTypeSel = document.getElementById('connect-cable-type');
        const isSrcSwitch = (srcDevice.category || '').includes('switch');
        const isDestSwitch = (destDevice.category || '').includes('switch');
        const isSrcRouter = (srcDevice.category || '').includes('router');
        const isDestRouter = (destDevice.category || '').includes('router');

        if ((isSrcSwitch && isDestSwitch) || (isSrcRouter && isDestRouter)) {
            cableTypeSel.value = 'copper_cross';
        } else {
            cableTypeSel.value = 'copper_straight';
        }

        const confirmBtn = document.getElementById('btn-confirm-connect');
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        const bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);
        newConfirmBtn.addEventListener('click', () => {
            const cableType = cableTypeSel.value;
            const srcPort = srcPortSel.value || 'eth0';
            const destPort = destPortSel.value || 'eth0';
            bsModal.hide();
            if (typeof onConfirm === 'function') {
                onConfirm(cableType, srcPort, destPort);
            }
        });

        bsModal.show();
    }

    showConnectionInspector(conn) {
        if (!conn) return;
        const devices = window.ramonetCanvas?.project?.devices || [];
        const srcId = String(conn.source_device || conn.from || conn.source || '');
        const destId = String(conn.target_device || conn.to || conn.target || '');
        const src = devices.find(d => String(d.id) === srcId || String(d.name).toLowerCase() === srcId.toLowerCase());
        const dest = devices.find(d => String(d.id) === destId || String(d.name).toLowerCase() === destId.toLowerCase());
        const srcName = src ? src.name : srcId;
        const destName = dest ? dest.name : destId;
        const srcPort = conn.source_port || conn.from_port || conn.src_port || 'port';
        const destPort = conn.target_port || conn.to_port || conn.dest_port || 'port';
        const cableType = (conn.type || 'copper_straight').replace(/_/g, ' ').toUpperCase();

        const container = document.getElementById('toast-container');
        if (!container) return;

        // Remove any previous connection toast
        document.querySelectorAll('.toast-cable-inspector').forEach(t => t.remove());

        const toast = document.createElement('div');
        toast.className = 'toast show ramonet-toast toast-cable-inspector mb-2 border border-info shadow-lg';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="toast-header bg-dark text-white border-bottom border-secondary border-opacity-25 d-flex justify-content-between align-items-center">
                <div><i class="fa-solid fa-plug text-cyan me-2"></i><strong>Cable Connection</strong></div>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body small text-secondary bg-dark">
                <div class="mb-2 text-white">
                    <strong class="text-info">${srcName}</strong> [${srcPort}] <i class="fa-solid fa-arrows-left-right text-cyan mx-1"></i> <strong class="text-info">${destName}</strong> [${destPort}]
                </div>
                <div class="text-muted mb-3" style="font-size:0.75rem;">Type: <span class="text-cyan">${cableType}</span> | Status: <span class="text-success">${conn.status || 'connected'}</span></div>
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-outline-danger py-1 px-2 disconnect-cable-btn" style="font-size:0.75rem;">
                        <i class="fa-solid fa-scissors me-1"></i>Disconnect Cable
                    </button>
                </div>
            </div>
        `;
        toast.querySelector('.disconnect-cable-btn')?.addEventListener('click', () => {
            window.ramonetCanvas?.deleteConnection(conn.id);
            toast.remove();
            this.showToast('Cable Disconnected', `Removed connection between ${srcName} [${srcPort}] and ${destName} [${destPort}]`, 'info');
        });
        toast.querySelector('.btn-close')?.addEventListener('click', () => {
            toast.remove();
            if (window.ramonetCanvas) {
                window.ramonetCanvas.selectedConnection = null;
                window.ramonetCanvas.renderConnections();
            }
        });
        container.appendChild(toast);
    }

    showToast(title, message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const id = 'toast_' + Date.now();
        const toast = document.createElement('div');
        toast.className = 'toast show ramonet-toast mb-2';
        toast.id = id;
        toast.setAttribute('role', 'alert');

        const icon = type === 'success' ? 'fa-circle-check text-success' : (type === 'danger' ? 'fa-circle-xmark text-danger' : 'fa-circle-info text-info');

        toast.innerHTML = `
            <div class="toast-header bg-sidebar text-white border-bottom border-secondary border-opacity-25">
                <i class="fa-solid ${icon} me-2"></i>
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body small text-secondary">
                ${message}
            </div>
        `;

        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4500);
    }

    // Load any of the 18 prebuilt network templates into canvas
    async loadNetworkTemplate(templateName) {
        this.showToast('Loading Topology', `Configuring ${templateName}...`, 'info');
        try {
            let resp = await fetch(`/api/projects/template/?name=${encodeURIComponent(templateName)}`);
            if (!resp.ok) {
                resp = await fetch(`/projects/template/?name=${encodeURIComponent(templateName)}`);
            }
            if (resp.ok) {
                const projectData = await resp.json();
                window.ramonetCanvas?.loadProjectData(projectData);
                setTimeout(() => {
                    window.ramonetCanvas?.fitToScreen();
                    window.ramonetTerminal?.syncDeviceSelector();
                    if (projectData.devices && projectData.devices.length > 0) {
                        const targetDev = projectData.devices.find(d => (d.category || '').includes('switch')) || projectData.devices.find(d => (d.category || '').includes('router')) || projectData.devices[0];
                        window.ramonetTerminal?.attachDevice(targetDev);
                        window.ramonetCanvas?.selectDevice(targetDev.id, false);
                        this.renderDeviceWebGUI(targetDev);
                        const urlParams = new URLSearchParams(window.location.search);
                        if (urlParams.get('open') === 'cli') {
                            this.showWorkbenchTab('cli-terminal');
                        } else {
                            this.showWorkbenchTab('device-web-gui');
                        }
                    }
                }, 120);
                this.showToast('Topology Ready', `Loaded "${templateName}" with ${projectData.devices?.length || 0} devices.`, 'success');
            } else {
                throw new Error('Template not found on server');
            }
        } catch (e) {
            console.warn('Template API fetch error, building starter topology:', e);
            this.buildDefaultStarterTopology(templateName);
        }
    }

    buildDefaultStarterTopology(name) {
        const starter = {
            id: 'proj_' + Date.now(),
            name: name,
            devices: [
                { id: 'pc1', name: 'PC1', category: 'computers', cli_platform: 'windows_cmd', icon: 'fa-desktop', x: 120, y: 180, ip: '192.168.1.10', subnet_mask: '255.255.255.0', gateway: '192.168.1.1', interfaces: [{ name: 'eth0', ip: '192.168.1.10', mask: '255.255.255.0', status: 'up' }] },
                { id: 'sw1', name: 'Switch1', category: 'switches', cli_platform: 'cisco_ios', icon: 'fa-network-wired', x: 340, y: 180, interfaces: [{ name: 'Fa0/1', status: 'up' }, { name: 'Fa0/2', status: 'up' }, { name: 'Gi0/1', status: 'up' }] },
                { id: 'r1', name: 'Router1', category: 'routers', cli_platform: 'cisco_ios', icon: 'fa-route', x: 560, y: 180, ip: '192.168.1.1', interfaces: [{ name: 'Gi0/0', ip: '192.168.1.1', mask: '255.255.255.0', status: 'up' }, { name: 'Gi0/1', ip: '10.0.0.1', mask: '255.255.255.0', status: 'up' }] },
                { id: 'srv1', name: 'WebServer', category: 'servers', cli_platform: 'linux_shell', icon: 'fa-server', x: 780, y: 180, ip: '10.0.0.100', subnet_mask: '255.255.255.0', gateway: '10.0.0.1', interfaces: [{ name: 'eth0', ip: '10.0.0.100', mask: '255.255.255.0', status: 'up' }] }
            ],
            connections: [
                { id: 'c1', source_device: 'pc1', source_port: 'eth0', target_device: 'sw1', target_port: 'Fa0/1', type: 'copper_straight', status: 'connected' },
                { id: 'c2', source_device: 'sw1', source_port: 'Gi0/1', target_device: 'r1', target_port: 'Gi0/0', type: 'copper_straight', status: 'connected' },
                { id: 'c3', source_device: 'r1', source_port: 'Gi0/1', target_device: 'srv1', target_port: 'eth0', type: 'copper_straight', status: 'connected' }
            ]
        };
        window.ramonetCanvas?.loadProjectData(starter);
        window.ramonetCanvas?.fitToScreen();
        window.ramonetTerminal?.syncDeviceSelector();
        if (starter.devices?.[0]) {
            const targetDev = starter.devices.find(d => (d.category || '').includes('switch')) || starter.devices[0];
            window.ramonetTerminal?.attachDevice(targetDev);
            window.ramonetCanvas?.selectDevice(targetDev.id, false);
            this.renderDeviceWebGUI(targetDev);
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('open') === 'cli') {
                this.showWorkbenchTab('cli-terminal');
            } else {
                this.showWorkbenchTab('device-web-gui');
            }
        }
        this.showToast('Template Generated', `Generated ${name}`, 'success');
    }

    renderDeviceWebGUI(device) {
        const mount = document.getElementById('device-web-gui-mount');
        if (!mount) return;

        if (!device) {
            mount.innerHTML = `
                <div class="p-4 text-center text-secondary d-flex flex-column align-items-center justify-content-center h-100">
                    <div class="mb-3 p-3 rounded-circle bg-dark border border-secondary border-opacity-25" style="width: 64px; height: 64px; display: inline-flex; align-items: center; justify-content: center;">
                        <i class="fa-solid fa-globe fa-2x text-cyan opacity-75"></i>
                    </div>
                    <h6 class="text-white fw-bold mb-1">Device Web GUI · Standby</h6>
                    <p class="small text-muted mb-0" style="max-width: 440px;">
                        Add devices from the library and click any device to launch its real-time Web Management Interface.
                    </p>
                </div>
            `;
            return;
        }

        const devName = device.name || 'Device';
        const devIp = device.ip || '192.168.1.1';
        const cat = (device.category || '').toLowerCase();
        const dNameLow = devName.toLowerCase();
        const picUrl = window.ramonetCanvas?.getDevicePic(device) || '/static/img/devices/switch.svg';

        let innerContent = '';

        if (cat.includes('router') || dNameLow.includes('router')) {
            innerContent = `
                <div class="row g-3">
                    <div class="col-md-4">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <div class="d-flex align-items-center justify-content-between mb-2">
                                <span class="small text-secondary fw-semibold">WAN Interface (Gi0/0)</span>
                                <span class="badge bg-success text-dark">CONNECTED</span>
                            </div>
                            <div class="h5 text-white mb-1">${devIp}</div>
                            <div class="small text-muted">Gateway: ${device.gateway || '203.0.113.1'}</div>
                            <div class="small text-muted">DNS: ${device.dns || '8.8.8.8'}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <div class="d-flex align-items-center justify-content-between mb-2">
                                <span class="small text-secondary fw-semibold">LAN DHCP Server</span>
                                <span class="badge bg-info text-dark">ACTIVE</span>
                            </div>
                            <div class="h5 text-white mb-1">Pool: 192.168.1.0/24</div>
                            <div class="small text-muted">Range: 192.168.1.100 - 192.168.1.200</div>
                            <div class="small text-muted">Lease Time: 24 Hours</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <div class="d-flex align-items-center justify-content-between mb-2">
                                <span class="small text-secondary fw-semibold">Routing Engine</span>
                                <span class="badge bg-purple">OSPF AREA 0</span>
                            </div>
                            <div class="h5 text-white mb-1">Status: Converged</div>
                            <div class="small text-muted">Direct Links: ${(device.interfaces || []).length}</div>
                            <div class="small text-muted">NAT Overload: Enabled</div>
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <h6 class="text-white small fw-bold mb-3"><i class="fa-solid fa-list-check text-cyan me-2"></i>Active Routing Table Entries</h6>
                            <div class="table-responsive">
                                <table class="table table-sm table-dark border-secondary mb-0 small">
                                    <thead>
                                        <tr class="text-secondary">
                                            <th>Type</th>
                                            <th>Destination Prefix</th>
                                            <th>Next Hop</th>
                                            <th>Interface</th>
                                            <th>Metric</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr><td><span class="badge bg-success text-dark">C</span></td><td>${devIp}/24</td><td>Direct Connection</td><td>GigabitEthernet0/0</td><td>0</td></tr>
                                        <tr><td><span class="badge bg-info text-dark">S</span></td><td>0.0.0.0/0</td><td>${device.gateway || '203.0.113.1'}</td><td>GigabitEthernet0/1</td><td>1/0</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else if (cat.includes('switch') || dNameLow.includes('switch')) {
            const ports = Array.from({ length: 24 }, (_, i) => i + 1);
            const portLeds = ports.map(p => {
                const isConnected = p <= 4;
                return `
                    <div class="text-center p-2 rounded border ${isConnected ? 'border-success bg-success bg-opacity-10' : 'border-secondary border-opacity-25 bg-dark'}" style="width: 48px;">
                        <div class="small text-white fw-bold">${p}</div>
                        <i class="fa-solid fa-circle ${isConnected ? 'text-success' : 'text-secondary opacity-50'}" style="font-size:0.55rem;"></i>
                    </div>
                `;
            }).join('');

            innerContent = `
                <div class="p-3 bg-card-secondary rounded border border-accent mb-3">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div>
                            <h6 class="text-white mb-0 fw-bold"><i class="fa-solid fa-network-wired text-cyan me-2"></i>24-Port Gigabit Ethernet Switch Matrix</h6>
                            <small class="text-muted">Visual Front Panel Status (Green = Link Active 1000M Full-Duplex)</small>
                        </div>
                        <span class="badge bg-success text-dark">Spanning Tree: RSTP Root</span>
                    </div>
                    <div class="d-flex flex-wrap gap-2 justify-content-center p-2 bg-dark rounded border border-secondary border-opacity-25">
                        ${portLeds}
                    </div>
                </div>
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <h6 class="text-white small fw-bold mb-2">VLAN Allocation</h6>
                            <table class="table table-sm table-dark border-secondary mb-0 small">
                                <thead><tr class="text-secondary"><th>VLAN ID</th><th>Name</th><th>Ports</th></tr></thead>
                                <tbody>
                                    <tr><td>1</td><td>Default</td><td>Fa0/1 - Fa0/24</td></tr>
                                    <tr><td>10</td><td>Corporate Data</td><td>Gi0/1 - Gi0/2</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <h6 class="text-white small fw-bold mb-2">PoE Power Budget</h6>
                            <div class="d-flex justify-content-between small text-secondary mb-1">
                                <span>Used: 38.5 W</span>
                                <span>Total: 126.0 W</span>
                            </div>
                            <div class="progress mb-2" style="height: 8px;">
                                <div class="progress-bar bg-success" style="width: 30%;"></div>
                            </div>
                            <small class="text-muted">Supplying power to connected IP Cameras & Wireless APs</small>
                        </div>
                    </div>
                </div>
            `;
        } else if (cat.includes('cctv') || dNameLow.includes('nvr') || dNameLow.includes('camera')) {
            innerContent = `
                <div class="row g-3">
                    <div class="col-md-8">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <div class="d-flex align-items-center justify-content-between mb-2">
                                <h6 class="text-white small fw-bold mb-0"><i class="fa-solid fa-video text-warning me-2"></i>Live Video Stream Matrix (H.265 / 4K)</h6>
                                <span class="badge bg-danger"><i class="fa-solid fa-record-vinyl me-1"></i>REC 24/7</span>
                            </div>
                            <div class="row g-2">
                                <div class="col-6">
                                    <div class="bg-black rounded p-3 text-center border border-secondary border-opacity-50 position-relative" style="min-height: 120px;">
                                        <div class="position-absolute top-0 start-0 p-1 small text-info font-monospace" style="font-size:0.65rem;">CH-01: Main Entrance</div>
                                        <div class="position-absolute bottom-0 end-0 p-1 small text-success font-monospace" style="font-size:0.65rem;">3840x2160 · 30 FPS</div>
                                        <i class="fa-solid fa-building-user text-secondary opacity-50 fa-2x my-3"></i>
                                    </div>
                                </div>
                                <div class="col-6">
                                    <div class="bg-black rounded p-3 text-center border border-secondary border-opacity-50 position-relative" style="min-height: 120px;">
                                        <div class="position-absolute top-0 start-0 p-1 small text-info font-monospace" style="font-size:0.65rem;">CH-02: Server Room</div>
                                        <div class="position-absolute bottom-0 end-0 p-1 small text-success font-monospace" style="font-size:0.65rem;">3840x2160 · 30 FPS</div>
                                        <i class="fa-solid fa-server text-secondary opacity-50 fa-2x my-3"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="p-3 bg-card-secondary rounded border border-accent h-100">
                            <h6 class="text-white small fw-bold mb-2">Surveillance Storage</h6>
                            <div class="d-flex justify-content-between small text-secondary mb-1">
                                <span>Used: 18.4 TB</span>
                                <span>Max: 32.0 TB</span>
                            </div>
                            <div class="progress mb-3" style="height: 8px;">
                                <div class="progress-bar bg-warning" style="width: 57%;"></div>
                            </div>
                            <div class="small text-muted mb-1"><i class="fa-solid fa-check text-success me-1"></i>RAID 5 Health: Optimal</div>
                            <div class="small text-muted mb-1"><i class="fa-solid fa-clock text-info me-1"></i>Retention: 42 Days</div>
                            <div class="small text-muted"><i class="fa-solid fa-network-wired text-cyan me-1"></i>RTSP Port: 554 (Open)</div>
                        </div>
                    </div>
                </div>
            `;
        } else if (cat.includes('server') || dNameLow.includes('server')) {
            innerContent = `
                <div class="row g-3">
                    <div class="col-md-4">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <div class="small text-secondary mb-1">CPU Load (8 Cores)</div>
                            <div class="h4 text-white mb-2">18.4%</div>
                            <div class="progress" style="height: 6px;"><div class="progress-bar bg-success" style="width: 18%;"></div></div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <div class="small text-secondary mb-1">Memory Utilization</div>
                            <div class="h4 text-white mb-2">4.2 / 16.0 GB</div>
                            <div class="progress" style="height: 6px;"><div class="progress-bar bg-info" style="width: 26%;"></div></div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <div class="small text-secondary mb-1">System Uptime</div>
                            <div class="h4 text-white mb-2">14d 06h 22m</div>
                            <span class="badge bg-success text-dark">HEALTHY</span>
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <h6 class="text-white small fw-bold mb-2">Listening Network Services</h6>
                            <div class="d-flex flex-wrap gap-2">
                                <span class="badge bg-dark border border-secondary text-white p-2"><i class="fa-solid fa-globe text-cyan me-1"></i>Nginx Web (Port 80/443) - RUNNING</span>
                                <span class="badge bg-dark border border-secondary text-white p-2"><i class="fa-solid fa-server text-purple me-1"></i>BIND9 DNS (Port 53) - RUNNING</span>
                                <span class="badge bg-dark border border-secondary text-white p-2"><i class="fa-solid fa-terminal text-warning me-1"></i>OpenSSH (Port 22) - RUNNING</span>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else if (cat.includes('firewall') || dNameLow.includes('firewall')) {
            innerContent = `
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <div class="d-flex align-items-center justify-content-between mb-2">
                                <h6 class="text-white small fw-bold mb-0">Stateful Inspection Firewall</h6>
                                <span class="badge bg-danger">DEFAULT DENY</span>
                            </div>
                            <table class="table table-sm table-dark border-secondary mb-0 small">
                                <thead><tr class="text-secondary"><th>Rule</th><th>Source</th><th>Dest</th><th>Action</th></tr></thead>
                                <tbody>
                                    <tr><td>1</td><td>LAN (192.168.1.0/24)</td><td>ANY (Internet)</td><td><span class="badge bg-success text-dark">ALLOW</span></td></tr>
                                    <tr><td>2</td><td>WAN (Internet)</td><td>DMZ Web (Port 80)</td><td><span class="badge bg-success text-dark">ALLOW</span></td></tr>
                                    <tr><td>3</td><td>ANY</td><td>ANY</td><td><span class="badge bg-danger">DROP</span></td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <h6 class="text-white small fw-bold mb-2">Security & VPN Tunnels</h6>
                            <div class="small text-muted mb-1"><i class="fa-solid fa-shield-halved text-success me-1"></i>Intrusion Prevention: Active (0 Threats)</div>
                            <div class="small text-muted mb-1"><i class="fa-solid fa-lock text-info me-1"></i>IPsec Site-to-Site VPN: 1 Tunnel Connected</div>
                            <div class="small text-muted"><i class="fa-solid fa-network-wired text-cyan me-1"></i>Active Connections in Table: 24 Sockets</div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // General Endpoint / PC / Printer / Storage
            innerContent = `
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <h6 class="text-white small fw-bold mb-3"><i class="fa-solid fa-network-wired text-cyan me-2"></i>Network Adapter Configuration</h6>
                            <div class="small text-secondary mb-1">IPv4 Address: <strong class="text-white font-monospace">${devIp}</strong></div>
                            <div class="small text-secondary mb-1">Subnet Mask: <strong class="text-white font-monospace">${device.subnet_mask || '255.255.255.0'}</strong></div>
                            <div class="small text-secondary mb-1">Default Gateway: <strong class="text-white font-monospace">${device.gateway || '192.168.1.1'}</strong></div>
                            <div class="small text-secondary">DNS Server: <strong class="text-white font-monospace">${device.dns || '8.8.8.8'}</strong></div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="p-3 bg-card-secondary rounded border border-accent">
                            <h6 class="text-white small fw-bold mb-3"><i class="fa-solid fa-heart-pulse text-success me-2"></i>Device Operational State</h6>
                            <div class="small text-muted mb-1"><i class="fa-solid fa-circle-check text-success me-1"></i>Status: ONLINE & RESPONSIVE</div>
                            <div class="small text-muted mb-1"><i class="fa-solid fa-bolt text-warning me-1"></i>Power Draw: ${device.power_watts || 25} Watts</div>
                            <div class="small text-muted"><i class="fa-solid fa-diagram-project text-info me-1"></i>Category: ${device.category || 'General'}</div>
                        </div>
                    </div>
                </div>
            `;
        }

        mount.innerHTML = `
            <div class="device-web-gui-container bg-dark rounded border border-secondary border-opacity-50 overflow-hidden shadow">
                <!-- Browser Header Bar -->
                <div class="web-gui-browser-bar bg-sidebar p-2 d-flex align-items-center gap-2 border-bottom border-secondary border-opacity-25">
                    <div class="d-flex align-items-center gap-1 text-secondary me-2">
                        <i class="fa-solid fa-arrow-left small cursor-pointer opacity-50"></i>
                        <i class="fa-solid fa-arrow-right small cursor-pointer opacity-50"></i>
                        <i class="fa-solid fa-rotate-right small cursor-pointer hover-text-white" title="Refresh GUI" onclick="window.ramonetUI.renderDeviceWebGUI(window.ramonetCanvas.selectedDevice)"></i>
                    </div>
                    <div class="flex-grow-1 bg-dark px-2 py-1 rounded text-white small font-monospace d-flex align-items-center justify-content-between border border-secondary border-opacity-25" style="max-width: 500px;">
                        <span><i class="fa-solid fa-lock text-success me-2"></i>https://${devIp}:443/admin</span>
                        <span class="badge bg-secondary font-monospace" style="font-size:0.65rem;">SSL / TLS 1.3</span>
                    </div>
                    <div class="ms-auto d-flex align-items-center gap-2">
                        <span class="badge bg-success text-dark"><i class="fa-solid fa-circle me-1" style="font-size:0.5rem;"></i>ONLINE</span>
                    </div>
                </div>

                <!-- Web GUI App Workspace Header -->
                <div class="p-3 bg-sidebar border-bottom border-secondary border-opacity-25 d-flex align-items-center justify-content-between">
                    <div class="d-flex align-items-center gap-3">
                        <img src="${picUrl}" class="palette-device-pic" alt="${devName}">
                        <div>
                            <h5 class="text-white fw-bold mb-0">${devName} Web Management Portal</h5>
                            <small class="text-muted">Hardware: ${device.model_name || device.category || 'Enterprise Appliance'} · Firmware v2.0</small>
                        </div>
                    </div>
                    <button class="btn btn-sm btn-outline-cyan" onclick="window.ramonetUI.showToast('Configuration Saved', 'Device web parameters updated successfully.', 'success')">
                        <i class="fa-solid fa-floppy-disk me-1"></i>Save Configuration
                    </button>
                </div>

                <!-- Web GUI App Workspace Body -->
                <div class="p-3">
                    ${innerContent}
                </div>
            </div>
        `;
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.ramonetUI = new RamonetUI();
});
