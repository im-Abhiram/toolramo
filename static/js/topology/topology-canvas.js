/**
 * Ramonet Interactive Network Topology Canvas
 * Vanilla JavaScript + SVG + HTML5 Canvas hybrid renderer.
 * Cisco Packet Tracer & GNS3-inspired network infrastructure designer.
 */

class TopologyCanvas {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;

        this.svg = document.getElementById('topology-svg');
        this.nodesContainer = document.getElementById('topology-nodes-container');
        this.minimap = document.getElementById('topology-minimap-canvas');

        // Project State
        this.project = {
            id: options.projectId || 'proj_' + Date.now(),
            name: options.projectName || 'Untitled Network Topology',
            devices: [],
            connections: []
        };

        // Canvas Viewport Transformation
        this.panX = 0;
        this.panY = 0;
        this.scale = 1.0;
        this.minScale = 0.3;
        this.maxScale = 2.5;

        // Interaction Modes
        this.mode = 'select'; // 'select', 'pan', 'connect'
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.connectSource = null; // { deviceId, portName }

        // History for Undo / Redo
        this.history = [];
        this.historyIndex = -1;
        this.maxHistory = 30;

        // Dragging State
        this.isDraggingNode = false;
        this.dragTargetNode = null;
        this.dragOffset = { x: 0, y: 0 };
        this.isPanningCanvas = false;
        this.panStart = { x: 0, y: 0 };

        // Grid
        this.gridSize = 24;
        this.snapToGrid = true;

        // Autosave debouncer
        this.debouncedSave = window.ramonetStorage.createDebouncedSaver(
            (proj) => window.ramonetStorage.saveProject(proj),
            750
        );

