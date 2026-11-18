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

    updateSelectedDevice(device) {
        this.selectedDevice = device;
        const panel = document.getElementById('device-inspector-panel');
        if (!panel) return;

        if (!device) {
            panel.classList.add('closed');
            window.ramonetTerminal?.attachDevice(null);
            return;
        }

        panel.classList.remove('closed');
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
        if (categoryInput) categoryInput.value = (device.category || 'Endpoint') + (device.is_layer3 ? ' (Layer 3 Routing)' : '');
        if (powerEl) powerEl.textContent = `${device.power_watts || 25} W`;
        if (poeEl) poeEl.textContent = `${device.poe_budget_watts || 0} W`;
        if (ipInput) ipInput.value = device.ip || '';
        if (maskInput) maskInput.value = device.subnet_mask || '255.255.255.0';
        if (gwInput) gwInput.value = device.gateway || '';
        if (dnsInput) dnsInput.value = device.dns || '8.8.8.8';
        if (iconEl) iconEl.className = `fa-solid ${device.icon || 'fa-server'}`;

        const ifcCount = (device.interfaces || []).length;
        if (ifcCountBadge) ifcCountBadge.textContent = `${ifcCount} port${ifcCount === 1 ? '' : 's'}`;

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

    openConnectModal(srcDevice, destDevice, onConfirm) {
        const modalEl = document.getElementById('connectCableModal');
        if (!modalEl) return;

        document.getElementById('connect-src-name').textContent = srcDevice.name;
        document.getElementById('connect-dest-name').textContent = destDevice.name;

        // Populate interface dropdowns
        const srcPortSel = document.getElementById('connect-src-port');
        const destPortSel = document.getElementById('connect-dest-port');

        srcPortSel.innerHTML = (srcDevice.interfaces || [{ name: 'eth0' }]).map(i => `<option value="${i.name}">${i.name} (${i.speed || 1000}M)</option>`).join('');
        destPortSel.innerHTML = (destDevice.interfaces || [{ name: 'eth0' }]).map(i => `<option value="${i.name}">${i.name} (${i.speed || 1000}M)</option>`).join('');

        const confirmBtn = document.getElementById('btn-confirm-connect');
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        const bsModal = new bootstrap.Modal(modalEl);
        newConfirmBtn.addEventListener('click', () => {
            const cableType = document.getElementById('connect-cable-type').value;
            const srcPort = srcPortSel.value;
            const destPort = destPortSel.value;
            bsModal.hide();
            onConfirm(cableType, srcPort, destPort);
        });

        bsModal.show();
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
        this.showToast('Loading Template', `Generating ${templateName}...`, 'info');
        try {
            const resp = await fetch(`/api/projects/template/?name=${encodeURIComponent(templateName)}`);
            if (resp.ok) {
                const projectData = await resp.json();
                window.ramonetCanvas?.loadProjectData(projectData);
                window.ramonetCanvas?.fitToScreen();
                this.showToast('Template Loaded', `Loaded "${templateName}" with ${projectData.devices?.length || 0} devices.`, 'success');
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
                { id: 'pc1', name: 'PC1', category: 'computers', icon: 'fa-desktop', x: 120, y: 180, ip: '192.168.1.10', subnet_mask: '255.255.255.0', gateway: '192.168.1.1', interfaces: [{ name: 'eth0', status: 'up' }] },
                { id: 'sw1', name: 'Switch1', category: 'switches', icon: 'fa-network-wired', x: 340, y: 180, interfaces: [{ name: 'Fa0/1', status: 'up' }, { name: 'Fa0/2', status: 'up' }, { name: 'Gi0/1', status: 'up' }] },
                { id: 'r1', name: 'Router1', category: 'routers', icon: 'fa-route', x: 560, y: 180, ip: '192.168.1.1', interfaces: [{ name: 'Gi0/0', ip: '192.168.1.1', mask: '255.255.255.0', status: 'up' }, { name: 'Gi0/1', ip: '10.0.0.1', mask: '255.255.255.0', status: 'up' }] },
                { id: 'srv1', name: 'WebServer', category: 'servers', icon: 'fa-server', x: 780, y: 180, ip: '10.0.0.100', subnet_mask: '255.255.255.0', gateway: '10.0.0.1', interfaces: [{ name: 'eth0', status: 'up' }] }
            ],
            connections: [
                { id: 'c1', source_device: 'pc1', source_port: 'eth0', target_device: 'sw1', target_port: 'Fa0/1', type: 'copper_straight', status: 'connected' },
                { id: 'c2', source_device: 'sw1', source_port: 'Gi0/1', target_device: 'r1', target_port: 'Gi0/0', type: 'copper_straight', status: 'connected' },
                { id: 'c3', source_device: 'r1', source_port: 'Gi0/1', target_device: 'srv1', target_port: 'eth0', type: 'copper_straight', status: 'connected' }
            ]
        };
        window.ramonetCanvas?.loadProjectData(starter);
        window.ramonetCanvas?.fitToScreen();
        this.showToast('Template Generated', `Generated ${name}`, 'success');
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.ramonetUI = new RamonetUI();
});
