/**
 * Ramonet Packet Flow Visualizer
 * Animates packets moving along physical/logical topology cables,
 * rendering step-by-step hop diagnostics in the workbench drawer.
 */

class PacketVisualizer {
    constructor(canvasInstance) {
        this.canvas = canvasInstance;
        this.currentTrace = null;
        this.currentHopIndex = 0;
        this.isPlaying = false;
        this.animationSpeedMs = 1200;
        this.animationTimer = null;
    }

    async tracePacket(srcDevId, destIp, protocol = 'ICMP', destPort = 80) {
        this.reset();
        const payload = {
            src_dev_id: srcDevId,
            dest_ip: destIp,
            protocol: protocol,
            dest_port: parseInt(destPort) || 80,
            topology: this.canvas.project
        };

        window.ramonetUI?.showWorkbenchTab('packet-inspector');
        const inspectorEl = document.getElementById('packet-inspector-content');
        if (inspectorEl) {
            inspectorEl.innerHTML = `
                <div class="p-3 text-center text-muted">
                    <i class="fa-solid fa-spinner fa-spin fa-2x text-info mb-2"></i>
                    <p>Simulating packet traversal across network topology...</p>
                </div>
            `;
        }

        try {
            // Call Django REST Framework simulation endpoint
            const response = await fetch('/api/simulation/trace/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Simulation API returned status ${response.status}`);
            }

            const data = await response.json();
            this.currentTrace = data;
            this.renderTraceReport(data);
            this.playAnimation();
        } catch (err) {
            console.warn('Backend trace endpoint failed or offline, running client fallback:', err);
            // Fallback: Use client-side simulation logic
            this.runClientFallbackTrace(srcDevId, destIp, protocol, destPort);
        }
    }

    runClientFallbackTrace(srcDevId, destIp, protocol, destPort) {
        const src = this.canvas.project.devices.find(d => d.id === srcDevId);
        const dest = this.canvas.project.devices.find(d => d.ip === destIp);

        const hops = [];
        hops.push({
            step: 1,
            device_name: src?.name || 'Source',
            action: 'ORIGINATE_PACKET',
            details: `Originated ${protocol} packet from ${src?.ip || '0.0.0.0'} to ${destIp}:${destPort}`
        });

        if (dest) {
            hops.push({
                step: 2,
                device_name: dest.name,
                action: 'PACKET_RECEIVED_BY_DESTINATION',
                details: `Packet successfully arrived at ${dest.name} (${destIp})`
            });
            this.currentTrace = { success: true, hops: hops, summary: 'Delivered successfully (Client Mode)' };
        } else {
            hops.push({
                step: 2,
                device_name: src?.name || 'Source',
                action: 'DROP',
                details: `Destination IP ${destIp} is unreachable on local subnet.`
            });
            this.currentTrace = { success: false, drop_reason: 'NO_ROUTE_TO_HOST', hops: hops };
        }

        this.renderTraceReport(this.currentTrace);
        this.playAnimation();
    }

    renderTraceReport(traceData) {
        const inspectorEl = document.getElementById('packet-inspector-content');
        if (!inspectorEl) return;

        const isSuccess = traceData.success;
        const bannerClass = isSuccess ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger';
        const bannerIcon = isSuccess ? 'fa-circle-check' : 'fa-circle-xmark';
        const summaryText = isSuccess ? (traceData.summary || 'Packet Delivered Successfully') : `Dropped: ${traceData.drop_reason || 'Host Unreachable'}`;

        let hopsHtml = '';
        (traceData.hops || []).forEach((h, idx) => {
            const isDrop = h.action === 'DROP' || (!isSuccess && idx === traceData.hops.length - 1);
            const badgeClass = isDrop ? 'bg-danger' : 'bg-info text-dark';
            hopsHtml += `
                <div class="hop-timeline-item p-2 mb-2 rounded border border-secondary border-opacity-25 bg-card">
                    <div class="d-flex align-items-center justify-content-between mb-1">
                        <span class="badge ${badgeClass}">Hop #${h.step}</span>
                        <strong class="text-white">${h.device_name || 'Device'}</strong>
                        <span class="text-muted small">${h.action || ''}</span>
                    </div>
                    <div class="small text-secondary font-monospace">${h.details || ''}</div>
                </div>
            `;
        });

        inspectorEl.innerHTML = `
            <div class="p-3">
                <div class="d-flex align-items-center justify-content-between mb-3 p-2 rounded ${bannerClass}">
                    <div><i class="fa-solid ${bannerIcon} me-2"></i><strong>${summaryText}</strong></div>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-light btn-sm" id="btn-anim-pause"><i class="fa-solid fa-pause"></i></button>
                        <button class="btn btn-outline-light btn-sm" id="btn-anim-step"><i class="fa-solid fa-forward-step"></i></button>
                        <button class="btn btn-outline-light btn-sm" id="btn-anim-reset"><i class="fa-solid fa-rotate-left"></i></button>
                    </div>
                </div>
                <div class="hops-timeline">${hopsHtml}</div>
            </div>
        `;

        document.getElementById('btn-anim-pause')?.addEventListener('click', () => this.togglePause());
        document.getElementById('btn-anim-step')?.addEventListener('click', () => this.stepForward());
        document.getElementById('btn-anim-reset')?.addEventListener('click', () => this.reset());
    }

    playAnimation() {
        this.isPlaying = true;
        this.currentHopIndex = 0;
        this.stepForward();
    }

    stepForward() {
        if (!this.currentTrace || !this.currentTrace.hops) return;
        if (this.currentHopIndex >= this.currentTrace.hops.length) {
            this.isPlaying = false;
            return;
        }

        const hop = this.currentTrace.hops[this.currentHopIndex];
        this.highlightHopDevice(hop.device_id || hop.device_name);
        this.currentHopIndex++;

        if (this.isPlaying && this.currentHopIndex < this.currentTrace.hops.length) {
            this.animationTimer = setTimeout(() => this.stepForward(), this.animationSpeedMs);
        }
    }

    togglePause() {
        this.isPlaying = !this.isPlaying;
        if (this.isPlaying) {
            this.stepForward();
        } else {
            clearTimeout(this.animationTimer);
        }
    }

    highlightHopDevice(devIdOrName) {
        document.querySelectorAll('.device-node.sim-active').forEach(el => el.classList.remove('sim-active'));
        if (!devIdOrName) return;

        const dev = this.canvas.project.devices.find(d => d.id === devIdOrName || d.name === devIdOrName);
        if (dev) {
            const el = document.getElementById(dev.id);
            if (el) {
                el.classList.add('sim-active');
                el.style.borderColor = '#FACC15';
                el.style.boxShadow = '0 0 20px #FACC15';
                setTimeout(() => {
                    el.style.borderColor = '';
                    el.style.boxShadow = '';
                }, 1000);
            }
        }
    }

    reset() {
        this.isPlaying = false;
        clearTimeout(this.animationTimer);
        this.currentHopIndex = 0;
        document.querySelectorAll('.device-node.sim-active').forEach(el => el.classList.remove('sim-active'));
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

window.PacketVisualizer = PacketVisualizer;
