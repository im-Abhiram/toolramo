/**
 * Ramonet Advanced Network Configuration Assistant
 * Dedicated assistant providing 15-section device guides, guided step-by-step wizards,
 * two-device "How to Connect" compatibility analysis, and local search.
 */

class NetworkConfigurationAssistant {
    constructor() {
        this.currentWizardStep = 1;
        this.wizardData = {};
        this.selectedDeviceForWizard = null;
    }

    // ================= 15-SECTION DEVICE GUIDE =================
    async showDeviceGuide(deviceOrType) {
        const modalEl = document.getElementById('assistantGuideModal');
        if (!modalEl) return;

        const devType = typeof deviceOrType === 'string' ? deviceOrType : (deviceOrType.category || deviceOrType.model_name || 'layer2_switch');
        const devName = typeof deviceOrType === 'object' ? deviceOrType.name : deviceOrType;

        const titleEl = document.getElementById('guideModalTitle');
        const bodyEl = document.getElementById('guideModalBody');
        if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-book-open text-info me-2"></i>Device Learning Guide: ${devName}`;

        bodyEl.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fa-solid fa-spinner fa-spin fa-2x text-info mb-2"></i>
                <p>Loading 15-section device architecture guide...</p>
            </div>
        `;

        const bsModal = new bootstrap.Modal(modalEl);
        bsModal.show();

        try {
            const resp = await fetch(`/api/knowledgebase/guide/?device_type=${encodeURIComponent(devType)}`);
            if (resp.ok) {
                const data = await resp.json();
                this.render15SectionGuide(bodyEl, data);
            } else {
                this.renderDefault15SectionGuide(bodyEl, devName, devType);
            }
        } catch (e) {
            this.renderDefault15SectionGuide(bodyEl, devName, devType);
        }
    }

    render15SectionGuide(container, data) {
        const g = data.guide || {};
        container.innerHTML = `
            <div class="accordion accordion-flush" id="guideAccordion">
                ${this.renderGuideSection(1, 'What is this device?', g.section1 || 'Core networking hardware/appliance used to forward frames or packets across local and wide-area networks.')}
                ${this.renderGuideSection(2, 'What does it do?', g.section2 || 'Provides physical and logical network connectivity, packet filtering, routing, or specialized network storage/video services.')}
                ${this.renderGuideSection(3, 'Why is it required?', g.section3 || 'Essential for interconnecting distributed computing nodes and establishing structured subnets.')}
                ${this.renderGuideSection(4, 'Where is it used?', g.section4 || 'Enterprise campus data closets, branch offices, industrial facilities, and home networks.')}
                ${this.renderGuideSection(5, 'How does it work?', g.section5 || 'Operates at OSI Layers 2-7, parsing protocol headers and referencing internal MAC, ARP, or routing tables.')}
                ${this.renderGuideSection(6, 'How does it connect to other devices?', g.section6 || 'Connects via Cat6 RJ45 twisted pair, single/multimode fiber optic cables, or 802.11 wireless links.')}
                ${this.renderGuideSection(7, 'Which ports and interfaces are available?', g.section7 || 'GigabitEthernet RJ45, 10G SFP+, Console RJ45/USB, and optional PoE+ power sourcing ports.')}
                ${this.renderGuideSection(8, 'What configurations are required?', g.section8 || 'Hostnames, management IP addresses, netmasks, default gateways, VLAN IDs, and administrative passwords.')}
                ${this.renderGuideSection(9, 'What protocols does it support?', g.section9 || 'IPv4, 802.1Q, STP/RSTP, OSPF, NAT, DHCP, DNS, SSH, and SNMP.')}
                ${this.renderGuideSection(10, 'What commands can be used?', g.section10 || 'show ip interface brief, show ip route, show running-config, ping, traceroute.')}
                ${this.renderGuideSection(11, 'How to verify the configuration?', g.section11 || 'Use ICMP ping, traceroute, and interface counter audits to verify end-to-end frame delivery.')}
                ${this.renderGuideSection(12, 'Common problems', g.section12 || 'Subnet mask mismatches, incorrect default gateway, administratively disabled interfaces, and VLAN isolation.')}
                ${this.renderGuideSection(13, 'Troubleshooting procedures', g.section13 || '1. Verify Layer 1 physical link LEDs. 2. Verify Layer 2 MAC learning and VLAN membership. 3. Ping local gateway.')}
                ${this.renderGuideSection(14, 'Security best practices', g.section14 || 'Disable unused interfaces, enforce port security, use SSH instead of Telnet, and configure strong passwords.')}
                ${this.renderGuideSection(15, 'Practical examples', g.section15 || 'Configuring an access port for an employee desktop on VLAN 10 with 802.1p Quality of Service.')}
            </div>
        `;
    }

    renderDefault15SectionGuide(container, name, type) {
        this.render15SectionGuide(container, {
            guide: {
                section1: `${name} is an enterprise network appliance designed for reliable packet forwarding and infrastructure support.`,
                section2: `Inspects and routes network traffic according to established Layer 2/3 protocols and security policies.`,
                section3: `Required to build scalable, fault-tolerant, and secure enterprise network segments.`,
                section4: `Deployed in corporate server rooms, wiring closets, and perimeter demarcation points.`,
                section5: `Processes frames using dedicated ASIC chipsets and maintains real-time lookup tables (CAM, ARP, Routing Table).`,
                section6: `Utilizes standard RJ45 Cat6 copper straight-through or LC/LC optical patch cords.`,
                section7: `Equipped with 10/100/1000 Mbps RJ45 interfaces and high-speed SFP/SFP+ uplink modules.`,
                section8: `Requires configuring IP address, netmask, default gateway, and authorized management access lists.`,
                section9: `Compliant with IEEE 802.3 Ethernet, IETF IPv4/IPv6, and standard routing/security RFCs.`,
                section10: `Configurable via Cisco IOS-inspired CLI, Linux iproute2, or intuitive Web GUI.`,
                section11: `Verified using end-to-end ICMP echo requests and link status command displays.`,
                section12: `Frequent failures involve cabling disconnects, speed/duplex negotiation mismatches, and firewall deny rules.`,
                section13: `Follow standard bottom-up methodology starting at Physical layer up through Application services.`,
                section14: `Shut down unused switchports, mandate encrypted SSHv2/HTTPS management, and change vendor defaults.`,
                section15: `Real-world implementation involves connecting upstream routers and downstream client workstations.`
            }
        });
    }

    renderGuideSection(num, title, content) {
        return `
            <div class="accordion-item bg-card border-secondary border-opacity-25 mb-2 rounded">
                <h2 class="accordion-header" id="heading${num}">
                    <button class="accordion-button collapsed bg-sidebar text-white py-2" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${num}">
                        <span class="badge bg-info text-dark me-2">#${num}</span> ${title}
                    </button>
                </h2>
                <div id="collapse${num}" class="accordion-collapse collapse" data-bs-parent="#guideAccordion">
                    <div class="accordion-body text-secondary small">
                        ${content}
                    </div>
                </div>
            </div>
        `;
    }

    // ================= GUIDED CONFIGURATION WIZARD =================
    openConfigWizard(device) {
        this.selectedDeviceForWizard = device;
        this.currentWizardStep = 1;
        this.wizardData = {
            hostname: device.name,
            ip: device.ip || '192.168.1.1',
            mask: device.subnet_mask || '255.255.255.0',
            gateway: device.gateway || '',
            vlanId: 10,
            vlanName: 'Data_VLAN'
        };

        const modalEl = document.getElementById('configWizardModal');
        if (!modalEl) return;
        this.renderWizardStep(1);
        const bsModal = new bootstrap.Modal(modalEl);
        bsModal.show();
    }

    renderWizardStep(stepNum) {
        this.currentWizardStep = stepNum;
        const container = document.getElementById('wizardStepContent');
        if (!container) return;

        const dev = this.selectedDeviceForWizard;

        if (stepNum === 1) {
            container.innerHTML = `
                <div class="mb-3">
                    <label class="form-label text-white">Step 1: Set Device Hostname</label>
                    <p class="text-muted small">The hostname uniquely identifies this device in CLI prompts and network monitoring tools.</p>
                    <input type="text" class="form-control" id="wiz-hostname" value="${this.wizardData.hostname}" />
                </div>
                <div class="p-3 bg-sidebar rounded border border-secondary border-opacity-25">
                    <span class="text-info font-monospace">CLI Command:</span>
                    <pre class="mb-0 text-success font-monospace">hostname ${this.wizardData.hostname}</pre>
                </div>
            `;
        } else if (stepNum === 2) {
            container.innerHTML = `
                <div class="mb-3">
                    <label class="form-label text-white">Step 2: Configure Management IP & Subnet Mask</label>
                    <p class="text-muted small">Assigns the logical IPv4 address used to manage and route traffic through this device.</p>
                    <div class="row g-2">
                        <div class="col-md-7">
                            <label class="form-label small text-muted">IP Address</label>
                            <input type="text" class="form-control" id="wiz-ip" value="${this.wizardData.ip}" />
                        </div>
                        <div class="col-md-5">
                            <label class="form-label small text-muted">Subnet Mask</label>
                            <input type="text" class="form-control" id="wiz-mask" value="${this.wizardData.mask}" />
                        </div>
                    </div>
                </div>
                <div class="p-3 bg-sidebar rounded border border-secondary border-opacity-25">
                    <span class="text-info font-monospace">CLI Command:</span>
                    <pre class="mb-0 text-success font-monospace">interface GigabitEthernet0/0\n ip address ${this.wizardData.ip} ${this.wizardData.mask}\n no shutdown</pre>
                </div>
            `;
        } else if (stepNum === 3) {
            container.innerHTML = `
                <div class="mb-3">
                    <label class="form-label text-white">Step 3: Configure Default Gateway</label>
                    <p class="text-muted small">The next-hop router IP where packets destined for remote subnets are forwarded.</p>
                    <input type="text" class="form-control" id="wiz-gateway" value="${this.wizardData.gateway}" placeholder="e.g. 192.168.1.1" />
                </div>
                <div class="p-3 bg-sidebar rounded border border-secondary border-opacity-25">
                    <span class="text-info font-monospace">CLI Command:</span>
                    <pre class="mb-0 text-success font-monospace">ip default-gateway ${this.wizardData.gateway || '192.168.1.1'}</pre>
                </div>
            `;
        } else if (stepNum === 4) {
            container.innerHTML = `
                <div class="mb-3">
                    <label class="form-label text-white">Step 4: Create Local VLAN</label>
                    <p class="text-muted small">Segments broadcast traffic into an isolated logical network.</p>
                    <div class="row g-2">
                        <div class="col-md-4">
                            <label class="form-label small text-muted">VLAN ID (1-4094)</label>
                            <input type="number" class="form-control" id="wiz-vlan-id" value="${this.wizardData.vlanId}" />
                        </div>
                        <div class="col-md-8">
                            <label class="form-label small text-muted">VLAN Name</label>
                            <input type="text" class="form-control" id="wiz-vlan-name" value="${this.wizardData.vlanName}" />
                        </div>
                    </div>
                </div>
                <div class="p-3 bg-sidebar rounded border border-secondary border-opacity-25">
                    <span class="text-info font-monospace">CLI Command:</span>
                    <pre class="mb-0 text-success font-monospace">vlan ${this.wizardData.vlanId}\n name ${this.wizardData.vlanName}</pre>
                </div>
            `;
        } else if (stepNum === 5) {
            container.innerHTML = `
                <div class="mb-3 text-center">
                    <i class="fa-solid fa-circle-check text-success fa-3x mb-2"></i>
                    <h5 class="text-white">Ready to Apply Configuration!</h5>
                    <p class="text-muted small">Review the configured parameters below. Clicking Apply will update the simulated device in real-time.</p>
                </div>
                <div class="p-3 bg-sidebar rounded border border-secondary border-opacity-25 font-monospace small">
                    <div><strong>Device:</strong> ${this.wizardData.hostname}</div>
                    <div><strong>Management IP:</strong> ${this.wizardData.ip} / ${this.wizardData.mask}</div>
                    <div><strong>Gateway:</strong> ${this.wizardData.gateway || 'None'}</div>
                    <div><strong>VLAN:</strong> ${this.wizardData.vlanId} (${this.wizardData.vlanName})</div>
                </div>
            `;
        }

        // Update step indicator
        document.getElementById('wizCurrentStepBadge').textContent = `Step ${stepNum} of 5`;
        const nextBtn = document.getElementById('wizNextBtn');
        if (nextBtn) {
            nextBtn.textContent = stepNum === 5 ? 'Apply to Device' : 'Next Step →';
        }
    }

    wizardNext() {
        if (this.currentWizardStep === 1) {
            const h = document.getElementById('wiz-hostname')?.value;
            if (h) this.wizardData.hostname = h;
            this.renderWizardStep(2);
        } else if (this.currentWizardStep === 2) {
            const ip = document.getElementById('wiz-ip')?.value;
            const mask = document.getElementById('wiz-mask')?.value;
            if (ip) this.wizardData.ip = ip;
            if (mask) this.wizardData.mask = mask;
            this.renderWizardStep(3);
        } else if (this.currentWizardStep === 3) {
            const gw = document.getElementById('wiz-gateway')?.value;
            if (gw) this.wizardData.gateway = gw;
            this.renderWizardStep(4);
        } else if (this.currentWizardStep === 4) {
            const vid = document.getElementById('wiz-vlan-id')?.value;
            const vname = document.getElementById('wiz-vlan-name')?.value;
            if (vid) this.wizardData.vlanId = parseInt(vid);
            if (vname) this.wizardData.vlanName = vname;
            this.renderWizardStep(5);
        } else if (this.currentWizardStep === 5) {
            // Apply to simulated device
            if (this.selectedDeviceForWizard) {
                this.selectedDeviceForWizard.name = this.wizardData.hostname;
                this.selectedDeviceForWizard.ip = this.wizardData.ip;
                this.selectedDeviceForWizard.subnet_mask = this.wizardData.mask;
                this.selectedDeviceForWizard.gateway = this.wizardData.gateway;
                this.selectedDeviceForWizard.vlans = this.selectedDeviceForWizard.vlans || {};
                this.selectedDeviceForWizard.vlans[this.wizardData.vlanId] = { name: this.wizardData.vlanName };

                window.ramonetCanvas?.renderDeviceNode(this.selectedDeviceForWizard);
                window.ramonetCanvas?.triggerChange(`Configured ${this.wizardData.hostname} via Wizard`);
                window.ramonetUI?.showToast('Configuration Applied', `Updated ${this.wizardData.hostname} successfully!`, 'success');
            }
            const modalEl = document.getElementById('configWizardModal');
            bootstrap.Modal.getInstance(modalEl)?.hide();
        }
    }

    // ================= TWO-DEVICE "HOW TO CONNECT" ASSISTANT =================
    async showHowToConnect(srcCategory, destCategory) {
        const modalEl = document.getElementById('howToConnectModal');
        if (!modalEl) return;

        const bodyEl = document.getElementById('howToConnectBody');
        bodyEl.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fa-solid fa-spinner fa-spin fa-2x text-info mb-2"></i>
                <p>Analyzing physical & logical interface compatibility...</p>
            </div>
        `;

        const bsModal = new bootstrap.Modal(modalEl);
        bsModal.show();

        try {
            const resp = await fetch(`/api/knowledgebase/how-to-connect/?src=${encodeURIComponent(srcCategory)}&target=${encodeURIComponent(destCategory)}`);
            if (resp.ok) {
                const data = await resp.json();
                this.renderHowToConnectReport(bodyEl, data);
            } else {
                this.renderDefaultConnectReport(bodyEl, srcCategory, destCategory);
            }
        } catch (e) {
            this.renderDefaultConnectReport(bodyEl, srcCategory, destCategory);
        }
    }

