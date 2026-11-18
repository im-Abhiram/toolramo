/**
 * rack-designer.js
 * Ramonet Physical Network Rack Designer Controller
 * Interactive 19-inch equipment mounting, multi-U height handling,
 * power & heat calculation, overlap detection, and logical device mapping.
 */

(function () {
    'use strict';

    // State
    let activeRackId = 'rack_a';
    let currentView = 'front';
    let selectedUnit = null;

    let rackData = {
        rack_a: {
            id: 'rack_a',
            name: 'Rack A — Server Room Main',
            height: 42,
            equipment: [
                { id: 'eq_1', name: 'Cisco Catalyst 2960-X 24P', type: 'layer2_switch', start_u: 40, height_u: 1, watts: 35.0, logical_device: 'SW-Access-01' },
                { id: 'eq_2', name: 'Cat6 24-Port Patch Panel', type: 'patch_panel', start_u: 39, height_u: 1, watts: 0.0, logical_device: 'PP-01' },
                { id: 'eq_3', name: 'FortiGate 100F Firewall', type: 'firewall', start_u: 37, height_u: 1, watts: 75.0, logical_device: 'FW-Perimeter' },
                { id: 'eq_4', name: 'Cisco ISR 4331 Router', type: 'router', start_u: 35, height_u: 1, watts: 60.0, logical_device: 'RTR-Campus-Core' },
                { id: 'eq_5', name: 'Dell PowerEdge R740 Server', type: 'windows_server', start_u: 20, height_u: 2, watts: 250.0, logical_device: 'SRV-HQ-Data' },
                { id: 'eq_6', name: 'APC Smart-UPS 3000VA', type: 'ups_power', start_u: 1, height_u: 2, watts: 0.0, logical_device: 'UPS-01' }
            ]
        },
        rack_b: {
            id: 'rack_b',
            name: 'Rack B — Network Distribution',
            height: 24,
            equipment: [
                { id: 'eq_b1', name: 'PoE+ Surveillance Switch', type: 'poe_switch', start_u: 23, height_u: 1, watts: 65.0, logical_device: 'SW-PoE-01' },
                { id: 'eq_b2', name: '16-Channel Surveillance NVR', type: 'nvr_recorder', start_u: 21, height_u: 2, watts: 90.0, logical_device: 'NVR-Central-01' }
            ]
        }
    };

    document.addEventListener('DOMContentLoaded', function () {
        loadRackState();
        renderRackElevation();
        updatePowerMetrics();
    });

    function loadRackState() {
        const saved = localStorage.getItem('ramonet_rack_designer_state');
        if (saved) {
            try {
                rackData = JSON.parse(saved);
            } catch (e) {
                console.warn('Could not parse saved rack data:', e);
            }
        }
    }

    function saveRackState() {
        localStorage.setItem('ramonet_rack_designer_state', JSON.stringify(rackData));
    }

    // -------------------------------------------------------------
    // RENDER ELEVATION
    // -------------------------------------------------------------
    function renderRackElevation() {
        const rack = rackData[activeRackId] || rackData['rack_a'];
        const container = document.getElementById('rack-frame-container');
        const badge = document.getElementById('rack-status-badge');
        if (!container) return;

        if (badge) {
            badge.textContent = `${rack.name} (${rack.height}U) — ${currentView.toUpperCase()} Elevation`;
        }

        container.innerHTML = '';

        // Check overlaps
        const occupiedMap = {};
        const overlaps = [];
        rack.equipment.forEach(eq => {
            for (let u = eq.start_u; u < eq.start_u + eq.height_u; u++) {
                if (occupiedMap[u]) {
                    overlaps.push({ unit: u, dev1: occupiedMap[u].name, dev2: eq.name });
                } else {
                    occupiedMap[u] = eq;
                }
            }
        });

        // Show/hide overlap warning
        const alertBox = document.getElementById('rack-overlap-alert');
        const alertText = document.getElementById('rack-overlap-text');
        if (alertBox && alertText) {
            if (overlaps.length > 0) {
                alertText.textContent = `Collision detected at unit U${overlaps[0].unit} between ${overlaps[0].dev1} and ${overlaps[0].dev2}.`;
                alertBox.classList.remove('d-none');
            } else {
                alertBox.classList.add('d-none');
            }
        }

        // Render slots from height down to 1
        const renderedEquipIds = new Set();

        for (let u = rack.height; u >= 1; u--) {
            const slot = document.createElement('div');
            slot.className = 'rack-unit-slot';
            slot.id = `rack-slot-${u}`;

            const num = document.createElement('div');
            num.className = 'rack-unit-number';
            num.textContent = `U${u}`;
            slot.appendChild(num);

            const content = document.createElement('div');
            content.className = 'rack-slot-content';

            const equip = occupiedMap[u];
            if (equip && !renderedEquipIds.has(equip.id)) {
                // Topmost slot for multi-U device
                renderedEquipIds.add(equip.id);
                const devCard = document.createElement('div');
                const isOverlap = overlaps.some(o => o.unit >= equip.start_u && o.unit < equip.start_u + equip.height_u);
                devCard.className = `rack-mounted-device ${isOverlap ? 'overlap-error' : ''} ${selectedUnit === equip.id ? 'selected' : ''}`;
                devCard.style.height = `${equip.height_u * 28 - 2}px`;
                devCard.style.marginTop = `${(equip.height_u - 1) * 28}px`; // span downwards visually
                devCard.onclick = function (e) {
                    e.stopPropagation();
                    selectRackEquipment(equip);
                };

                let icon = 'fa-server';
                if (equip.type.includes('switch')) icon = 'fa-network-wired';
                else if (equip.type.includes('router')) icon = 'fa-route';
                else if (equip.type.includes('firewall')) icon = 'fa-shield-halved';
                else if (equip.type.includes('patch')) icon = 'fa-bars-staggered';
                else if (equip.type.includes('ups')) icon = 'fa-car-battery';
                else if (equip.type.includes('nvr')) icon = 'fa-video';

                devCard.innerHTML = `
                    <div class="d-flex align-items-center gap-2 overflow-hidden">
                        <i class="fa-solid ${icon} text-info"></i>
                        <span class="small fw-semibold text-truncate" style="max-width: 220px;">${equip.name}</span>
                        ${equip.logical_device ? `<span class="badge bg-dark text-info border border-secondary" style="font-size: 0.65rem;">${equip.logical_device}</span>` : ''}
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <span class="small text-muted font-monospace" style="font-size: 0.7rem;">${equip.watts}W</span>
                        <span class="badge bg-secondary" style="font-size: 0.65rem;">${equip.height_u}U</span>
                        <button type="button" class="btn btn-xs text-danger p-0" title="Unmount" onclick="unmountEquipment('${equip.id}', event)">
                            <i class="fa-solid fa-xmark"></i>
                        </button>
                    </div>
                `;
                content.appendChild(devCard);
            } else if (!equip) {
                // Empty slot
                content.innerHTML = `<span class="small text-muted opacity-25" style="font-size: 0.65rem;">Empty ${u}U</span>`;
            }

            slot.appendChild(content);
            container.appendChild(slot);
        }
    }

    // -------------------------------------------------------------
    // MOUNT / UNMOUNT
    // -------------------------------------------------------------
    window.mountEquipmentToRack = function (name, type, height_u, watts) {
        const rack = rackData[activeRackId];
        if (!rack) return;

        // Find available starting U (top-down or bottom-up)
        const occupied = new Set();
        rack.equipment.forEach(e => {
            for (let u = e.start_u; u < e.start_u + e.height_u; u++) {
                occupied.add(u);
            }
        });

        // Find lowest available block of height_u
        let start_u = null;
        for (let u = 1; u <= rack.height - height_u + 1; u++) {
            let fits = true;
            for (let k = 0; k < height_u; k++) {
                if (occupied.has(u + k)) {
                    fits = false;
                    break;
                }
            }
            if (fits) {
                start_u = u;
                break;
            }
        }

        if (!start_u) {
            alert(`No contiguous ${height_u}U space available in ${rack.name}!`);
            return;
        }

        const newEq = {
            id: `eq_${Date.now()}`,
            name: name,
            type: type,
            start_u: start_u,
            height_u: height_u,
            watts: watts,
            logical_device: null
        };

        rack.equipment.push(newEq);
        saveRackState();
        renderRackElevation();
        updatePowerMetrics();
        selectRackEquipment(newEq);
    };

    window.unmountEquipment = function (eqId, event) {
        if (event) event.stopPropagation();
        const rack = rackData[activeRackId];
        if (!rack) return;
        rack.equipment = rack.equipment.filter(e => e.id !== eqId);
        saveRackState();
        renderRackElevation();
        updatePowerMetrics();

        const inspBody = document.getElementById('rack-inspector-body');
        if (inspBody) {
            inspBody.innerHTML = '<div class="small text-muted text-center py-3">Equipment unmounted. Select another unit.</div>';
        }
    };

    window.clearActiveRack = function () {
        if (!confirm('Unmount all equipment from this rack?')) return;
        const rack = rackData[activeRackId];
        if (rack) {
            rack.equipment = [];
            saveRackState();
            renderRackElevation();
            updatePowerMetrics();
        }
    };

    // -------------------------------------------------------------
    // SELECT & INSPECT
    // -------------------------------------------------------------
    function selectRackEquipment(equip) {
        selectedUnit = equip.id;
        renderRackElevation();

        const badge = document.getElementById('selected-u-badge');
        if (badge) badge.textContent = `Unit ${equip.start_u}U (${equip.height_u}U)`;

        const inspBody = document.getElementById('rack-inspector-body');
        if (inspBody) {
            inspBody.innerHTML = `
                <div class="mb-3">
                    <label class="small text-muted mb-1">Equipment Name:</label>
                    <input type="text" class="form-control form-control-sm bg-dark text-light border-secondary" id="eq-name-input" value="${equip.name}" onchange="updateSelectedEquipName(this.value)">
                </div>
                <div class="row g-2 mb-3">
                    <div class="col-6">
                        <label class="small text-muted mb-1">Rack Position (Start U):</label>
                        <input type="number" class="form-control form-control-sm bg-dark text-light border-secondary" min="1" max="48" value="${equip.start_u}" onchange="updateSelectedEquipU(this.value)">
                    </div>
                    <div class="col-6">
                        <label class="small text-muted mb-1">Power Draw:</label>
                        <input type="number" class="form-control form-control-sm bg-dark text-light border-secondary" value="${equip.watts}" onchange="updateSelectedEquipWatts(this.value)">
                    </div>
                </div>
                <div class="mb-3">
                    <label class="small text-muted mb-1">Mapped Logical Device:</label>
                    <input type="text" class="form-control form-control-sm bg-dark text-light border-secondary" placeholder="e.g. SW-Core-01" value="${equip.logical_device || ''}" onchange="updateSelectedLogicalDev(this.value)">
                    <div class="form-text text-muted" style="font-size: 0.68rem;">Ties physical rack unit to Network Designer & IPAM logic.</div>
                </div>
            `;
        }

        // Render patching table
        const patchCont = document.getElementById('rack-patching-container');
        if (patchCont) {
            patchCont.innerHTML = `
                <div class="table-responsive small font-monospace">
                    <table class="table table-dark table-sm table-bordered mb-0">
                        <thead>
                            <tr>
                                <th>Port</th>
                                <th>Destination</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>Port 1</td><td>Patch Panel 1 - Jack 1</td><td class="text-success">Connected</td></tr>
                            <tr><td>Port 2</td><td>Patch Panel 1 - Jack 2</td><td class="text-success">Connected</td></tr>
                            <tr><td>Port 24</td><td>Uplink to Core Router</td><td class="text-info">Trunk</td></tr>
                        </tbody>
                    </table>
                </div>
            `;
        }
    }

    window.updateSelectedEquipName = function (val) {
        const equip = findSelectedEquip();
        if (equip) { equip.name = val; saveRackState(); renderRackElevation(); }
    };

    window.updateSelectedEquipU = function (val) {
        const equip = findSelectedEquip();
        if (equip) { equip.start_u = parseInt(val, 10); saveRackState(); renderRackElevation(); updatePowerMetrics(); }
    };

    window.updateSelectedEquipWatts = function (val) {
        const equip = findSelectedEquip();
        if (equip) { equip.watts = parseFloat(val); saveRackState(); updatePowerMetrics(); }
    };

    window.updateSelectedLogicalDev = function (val) {
        const equip = findSelectedEquip();
        if (equip) { equip.logical_device = val.trim(); saveRackState(); renderRackElevation(); }
    };

    function findSelectedEquip() {
        const rack = rackData[activeRackId];
        if (!rack) return null;
        return rack.equipment.find(e => e.id === selectedUnit);
    }

    // -------------------------------------------------------------
    // POWER & HEAT METRICS
    // -------------------------------------------------------------
    function updatePowerMetrics() {
        const rack = rackData[activeRackId];
        if (!rack) return;

        let totalU = 0;
        let totalWatts = 0.0;
        rack.equipment.forEach(e => {
            totalU += e.height_u;
            totalWatts += e.watts;
        });

        const pct = Math.min(100, Math.round((totalU / rack.height) * 100));
        const occText = document.getElementById('rack-occupied-text');
        const occBar = document.getElementById('rack-occupied-bar');
        const pwrText = document.getElementById('rack-power-text');
        const btuText = document.getElementById('rack-btu-text');

        if (occText) occText.textContent = `${totalU} / ${rack.height} U (${pct}%)`;
        if (occBar) occBar.style.width = `${pct}%`;
        if (pwrText) pwrText.textContent = `${totalWatts.toFixed(0)} Watts`;
        if (btuText) btuText.textContent = `${(totalWatts * 3.412142).toFixed(0)} BTU/hr`;
    }

    // -------------------------------------------------------------
    // RACK CONTROLS
    // -------------------------------------------------------------
    window.switchActiveRack = function () {
        const sel = document.getElementById('active-rack-select');
        if (sel) {
            activeRackId = sel.value;
            const hSel = document.getElementById('rack-height-select');
            if (hSel && rackData[activeRackId]) {
                hSel.value = rackData[activeRackId].height.toString();
            }
            renderRackElevation();
            updatePowerMetrics();
        }
    };

    window.updateRackHeight = function () {
        const sel = document.getElementById('rack-height-select');
        if (sel && rackData[activeRackId]) {
            rackData[activeRackId].height = parseInt(sel.value, 10);
            saveRackState();
            renderRackElevation();
            updatePowerMetrics();
        }
    };

    window.setRackView = function (view) {
        currentView = view;
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.classList.remove('active', 'btn-outline-info');
            btn.classList.add('btn-outline-secondary', 'text-secondary');
            if (btn.dataset.view === view) {
                btn.classList.add('active', 'btn-outline-info');
                btn.classList.remove('btn-outline-secondary', 'text-secondary');
            }
        });
        renderRackElevation();
    };

    window.promptCreateNewRack = function () {
        const name = prompt('Enter a name for the new physical rack:', 'Rack C — Edge Enclosure');
        if (!name) return;
        const newId = `rack_${Date.now()}`;
        rackData[newId] = {
            id: newId,
            name: name,
            height: 42,
            equipment: []
        };
        activeRackId = newId;

        const sel = document.getElementById('active-rack-select');
        if (sel) {
            const opt = document.createElement('option');
            opt.value = newId;
            opt.textContent = `${name} (42U)`;
            sel.appendChild(opt);
            sel.value = newId;
        }

        saveRackState();
        renderRackElevation();
        updatePowerMetrics();
    };

})();