        this.initEventListeners();
        this.pushHistoryState('Initial State');
        this.updateModeIndicator();
    }

    initEventListeners() {
        // Panning with Mouse Drag
        this.container.addEventListener('mousedown', (e) => {
            if (e.target === this.container || e.target === this.svg || e.target.closest('#topology-svg') || e.target.classList.contains('canvas-container')) {
                if (e.button === 0 || e.button === 1) { // Left click on background or Middle click
                    this.isPanningCanvas = true;
                    this.panStart = { x: e.clientX - this.panX, y: e.clientY - this.panY };
                    this.container.classList.add('panning');
                    this.deselectAll();
                }
            }
        });

        window.addEventListener('mousemove', (e) => {
            if (this.isPanningCanvas) {
                this.panX = e.clientX - this.panStart.x;
                this.panY = e.clientY - this.panStart.y;
                this.applyTransform();
                this.renderMinimap();
            } else if (this.isDraggingNode && this.dragTargetNode) {
                const rect = this.container.getBoundingClientRect();
                let x = (e.clientX - rect.left - this.panX) / this.scale - this.dragOffset.x;
                let y = (e.clientY - rect.top - this.panY) / this.scale - this.dragOffset.y;

                if (this.snapToGrid) {
                    x = Math.round(x / this.gridSize) * this.gridSize;
                    y = Math.round(y / this.gridSize) * this.gridSize;
                }

                this.dragTargetNode.x = Math.max(10, x);
                this.dragTargetNode.y = Math.max(10, y);
                this.updateNodeElementPosition(this.dragTargetNode);
                this.renderConnections();
                this.renderMinimap();
            } else if (this.mode === 'connect' && this.connectSource) {
                const rect = this.container.getBoundingClientRect();
                const mouseX = (e.clientX - rect.left - this.panX) / this.scale;
                const mouseY = (e.clientY - rect.top - this.panY) / this.scale;
                this.updateTempCable(this.connectSource.x + 50, this.connectSource.y + 42, mouseX, mouseY);
            }
        });

        window.addEventListener('mouseup', (e) => {
            if (this.isPanningCanvas) {
                this.isPanningCanvas = false;
                this.container.classList.remove('panning');
            }
            if (this.isDraggingNode) {
                this.isDraggingNode = false;
                this.dragTargetNode = null;
                this.triggerChange('Device Moved');
            }
            if (this.isDraggingCable) {
                this.isDraggingCable = false;
            }
        });

        // Zoom with Mouse Wheel
        this.container.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomFactor = 1.1;
            const direction = e.deltaY > 0 ? (1 / zoomFactor) : zoomFactor;
            this.zoomAtPoint(direction, e.clientX, e.clientY);
        }, { passive: false });

        // Drag and Drop from Sidebar Palette
        this.container.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'copy';
            this.container.classList.add('drag-over-active');
        });

        this.container.addEventListener('dragleave', (e) => {
            if (e.target === this.container) {
                this.container.classList.remove('drag-over-active');
            }
        });

        this.container.addEventListener('drop', (e) => {
            e.preventDefault();
            this.container.classList.remove('drag-over-active');

            let devData = null;
            const rawData = e.dataTransfer.getData('application/json') || e.dataTransfer.getData('text/plain');
            if (rawData) {
                try {
                    devData = JSON.parse(rawData);
                } catch (err) {
                    console.warn('Could not parse drop JSON:', err);
                }
            }

            // Fallback to in-memory dragged object
            if (!devData && window.__draggedDeviceDefinition) {
                devData = window.__draggedDeviceDefinition;
            }

            if (!devData) return;

            try {
                const rect = this.container.getBoundingClientRect();
                const dropX = (e.clientX - rect.left - this.panX) / this.scale - 50;
                const dropY = (e.clientY - rect.top - this.panY) / this.scale - 40;

                const added = this.addDevice(devData, Math.max(20, Math.round(dropX)), Math.max(20, Math.round(dropY)));
                window.ramonetUI?.showToast('Device Placed', `${added.name} placed on canvas.`, 'success');
            } catch (err) {
                console.error('Drop device failed:', err);
            } finally {
                window.__draggedDeviceDefinition = null;
            }
        });

        // Keyboard Shortcuts (Delete, Undo, Redo, Duplicate)
        window.addEventListener('keydown', (e) => {
            // Check if user is typing in an input or terminal
            if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

            if (e.key === 'Escape') {
                if (this.mode === 'connect') {
                    this.cancelConnectMode();
                }
                this.deselectAll();
            } else if (e.key === 'Delete' || e.key === 'Backspace') {
                if (this.selectedDevice) {
                    this.deleteDevice(this.selectedDevice.id);
                } else if (this.selectedConnection) {
                    this.deleteConnection(this.selectedConnection.id);
                }
            } else if (e.ctrlKey && e.key.toLowerCase() === 'z') {
                e.preventDefault();
                this.undo();
            } else if (e.ctrlKey && e.key.toLowerCase() === 'y') {
                e.preventDefault();
                this.redo();
            } else if (e.ctrlKey && e.key.toLowerCase() === 'd') {
                e.preventDefault();
                if (this.selectedDevice) {
                    this.duplicateDevice(this.selectedDevice.id);
                }
            }
        });
    }

    applyTransform() {
        if (this.nodesContainer) {
            this.nodesContainer.style.transform = `translate(${this.panX}px, ${this.panY}px) scale(${this.scale})`;
            this.nodesContainer.style.transformOrigin = '0 0';
        }
        if (this.svg) {
            const g = this.svg.querySelector('g.transform-group');
            if (g) {
                g.setAttribute('transform', `translate(${this.panX}, ${this.panY}) scale(${this.scale})`);
            }
        }
    }

    zoomAtPoint(direction, clientX, clientY) {
        const newScale = Math.min(Math.max(this.scale * direction, this.minScale), this.maxScale);
        if (newScale === this.scale) return;

        const rect = this.container.getBoundingClientRect();
        const mouseX = clientX - rect.left;
        const mouseY = clientY - rect.top;

        this.panX = mouseX - (mouseX - this.panX) * (newScale / this.scale);
        this.panY = mouseY - (mouseY - this.panY) * (newScale / this.scale);
        this.scale = newScale;

        this.applyTransform();
        this.renderMinimap();
    }

    resetZoom() {
        this.panX = 50;
        this.panY = 50;
        this.scale = 1.0;
        this.applyTransform();
        this.renderMinimap();
    }

    fitToScreen() {
        if (this.project.devices.length === 0) {
            this.resetZoom();
            return;
        }

        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        this.project.devices.forEach(d => {
            minX = Math.min(minX, d.x);
            minY = Math.min(minY, d.y);
            maxX = Math.max(maxX, d.x + 90);
            maxY = Math.max(maxY, d.y + 80);
        });

        const pad = 60;
        const bboxW = (maxX - minX) + pad * 2;
        const bboxH = (maxY - minY) + pad * 2;
        const contW = this.container.clientWidth || 1000;
        const contH = this.container.clientHeight || 700;

        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;

        this.scale = Math.min(Math.max(Math.min(contW / bboxW, contH / bboxH), 0.4), 1.2);
        this.panX = (contW / 2) - (centerX * this.scale);
        this.panY = (contH / 2) - (centerY * this.scale);

        this.applyTransform();
        this.renderMinimap();
    }

    // ================= DEVICE MANAGEMENT =================

    addDevice(definition, x = 100, y = 100) {
        const type = (definition.device_type || definition.type || '').toLowerCase();
        const category = (definition.category || '').toLowerCase();
        const modelName = (definition.model_name || definition.name || '').toLowerCase();
        
        let prefix = 'PC';
        let devIcon = definition.icon || 'fa-server';
        let devCat = category || 'computers';

        if (type.includes('nvr') || modelName.includes('nvr') || category.includes('nvr')) {
            prefix = 'NVR';
            devIcon = 'fa-hard-drive';
            devCat = 'cctv';
        } else if (type.includes('camera') || modelName.includes('camera') || category.includes('camera') || category.includes('cctv')) {
            prefix = 'Camera';
            devIcon = 'fa-video';
            devCat = 'cctv';
        } else if (category.includes('switch') || type.includes('switch') || modelName.includes('switch')) {
            prefix = 'Switch';
            devIcon = 'fa-network-wired';
            devCat = 'switches';
        } else if (category.includes('router') || type.includes('router') || modelName.includes('router')) {
            prefix = 'Router';
            devIcon = 'fa-route';
            devCat = 'routers';
        } else if (category.includes('firewall') || type.includes('firewall') || modelName.includes('firewall')) {
            prefix = 'Firewall';
            devIcon = 'fa-shield-halved';
            devCat = 'firewalls';
        } else if (type.includes('nas') || modelName.includes('nas') || category.includes('storage')) {
            prefix = 'NAS';
            devIcon = 'fa-hard-drive';
            devCat = 'storage';
        } else if (category.includes('printer') || type.includes('printer') || modelName.includes('printer')) {
            prefix = 'Printer';
            devIcon = 'fa-print';
            devCat = 'printers';
        } else if (category.includes('server') || type.includes('server') || modelName.includes('server')) {
            prefix = 'Server';
            devIcon = 'fa-server';
            devCat = 'servers';
        } else if (category.includes('wireless') || type.includes('ap') || type.includes('access_point') || modelName.includes('ap')) {
            prefix = 'AP';
            devIcon = 'fa-wifi';
            devCat = 'wireless';
        } else {
            prefix = 'PC';
            devIcon = 'fa-desktop';
            devCat = 'computers';
        }

        const count = this.project.devices.filter(d => (d.name || '').startsWith(prefix)).length + 1;
        const deviceId = 'dev_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
        const deviceName = `${prefix}${count}`;

        // Clone interfaces
        const interfaces = (definition.available_interfaces || [
            { name: 'eth0', type: 'copper', speed: 1000, status: 'up' }
        ]).map(ifc => ({ ...ifc, status: 'up' }));

        const newDevice = {
            id: deviceId,
            name: deviceName,
            definition_id: definition.id,
            category: devCat,
            model_name: definition.model_name || definition.name,
            icon: devIcon,
            cli_platform: definition.cli_platform || (devCat === 'computers' ? 'windows_cmd' : (devCat === 'servers' ? 'linux_shell' : 'cisco_ios')),
            is_layer3: definition.is_layer3 || false,
            power_watts: definition.power_watts || 25,
            poe_budget_watts: definition.poe_budget_watts || 0,
            x: Math.round(x),
            y: Math.round(y),
            ip: definition.default_config?.ip || '',
            subnet_mask: definition.default_config?.subnet_mask || '255.255.255.0',
            gateway: definition.default_config?.gateway || '',
            dns: '8.8.8.8',
            interfaces: interfaces,
            routes: definition.default_config?.routes || [],
            vlans: definition.default_config?.vlans || {'1': { name: 'default' }},
            firewall_rules: definition.default_config?.firewall_rules || [],
            running_config: definition.default_config || {}
        };

        this.project.devices.push(newDevice);
        this.renderDeviceNode(newDevice);
        this.renderMinimap();
        this.selectDevice(newDevice.id);
        window.ramonetTerminal?.syncDeviceSelector();
        this.triggerChange(`Added ${deviceName}`);
        return newDevice;
    }

    renderDeviceNode(device) {
        if (!this.nodesContainer) return;

        let el = document.getElementById(device.id);
        if (!el) {
            el = document.createElement('div');
            el.id = device.id;
            el.className = `device-node ${this.getCategoryClass(device.category)}`;
            el.style.pointerEvents = 'auto';
            el.innerHTML = `
                <div class="port-connector-anchor top" data-anchor="top" title="Connect Cable (+)"><i class="fa-solid fa-plus"></i></div>
                <div class="port-connector-anchor bottom" data-anchor="bottom" title="Connect Cable (+)"><i class="fa-solid fa-plus"></i></div>
                <div class="port-connector-anchor left" data-anchor="left" title="Connect Cable (+)"><i class="fa-solid fa-plus"></i></div>
                <div class="port-connector-anchor right" data-anchor="right" title="Connect Cable (+)"><i class="fa-solid fa-plus"></i></div>
                <span class="node-status-beacon" title="Node Online: Operational"><span class="node-status-dot"></span></span>
                <div class="device-node-pic">
                    <img src="${this.getDevicePic(device)}" class="device-pic" alt="${device.name}" draggable="false">
                </div>
                <div class="device-node-name" title="${device.name}">${device.name}</div>
                <div class="device-node-ip" title="${device.ip || 'No IP'}">${device.ip || '---'}</div>
            `;
            this.nodesContainer.appendChild(el);

            // Anchor direct connection click & drag
            el.querySelectorAll('.port-connector-anchor').forEach(anchor => {
                anchor.addEventListener('mousedown', (e) => {
                    e.stopPropagation();
                    e.preventDefault();
                    if (!this.connectSource) {
                        this.startConnectMode();
                        this.connectSource = device;
                        el.classList.add('connecting-source');
                        window.ramonetUI?.showToast('Select Destination', `Connecting from ${device.name}. Click or drag to target device (+)`, 'info');
                    } else if (String(this.connectSource.id) !== String(device.id)) {
                        const src = this.connectSource;
                        const dest = device;
                        const srcEl = document.getElementById(src.id);
                        if (srcEl) srcEl.classList.remove('connecting-source');
                        this.removeTempCable();
                        this.cancelConnectMode();
                        window.ramonetUI?.openConnectModal(src, dest, (cableType, srcPort, destPort) => {
                            this.createConnection(src.id, srcPort, dest.id, destPort, cableType);
                        });
                        return;
                    }
                    this.isDraggingCable = true;
                });

                anchor.addEventListener('mouseup', (e) => {
                    if (this.connectSource && String(this.connectSource.id) !== String(device.id)) {
                        e.stopPropagation();
                        this.isDraggingCable = false;
                        const src = this.connectSource;
                        const dest = device;
                        const srcEl = document.getElementById(src.id);
                        if (srcEl) srcEl.classList.remove('connecting-source');
                        this.removeTempCable();
                        this.cancelConnectMode();
                        window.ramonetUI?.openConnectModal(src, dest, (cableType, srcPort, destPort) => {
                            this.createConnection(src.id, srcPort, dest.id, destPort, cableType);
                        });
                    }
                });
            });

            // Node mouseup when dragging cable to body of device
            el.addEventListener('mouseup', (e) => {
                if (this.isDraggingCable && this.connectSource && String(this.connectSource.id) !== String(device.id)) {
                    e.stopPropagation();
                    this.isDraggingCable = false;
                    const src = this.connectSource;
                    const dest = device;
                    const srcEl = document.getElementById(src.id);
                    if (srcEl) srcEl.classList.remove('connecting-source');
                    this.removeTempCable();
                    this.cancelConnectMode();
                    window.ramonetUI?.openConnectModal(src, dest, (cableType, srcPort, destPort) => {
                        this.createConnection(src.id, srcPort, dest.id, destPort, cableType);
                    });
                }
            });

            // Node Drag Events
            el.addEventListener('mousedown', (e) => {
                if (e.button !== 0) return; // Only left click
                e.stopPropagation();

                if (this.mode === 'connect') {
                    this.handleConnectClick(device);
                    return;
                }

                this.selectDevice(device.id, true);
                this.isDraggingNode = true;
                this.dragTargetNode = device;
                this.dragOffset = {
                    x: (e.clientX - this.container.getBoundingClientRect().left - this.panX) / this.scale - device.x,
                    y: (e.clientY - this.container.getBoundingClientRect().top - this.panY) / this.scale - device.y
                };
            });

            // Double Click opens Inspector
            el.addEventListener('dblclick', (e) => {
                e.stopPropagation();
                this.selectDevice(device.id);
                window.ramonetUI?.openDeviceInspector(device);
            });

            // Context Menu
            el.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.selectDevice(device.id);
                this.showContextMenu(e.clientX, e.clientY, device);
            });
        }

        this.updateNodeElementPosition(device);
    }

    updateNodeElementPosition(device) {
        const el = document.getElementById(device.id);
        if (!el) return;
        el.style.left = `${device.x}px`;
        el.style.top = `${device.y}px`;

        // Update displayed name & IP
        const nameEl = el.querySelector('.device-node-name');
        if (nameEl) nameEl.textContent = device.name;
        const ipEl = el.querySelector('.device-node-ip');
        if (ipEl) ipEl.textContent = device.ip || '---';

        // Ensure picture is up-to-date
        const picEl = el.querySelector('.device-pic');
        if (picEl) {
            picEl.src = this.getDevicePic(device);
        } else {
            const iconEl = el.querySelector('.device-node-icon');
            if (iconEl) {
                iconEl.className = 'device-node-pic';
                iconEl.innerHTML = `<img src="${this.getDevicePic(device)}" class="device-pic" alt="${device.name}" draggable="false">`;
            }
        }
    }

    getDevicePic(device) {
        if (!device) return '/static/img/devices/switch.svg';
        const cat = (device.category || '').toLowerCase();
        const type = (device.device_type || device.type || '').toLowerCase();
        const name = (device.name || '').toLowerCase();
        const model = (device.model_name || '').toLowerCase();

        if (name.includes('nvr') || model.includes('nvr') || type.includes('nvr')) return '/static/img/devices/nvr.svg';
        if (cat.includes('cctv') || cat.includes('camera') || type.includes('camera') || name.includes('cam')) return '/static/img/devices/camera.svg';
        if (cat.includes('switch') || type.includes('switch') || name.includes('switch') || name.startsWith('sw')) return '/static/img/devices/switch.svg';
        if (cat.includes('router') || type.includes('router') || name.includes('router') || name.startsWith('r')) return '/static/img/devices/router.svg';
        if (cat.includes('firewall') || type.includes('firewall') || name.includes('fw')) return '/static/img/devices/firewall.svg';
        if (cat.includes('server') || type.includes('server') || name.includes('srv') || name.includes('server')) return '/static/img/devices/server.svg';
        if (cat.includes('storage') || cat.includes('nas') || type.includes('nas')) return '/static/img/devices/storage.svg';
        if (cat.includes('printer') || type.includes('printer') || name.includes('print')) return '/static/img/devices/printer.svg';
        if (cat.includes('wireless') || cat.includes('ap') || type.includes('ap') || name.includes('ap')) return '/static/img/devices/wireless.svg';
        if (name.includes('laptop') || model.includes('laptop')) return '/static/img/devices/laptop.svg';
        if (cat.includes('cloud') || name.includes('internet') || name.includes('wan') || name.includes('cloud')) return '/static/img/devices/cloud.svg';
        if (cat.includes('computer') || cat.includes('endpoint') || name.includes('pc')) return '/static/img/devices/pc.svg';
        return '/static/img/devices/switch.svg';
    }

    getCategoryClass(category = '') {
        const cat = category.toLowerCase();
        if (cat.includes('switch')) return 'switch';
        if (cat.includes('router')) return 'router';
        if (cat.includes('firewall')) return 'firewall';
        if (cat.includes('cctv') || cat.includes('camera') || cat.includes('nvr')) return 'cctv';
        if (cat.includes('server')) return 'server';
        if (cat.includes('storage') || cat.includes('nas')) return 'storage';
        if (cat.includes('wireless') || cat.includes('ap')) return 'wireless';
        return 'computer';
    }

    selectDevice(deviceId, openInspector = true) {
        this.deselectAll(false);
        this.selectedDevice = this.project.devices.find(d => d.id === deviceId);
        if (this.selectedDevice) {
            const el = document.getElementById(deviceId);
            if (el) el.classList.add('selected');
            this.updateModeIndicator();
            window.ramonetUI?.updateSelectedDevice(this.selectedDevice, openInspector);
        }
    }

    deleteDevice(deviceId) {
        const index = this.project.devices.findIndex(d => d.id === deviceId);
        if (index === -1) return;

        const devName = this.project.devices[index].name;

        // Remove DOM element
        const el = document.getElementById(deviceId);
        if (el) el.remove();

        // Remove connected cables
        const strId = String(deviceId);
        this.project.connections = this.project.connections.filter(c => {
            const s = String(c.source_device || c.from || c.source || '');
            const t = String(c.target_device || c.to || c.target || '');
            return s !== strId && t !== strId;
        });

        this.project.devices.splice(index, 1);
        this.selectedDevice = null;
        this.renderConnections();
        this.renderMinimap();
        window.ramonetUI?.updateSelectedDevice(null);
        window.ramonetTerminal?.syncDeviceSelector();
        this.triggerChange(`Deleted ${devName}`);
    }

    duplicateDevice(deviceId) {
        const original = this.project.devices.find(d => d.id === deviceId);
        if (!original) return;

        const clone = JSON.parse(JSON.stringify(original));
        clone.id = 'dev_' + Date.now();
        clone.name = original.name + '_Copy';
        clone.x = original.x + 40;
        clone.y = original.y + 40;
        if (clone.ip) {
            // Append or bump IP
            const parts = clone.ip.split('.');
            if (parts.length === 4) {
                parts[3] = Math.min(250, parseInt(parts[3]) + 1);
                clone.ip = parts.join('.');
            }
        }

        this.project.devices.push(clone);
        this.renderDeviceNode(clone);
        this.renderMinimap();
        this.selectDevice(clone.id);
        this.triggerChange(`Duplicated ${original.name}`);
    }

    deselectAll(notifyUI = true) {
        document.querySelectorAll('.device-node.selected').forEach(el => el.classList.remove('selected'));
        if (this.svg) {
            this.svg.querySelectorAll('.cable-line.selected').forEach(el => el.classList.remove('selected'));
        }
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.hideContextMenu();
        this.updateModeIndicator();
        if (notifyUI) {
            window.ramonetUI?.updateSelectedDevice(null);
        }
    }

    // ================= CONNECTIONS & CABLING =================

    startConnectMode() {
        this.mode = 'connect';
        this.connectSource = null;
        this.container.classList.add('connecting-mode');

        const connectBtn = document.getElementById('btn-mode-connect');
        const selectBtn = document.getElementById('btn-mode-select');
        if (connectBtn) connectBtn.classList.add('active');
        if (selectBtn) selectBtn.classList.remove('active');

        this.updateModeIndicator();
        window.ramonetUI?.showToast('Cable Tool Active', '1) Click the first device. 2) Click the second device to attach cable.', 'info');
    }

    cancelConnectMode() {
        this.mode = 'select';
        if (this.connectSource) {
            const el = document.getElementById(this.connectSource.id);
            if (el) el.classList.remove('connecting-source');
        }
        this.connectSource = null;
        this.removeTempCable();
        this.container.classList.remove('connecting-mode');

        const connectBtn = document.getElementById('btn-mode-connect');
        const selectBtn = document.getElementById('btn-mode-select');
        if (connectBtn) connectBtn.classList.remove('active');
        if (selectBtn) selectBtn.classList.add('active');

        this.updateModeIndicator();
    }

    updateModeIndicator() {
        const badge = document.getElementById('status-mode-badge');
        const desc = document.getElementById('status-mode-desc');
        if (!badge) return;

        if (this.mode === 'connect') {
            badge.className = 'badge bg-warning text-dark fw-bold';
            badge.innerHTML = '<i class="fa-solid fa-plug me-1"></i>Connect Mode';
            if (desc) desc.textContent = this.connectSource 
                ? `Source: ${this.connectSource.name}. Now click destination device.` 
                : 'Click first device, then second device to attach cable (ESC to cancel)';
        } else {
            badge.className = 'badge bg-primary text-dark fw-bold';
            badge.innerHTML = '<i class="fa-solid fa-arrow-pointer me-1"></i>Selection Mode';
            if (desc) desc.textContent = this.selectedDevice 
                ? `Selected: ${this.selectedDevice.name} [${this.selectedDevice.ip || 'No IP'}]`
                : 'Click device to inspect · Drag to position';
        }
    }

    updateTempCable(x1, y1, x2, y2) {
        if (!this.svg) return;
        const g = this.svg.querySelector('g.connections-layer');
        if (!g) return;
        let line = g.querySelector('.temp-cable-line');
        if (!line) {
            line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('class', 'temp-cable-line');
            g.appendChild(line);
        }
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
    }

    removeTempCable() {
        if (!this.svg) return;
        const line = this.svg.querySelector('.temp-cable-line');
        if (line) line.remove();
    }

    handleConnectClick(device) {
        if (!this.connectSource) {
            // Picked first device (Source)
            this.connectSource = device;
            const el = document.getElementById(device.id);
            if (el) el.classList.add('connecting-source');
            window.ramonetUI?.showToast('Select Destination', `Connecting from ${device.name}. Now click or drag to target device.`, 'info');
        } else {
            // Picked second device (Target)
            if (String(this.connectSource.id) === String(device.id)) {
                return; // Double click or re-click on same device safely ignored
            }

            const src = this.connectSource;
            const dest = device;

            const srcEl = document.getElementById(src.id);
            if (srcEl) srcEl.classList.remove('connecting-source');
            this.removeTempCable();
            this.cancelConnectMode();

            // Open Port Connection Modal
            window.ramonetUI?.openConnectModal(src, dest, (cableType, srcPort, destPort) => {
                this.createConnection(src.id, srcPort, dest.id, destPort, cableType);
            });
        }
    }

    createConnection(srcDevId, srcPort, destDevId, destPort, cableType = 'copper_straight') {
        const sId = String(srcDevId);
        const dId = String(destDevId);
        const sPort = String(srcPort || 'eth0');
        const dPort = String(destPort || 'eth0');

        // Prevent duplicate connection on same ports
        const exists = this.project.connections.some(c => 
            (String(c.source_device) === sId && String(c.source_port) === sPort) ||
            (String(c.target_device) === sId && String(c.target_port) === sPort) ||
            (String(c.source_device) === dId && String(c.source_port) === dPort) ||
            (String(c.target_device) === dId && String(c.target_port) === dPort)
        );

        if (exists) {
            window.ramonetUI?.showToast('Port in Use', `Interface is already connected to another cable.`, 'danger');
            return;
        }

        const connId = 'conn_' + Date.now() + '_' + Math.floor(Math.random() * 100);
        const connection = {
            id: connId,
            source_device: sId,
            source_port: sPort,
            target_device: dId,
            target_port: dPort,
            from: sId,
            to: dId,
            from_port: sPort,
            to_port: dPort,
            type: cableType,
            status: 'connected',
            speed: 1000
        };

        // Mark interfaces as active/up on devices
        const srcDev = this.project.devices.find(d => String(d.id) === sId);
        const destDev = this.project.devices.find(d => String(d.id) === dId);
        if (srcDev?.interfaces) {
            const ifc = srcDev.interfaces.find(i => typeof i === 'object' && i.name === sPort);
            if (ifc) ifc.status = 'up';
        }
        if (destDev?.interfaces) {
            const ifc = destDev.interfaces.find(i => typeof i === 'object' && i.name === dPort);
            if (ifc) ifc.status = 'up';
        }

        this.project.connections.push(connection);
        this.renderConnections();
        this.renderMinimap();
        this.triggerChange('Created Cable Connection');
        window.ramonetUI?.showToast('Connected', `Connected ${sPort} ↔ ${dPort} via ${cableType.replace('_', ' ')}`, 'success');
    }

    deleteConnection(connId) {
        const index = this.project.connections.findIndex(c => String(c.id) === String(connId));
        if (index === -1) return;
        this.project.connections.splice(index, 1);
        this.selectedConnection = null;
        this.renderConnections();
        this.renderMinimap();
        this.triggerChange('Removed Cable Connection');
    }

    renderConnections() {
        if (!this.svg) return;
        const g = this.svg.querySelector('g.connections-layer');
        if (!g) return;

        // Preserve temporary cable line if active
        const tempLine = g.querySelector('.temp-cable-line');
        g.innerHTML = '';
        if (tempLine) g.appendChild(tempLine);

        this.project.connections.forEach(conn => {
            const srcId = String(conn.source_device || conn.from || conn.source || '');
            const destId = String(conn.target_device || conn.to || conn.target || '');
            const src = this.project.devices.find(d => String(d.id) === srcId || String(d.name).toLowerCase() === srcId.toLowerCase());
            const dest = this.project.devices.find(d => String(d.id) === destId || String(d.name).toLowerCase() === destId.toLowerCase());
            if (!src || !dest) return;

            // Compute center points of node boxes
            const x1 = src.x + 50;
            const y1 = src.y + 42;
            const x2 = dest.x + 50;
            const y2 = dest.y + 42;

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            path.setAttribute('x1', x1);
            path.setAttribute('y1', y1);
            path.setAttribute('x2', x2);
            path.setAttribute('y2', y2);
            const cableType = conn.type ? conn.type.replace(/_/g, '-') : 'copper-straight';
            const isSelected = this.selectedConnection && String(this.selectedConnection.id) === String(conn.id);
            path.setAttribute('class', `cable-line ${cableType}${isSelected ? ' selected' : ''}`);
            path.id = conn.id;

            path.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectedConnection = conn;
                this.renderConnections();
                window.ramonetUI?.showConnectionInspector?.(conn);
            });

            g.appendChild(path);

            // Port Label Badges on Cable
            const midX = (x1 + x2) / 2;
            const midY = (y1 + y2) / 2;
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', midX);
            label.setAttribute('y', midY - 6);
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('fill', '#94A3B8');
            label.setAttribute('font-size', '10px');
            label.setAttribute('font-family', 'monospace');
            const sPort = conn.source_port || conn.from_port || conn.src_port || 'port';
            const dPort = conn.target_port || conn.to_port || conn.dest_port || 'port';
            label.textContent = `${sPort} ↔ ${dPort}`;
            g.appendChild(label);
        });
    }

    // ================= MINIMAP =================

    renderMinimap() {
        if (!this.minimap) return;
        const ctx = this.minimap.getContext('2d');
        const w = this.minimap.width;
        const h = this.minimap.height;

        ctx.clearRect(0, 0, w, h);
        ctx.fillStyle = '#111827';
        ctx.fillRect(0, 0, w, h);

        if (this.project.devices.length === 0) return;

        // Scale bounds
        const scaleX = w / 2500;
        const scaleY = h / 1800;

        // Draw connections
        ctx.strokeStyle = '#38BDF8';
        ctx.lineWidth = 1;
        this.project.connections.forEach(conn => {
            const src = this.project.devices.find(d => d.id === conn.source_device);
            const dest = this.project.devices.find(d => d.id === conn.target_device);
            if (!src || !dest) return;
            ctx.beginPath();
            ctx.moveTo((src.x + 50) * scaleX, (src.y + 42) * scaleY);
            ctx.lineTo((dest.x + 50) * scaleX, (dest.y + 42) * scaleY);
            ctx.stroke();
        });

        // Draw device dots
        this.project.devices.forEach(dev => {
            ctx.fillStyle = dev.category.includes('router') ? '#A855F7' : (dev.category.includes('switch') ? '#38BDF8' : '#22C55E');
            ctx.fillRect(dev.x * scaleX, dev.y * scaleY, 6, 6);
        });
    }

    // ================= HISTORY (UNDO / REDO) =================

    triggerChange(actionName = 'Edit') {
        this.pushHistoryState(actionName);
        this.debouncedSave(this.project);
    }

    pushHistoryState(actionName) {
        // Truncate any redo branches
        if (this.historyIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.historyIndex + 1);
        }

        const snapshot = JSON.stringify(this.project);
        this.history.push({ action: actionName, data: snapshot });
        if (this.history.length > this.maxHistory) {
            this.history.shift();
        } else {
            this.historyIndex++;
        }
    }

    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            const snap = this.history[this.historyIndex];
            this.loadProjectData(JSON.parse(snap.data));
            window.ramonetUI?.showToast('Undo', snap.action, 'info');
        }
    }

    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            const snap = this.history[this.historyIndex];
            this.loadProjectData(JSON.parse(snap.data));
            window.ramonetUI?.showToast('Redo', snap.action, 'info');
        }
    }

    loadProjectData(projectData) {
        this.project = projectData;
        if (this.nodesContainer) this.nodesContainer.innerHTML = '';
        this.project.devices.forEach(d => this.renderDeviceNode(d));
        this.renderConnections();
        this.renderMinimap();
        this.deselectAll(false);
        window.ramonetTerminal?.syncDeviceSelector();
    }

    // ================= CONTEXT MENU =================

    showContextMenu(clientX, clientY, device) {
        const menu = document.getElementById('topology-context-menu');
        if (!menu) return;

        menu.style.display = 'block';
        menu.style.left = `${clientX}px`;
        menu.style.top = `${clientY}px`;

        const titleEl = menu.querySelector('.context-menu-device-title');
        if (titleEl) titleEl.textContent = device.name;

        // Click outside closes menu
        const closeHandler = () => {
            menu.style.display = 'none';
            window.removeEventListener('click', closeHandler);
        };
        setTimeout(() => window.addEventListener('click', closeHandler), 10);
    }

    hideContextMenu() {
        const menu = document.getElementById('topology-context-menu');
        if (menu) menu.style.display = 'none';
    }
}

window.TopologyCanvas = TopologyCanvas;
