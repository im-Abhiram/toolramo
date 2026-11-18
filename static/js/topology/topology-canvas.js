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
    }

    initEventListeners() {
        // Panning with Mouse Drag
        this.container.addEventListener('mousedown', (e) => {
            if (e.target === this.container || e.target === this.svg) {
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
            }
        });

        window.addEventListener('mouseup', () => {
            if (this.isPanningCanvas) {
                this.isPanningCanvas = false;
                this.container.classList.remove('panning');
            }
            if (this.isDraggingNode) {
                this.isDraggingNode = false;
                this.dragTargetNode = null;
                this.triggerChange('Device Moved');
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

            if (e.key === 'Delete' || e.key === 'Backspace') {
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
            maxX = Math.max(maxX, d.x + 100);
            maxY = Math.max(maxY, d.y + 90);
        });

        const width = maxX - minX + 150;
        const height = maxY - minY + 150;
        const contW = this.container.clientWidth;
        const contH = this.container.clientHeight;

        this.scale = Math.min(Math.max(Math.min(contW / width, contH / height), 0.5), 1.4);
        this.panX = (contW - width * this.scale) / 2 - minX * this.scale;
        this.panY = (contH - height * this.scale) / 2 - minY * this.scale;

        this.applyTransform();
        this.renderMinimap();
    }

    // ================= DEVICE MANAGEMENT =================

    addDevice(definition, x = 100, y = 100) {
        const category = (definition.category || definition.device_type || 'computer').toLowerCase();
        const baseName = definition.name || 'Device';
        
        // Count existing devices of this category for auto-naming
        const count = this.project.devices.filter(d => (d.category || '').toLowerCase().includes(category)).length + 1;
        
        let prefix = 'PC';
        if (category.includes('switch')) prefix = 'Switch';
        else if (category.includes('router')) prefix = 'Router';
        else if (category.includes('firewall')) prefix = 'Firewall';
        else if (category.includes('cctv') || category.includes('camera')) prefix = 'Camera';
        else if (category.includes('nvr')) prefix = 'NVR';
        else if (category.includes('storage') || category.includes('nas')) prefix = 'NAS';
        else if (category.includes('printer')) prefix = 'Printer';
        else if (category.includes('server')) prefix = 'Server';
        else if (category.includes('wireless')) prefix = 'AP';

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
            category: category,
            model_name: definition.model_name || definition.name,
            icon: definition.icon || 'fa-server',
            cli_platform: definition.cli_platform || 'cisco_ios',
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
                <div class="port-connector-anchor top" data-anchor="top"></div>
                <div class="port-connector-anchor bottom" data-anchor="bottom"></div>
                <div class="port-connector-anchor left" data-anchor="left"></div>
                <div class="port-connector-anchor right" data-anchor="right"></div>
                <div class="device-node-icon">
                    <i class="fa-solid ${device.icon}"></i>
                </div>
                <div class="device-node-name" title="${device.name}">${device.name}</div>
                <div class="device-node-ip" title="${device.ip || 'No IP'}">${device.ip || '---'}</div>
            `;
            this.nodesContainer.appendChild(el);

            // Node Drag Events
            el.addEventListener('mousedown', (e) => {
                if (e.button !== 0) return; // Only left click
                e.stopPropagation();

                if (this.mode === 'connect') {
                    this.handleConnectClick(device);
                    return;
                }

                this.selectDevice(device.id);
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

    selectDevice(deviceId) {
        this.deselectAll();
        this.selectedDevice = this.project.devices.find(d => d.id === deviceId);
        if (this.selectedDevice) {
            const el = document.getElementById(deviceId);
            if (el) el.classList.add('selected');
            window.ramonetUI?.updateSelectedDevice(this.selectedDevice);
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
        this.project.connections = this.project.connections.filter(c => 
            c.source_device !== deviceId && c.target_device !== deviceId
        );

        this.project.devices.splice(index, 1);
        this.selectedDevice = null;
        this.renderConnections();
        this.renderMinimap();
        window.ramonetUI?.updateSelectedDevice(null);
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

    deselectAll() {
        document.querySelectorAll('.device-node.selected').forEach(el => el.classList.remove('selected'));
        this.selectedDevice = null;
        this.selectedConnection = null;
        this.hideContextMenu();
        window.ramonetUI?.updateSelectedDevice(null);
    }

    // ================= CONNECTIONS & CABLING =================

    startConnectMode() {
        this.mode = 'connect';
        this.connectSource = null;
        this.container.classList.add('connecting-mode');
        window.ramonetUI?.showToast('Connection Mode', 'Click the first device, then click the second device to connect.', 'info');
    }

    cancelConnectMode() {
        this.mode = 'select';
        this.connectSource = null;
        this.container.classList.remove('connecting-mode');
    }

    handleConnectClick(device) {
        if (!this.connectSource) {
            // Picked first device
            this.connectSource = device;
            window.ramonetUI?.showToast('Select Destination', `Selected ${device.name}. Now click the target device.`, 'info');
        } else {
            // Picked second device
            if (this.connectSource.id === device.id) {
                window.ramonetUI?.showToast('Invalid Connection', 'Cannot connect a device to itself.', 'warning');
                return;
            }

            const src = this.connectSource;
            const dest = device;
            this.cancelConnectMode();

            // Open Port Connection Modal
            window.ramonetUI?.openConnectModal(src, dest, (cableType, srcPort, destPort) => {
                this.createConnection(src.id, srcPort, dest.id, destPort, cableType);
            });
        }
    }

    createConnection(srcDevId, srcPort, destDevId, destPort, cableType = 'copper_straight') {
        // Prevent duplicate connection on same ports
        const exists = this.project.connections.some(c => 
            (c.source_device === srcDevId && c.source_port === srcPort) ||
            (c.target_device === srcDevId && c.target_port === srcPort) ||
            (c.source_device === destDevId && c.source_port === destPort) ||
            (c.target_device === destDevId && c.target_port === destPort)
        );

        if (exists) {
            window.ramonetUI?.showToast('Port in use', 'One of the selected interfaces already has a cable connected.', 'danger');
            return;
        }

        const connId = 'conn_' + Date.now() + '_' + Math.floor(Math.random() * 100);
        const connection = {
            id: connId,
            source_device: srcDevId,
            source_port: srcPort,
            target_device: destDevId,
            target_port: destPort,
            type: cableType,
            status: 'connected',
            speed: 1000
        };

        this.project.connections.push(connection);
        this.renderConnections();
        this.renderMinimap();
        this.triggerChange('Created Cable Connection');
        window.ramonetUI?.showToast('Connected', `Connected via ${cableType.replace('_', ' ')}`, 'success');
    }

    deleteConnection(connId) {
        const index = this.project.connections.findIndex(c => c.id === connId);
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

        g.innerHTML = '';

        this.project.connections.forEach(conn => {
            const src = this.project.devices.find(d => d.id === conn.source_device);
            const dest = this.project.devices.find(d => d.id === conn.target_device);
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
            path.setAttribute('class', `cable-line ${conn.type.replace('_', '-')}`);
            path.id = conn.id;

            path.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectedConnection = conn;
                window.ramonetUI?.showConnectionInspector(conn);
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
            label.textContent = `${conn.source_port} ↔ ${conn.target_port}`;
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
        this.deselectAll();
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