    renderHowToConnectReport(container, rule) {
        let instructionsHtml = '';
        (rule.step_by_step_instructions || []).forEach((s, idx) => {
            instructionsHtml += `<li class="mb-2"><span class="badge bg-secondary me-2">${idx + 1}</span>${s}</li>`;
        });

        let verifyHtml = '';
        (rule.verification_commands || []).forEach(v => {
            verifyHtml += `<div class="font-monospace text-success small mb-1"><i class="fa-solid fa-angle-right me-1"></i>${v}</div>`;
        });

        container.innerHTML = `
            <div class="p-3 mb-3 bg-sidebar rounded border border-secondary border-opacity-25">
                <div class="row g-2">
                    <div class="col-md-6">
                        <small class="text-muted d-block">Recommended Cable:</small>
                        <strong class="text-info"><i class="fa-solid fa-plug me-1"></i>${rule.recommended_cable || 'Cat6 Copper Straight-Through'}</strong>
                    </div>
                    <div class="col-md-6">
                        <small class="text-muted d-block">Required Port Type:</small>
                        <strong class="text-white"><i class="fa-solid fa-ethernet me-1"></i>${rule.required_ports || 'Gigabit RJ45 Ethernet'}</strong>
                    </div>
                </div>
            </div>

            <h6 class="text-white mb-2"><i class="fa-solid fa-list-check text-info me-2"></i>Step-by-Step Connection Instructions</h6>
            <ol class="list-unstyled text-secondary small mb-3">
                ${instructionsHtml || '<li>Connect cable securely between corresponding RJ45 ports.</li>'}
            </ol>

            <h6 class="text-white mb-2"><i class="fa-solid fa-terminal text-info me-2"></i>Verification Commands</h6>
            <div class="p-2 bg-sidebar rounded border border-secondary border-opacity-25 mb-3">
                ${verifyHtml || '<div class="text-muted small">ping & show ip interface brief</div>'}
            </div>

            <div class="p-2 bg-warning-subtle text-warning-emphasis rounded small">
                <i class="fa-solid fa-lightbulb me-1"></i><strong>Pro-Tip:</strong> ${rule.power_requirements || 'Verify PoE power budget and interface shutdown states.'}
            </div>
        `;
    }

    renderDefaultConnectReport(container, src, dest) {
        this.renderHowToConnectReport(container, {
            recommended_cable: 'Cat6 Copper Straight-Through (RJ45)',
            required_ports: 'GigabitEthernet 10/100/1000 Mbps',
            step_by_step_instructions: [
                `Locate an available RJ45 interface on the ${src}.`,
                `Connect a certified Cat6 straight-through patch cable.`,
                `Connect the other end to the ${dest}.`,
                `Verify link status indicator LEDs turn green.`,
                `Configure IP addresses in the same subnet mask.`
            ],
            verification_commands: ['show ip interface brief', 'ping <target_ip>'],
            power_requirements: 'Standard AC power supplies required for both endpoints.'
        });
    }

    // ================= LOCAL KNOWLEDGE SEARCH =================
    async searchHelp(query) {
        if (!query || query.trim().length < 2) return [];
        try {
            const resp = await fetch(`/api/knowledgebase/search/?q=${encodeURIComponent(query.trim())}`);
            if (resp.ok) {
                return await resp.json();
            }
        } catch (e) {
            console.warn('Local help search fetch failed:', e);
        }
        return [];
    }
}

window.ramonetAssistant = new NetworkConfigurationAssistant();
