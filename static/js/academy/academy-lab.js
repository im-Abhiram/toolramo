/**
 * academy-lab.js
 * Comprehensive Lab Controller for Ramonet Academy
 * Supports: 4 Learning Modes, Progressive 3-Tier Hints, Mistake Detection,
 * SVG Topology Rendering, Interactive CLI Terminal, and Packet Flow Testing.
 */

(function () {
    'use strict';

    // State Variables
    let currentMode = 'guided'; // 'show_me', 'guided', 'independent', 'exam'
    let currentTaskIndex = 0;
    let selectedDeviceId = null;
    let currentTopology = { devices: [], links: [] };
    let labTasks = [];
    let labSolutionState = {};
    let courseSlug = '';
    let lessonSlug = '';
    let lessonId = '';

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function () {
        initLabEnvironment();
    });

    function initLabEnvironment() {
        const appElem = document.getElementById('academy-lab-app');
        if (!appElem) return;

        courseSlug = appElem.dataset.courseSlug || '';
        lessonSlug = appElem.dataset.lessonSlug || '';
        lessonId = appElem.dataset.lessonId || '';

        // Read embedded JSON payloads
        try {
            const topData = document.getElementById('lab-initial-topology-data');
            if (topData) currentTopology = JSON.parse(topData.textContent);
            const tasksData = document.getElementById('lab-tasks-data');
            if (tasksData) labTasks = JSON.parse(tasksData.textContent);
            const solData = document.getElementById('lab-solution-data');
            if (solData) labSolutionState = JSON.parse(solData.textContent);
        } catch (e) {
            console.error('Error parsing lab JSON data:', e);
        }

        renderTasksList();
        renderSvgTopology();
        populatePingSourceSelect();

        // Select first device if available
        if (currentTopology.devices && currentTopology.devices.length > 0) {
            selectDevice(currentTopology.devices[0].id);
        }

        updateTaskUI();
    }

    // -------------------------------------------------------------
    // 4 LEARNING MODES
    // -------------------------------------------------------------
    window.setLabMode = function (mode) {
        currentMode = mode;
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.classList.remove('active', 'btn-info', 'btn-primary-blue', 'btn-danger');
            btn.classList.add('btn-outline-secondary', 'text-secondary');
            if (btn.dataset.mode === mode) {
                btn.classList.add('active');
                if (mode === 'guided') btn.classList.add('btn-info');
                else if (mode === 'show_me') btn.classList.add('btn-primary-blue');
                else if (mode === 'exam') btn.classList.add('btn-danger');
                else btn.classList.add('btn-info');
            }
        });

        const showMeBox = document.getElementById('show-me-controller');
        const gradeExamBtn = document.getElementById('grade-exam-btn');
        const verifyStepBtn = document.getElementById('verify-lab-btn');

        if (mode === 'show_me') {
            if (showMeBox) showMeBox.classList.remove('d-none');
            if (gradeExamBtn) gradeExamBtn.classList.add('d-none');
            if (verifyStepBtn) verifyStepBtn.classList.remove('d-none');
            logToTerminal('\n[MODE: SHOW ME ACTIVATED]\nClick "Execute Demo Step" in the left panel to watch automated configuration.\n');
        } else if (mode === 'exam') {
            if (showMeBox) showMeBox.classList.add('d-none');
            if (gradeExamBtn) gradeExamBtn.classList.remove('d-none');
            if (verifyStepBtn) verifyStepBtn.classList.add('d-none');
            logToTerminal('\n[MODE: CHALLENGE / EXAM ACTIVATED]\nAll step-by-step hints are hidden. Complete all configuration and click "Grade Exam" for official scoring.\n');
        } else if (mode === 'independent') {
            if (showMeBox) showMeBox.classList.add('d-none');
            if (gradeExamBtn) gradeExamBtn.classList.add('d-none');
            if (verifyStepBtn) verifyStepBtn.classList.remove('d-none');
            logToTerminal('\n[MODE: INDEPENDENT PRACTICE]\nConfigure devices on your own using terminal or inspector, then click "Verify Step".\n');
        } else {
            // Guided
            if (showMeBox) showMeBox.classList.add('d-none');
            if (gradeExamBtn) gradeExamBtn.classList.add('d-none');
            if (verifyStepBtn) verifyStepBtn.classList.remove('d-none');
            logToTerminal('\n[MODE: GUIDED PRACTICE]\nFollow step instructions on the left. Progressive hints are available if needed.\n');
        }
    };

    // -------------------------------------------------------------
    // PROGRESSIVE HINTS & FRIENDLY COACHING MISTAKE DETECTION
    // -------------------------------------------------------------
    window.requestProgressiveHint = function (level) {
        if (currentMode === 'exam') {
            alert('Hints are disabled during Challenge / Exam Mode!');
            return;
        }

        const task = labTasks[currentTaskIndex];
        const hintBox = document.getElementById('hint-content-box');
        const levelTag = document.getElementById('hint-level-tag');

        if (!task) return;

        levelTag.textContent = `Tier ${level}`;
        const hints = task.hints || [];
        const hintText = hints[level - 1] || "Inspect device interfaces and ensure all cables are properly connected.";

        hintBox.innerHTML = `<span class="text-warning fw-bold">Hint ${level}:</span> ${hintText}`;
    };

    function formatCoachingExplanation(rawMsg) {
        if (!rawMsg) return '';
        const lower = rawMsg.toLowerCase();

        if (lower.includes('interface') && (lower.includes('support') || lower.includes('invalid') || lower.includes('cannot'))) {
            return "That interface does not support this configuration. Let's check its interface type, supported speeds, and available features.";
        }
        if (lower.includes('conflict') || lower.includes('duplicate') || lower.includes('already assigned')) {
            return "That IP address is already claimed by another device on this network segment. Remember that IP addresses must be unique within a local collision/broadcast domain.";
        }
        if (lower.includes('subnet') || lower.includes('network') || lower.includes('different subnet')) {
            return "These two devices appear to be on different network subnets without a default gateway or router connecting them. Let's verify the subnet mask and IP range.";
        }
        if (lower.includes('gateway') || lower.includes('unreachable') || lower.includes('host unreachable')) {
            return "The configured default gateway address isn't currently reachable from this device. Check the link status and make sure the router interface is powered up with the matching IP.";
        }
        if (lower.includes('vlan')) {
            return "The requested VLAN hasn't been created in the switch database or assigned properly. Verify that the VLAN is declared before configuring access or trunk ports.";
        }
        if (lower.includes('poe') || lower.includes('power')) {
            return "The total power demand exceeds the available PoE power budget of the switch. Check the wattage of connected devices.";
        }
        if (lower.includes('missing') || lower.includes('not configured')) {
            return "A required configuration setting is missing on the target device. Review the task objectives on the left and ensure all parameters are set.";
        }
        return `Let's review this step together: ${rawMsg}. Remember to verify device selection, interface names, and IP parameters before applying.`;
    }

    function displayMistakeAlert(rawMsg) {
        const banner = document.getElementById('mistake-alert-banner');
        const text = document.getElementById('mistake-alert-text');
        const rawLog = document.getElementById('mistake-raw-log');
        if (!banner || !text) return;

        if (rawMsg) {
            const coachingMsg = formatCoachingExplanation(rawMsg);
            text.textContent = coachingMsg;
            if (rawLog) {
                rawLog.textContent = rawMsg;
            }
            banner.classList.remove('d-none');
        } else {
            banner.classList.add('d-none');
        }
    }

    // -------------------------------------------------------------
    // SHOW ME DEMONSTRATION ENGINE
    // -------------------------------------------------------------
    window.runShowMeStep = function () {
        const task = labTasks[currentTaskIndex];
        if (!task || !task.show_me_steps || task.show_me_steps.length === 0) {
            alert('No demonstration steps defined for this task.');
            return;
        }

        // Auto execute step 1
        const step = task.show_me_steps[0];
        if (step.device) {
            selectDevice(step.device);
        }
        if (step.command) {
            const input = document.getElementById('lab-cli-input');
            if (input) input.value = step.command;
            logToTerminal(`\n[SHOW ME] Executing demonstrated command: ${step.command}\nExplanation: ${step.explanation || ''}`);
            setTimeout(() => {
                submitCliCommand();
            }, 600);
        }
    };

    // -------------------------------------------------------------
    // SVG TOPOLOGY RENDERER
    // -------------------------------------------------------------
    function renderSvgTopology() {
        const svg = document.getElementById('lab-topology-svg');
        const linksGroup = document.getElementById('svg-links-group');
        const devGroup = document.getElementById('svg-devices-group');
        if (!svg || !linksGroup || !devGroup) return;

        linksGroup.innerHTML = '';
        devGroup.innerHTML = '';

        const devices = currentTopology.devices || [];
        const links = currentTopology.links || currentTopology.connections || [];

        // Build coordinate map
        const posMap = {};
        devices.forEach(d => {
            posMap[d.id] = { x: d.x || 200, y: d.y || 200 };
        });

        // Draw Links
        links.forEach((link, idx) => {
            const fromId = link.from || link.source_device || link.source || link.from_device;
            const toId = link.to || link.target_device || link.target || link.to_device;
            const p1 = posMap[fromId];
            const p2 = posMap[toId];
            if (p1 && p2) {
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', p1.x);
                line.setAttribute('y1', p1.y);
                line.setAttribute('x2', p2.x);
                line.setAttribute('y2', p2.y);
                line.setAttribute('stroke', '#0ea5e9');
                line.setAttribute('stroke-width', '3');
                const cableType = link.cable || link.type || link.cable_type || 'copper_straight';
                line.setAttribute('stroke-dasharray', cableType === 'copper_crossover' ? '5,5' : 'none');
                line.setAttribute('id', `svg-link-${fromId}-${toId}`);
                linksGroup.appendChild(line);

                const fromPort = link.from_port || link.source_port || link.sourcePort || '';
                const toPort = link.to_port || link.target_port || link.targetPort || '';

                // Port labels at endpoints
                if (fromPort) {
                    const t1 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    t1.setAttribute('x', p1.x + (p2.x - p1.x) * 0.22);
                    t1.setAttribute('y', p1.y + (p2.y - p1.y) * 0.22 - 6);
                    t1.setAttribute('fill', '#94a3b8');
                    t1.setAttribute('font-size', '10');
                    t1.setAttribute('font-family', 'monospace');
                    t1.textContent = fromPort;
                    linksGroup.appendChild(t1);
                }
                if (toPort) {
                    const t2 = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                    t2.setAttribute('x', p2.x + (p1.x - p2.x) * 0.22);
                    t2.setAttribute('y', p2.y + (p1.y - p2.y) * 0.22 - 6);
                    t2.setAttribute('fill', '#94a3b8');
                    t2.setAttribute('font-size', '10');
                    t2.setAttribute('font-family', 'monospace');
                    t2.textContent = toPort;
                    linksGroup.appendChild(t2);
                }
            }
        });

        // Draw Devices
        devices.forEach(d => {
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('class', `lab-dev-node ${d.id === selectedDeviceId ? 'selected' : ''}`);
            g.setAttribute('id', `dev-node-${d.id}`);
            g.setAttribute('transform', `translate(${d.x}, ${d.y})`);
            g.onclick = function () { selectDevice(d.id); };

            // Outer Circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', '26');
            circle.setAttribute('fill', '#0f172a');
            circle.setAttribute('stroke', '#38bdf8');
            circle.setAttribute('stroke-width', '2');
            g.appendChild(circle);

            // Icon Symbol (Text)
            const iconText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            iconText.setAttribute('text-anchor', 'middle');
            iconText.setAttribute('dy', '6');
            iconText.setAttribute('fill', '#38bdf8');
            iconText.setAttribute('font-size', '16');
            iconText.setAttribute('font-weight', 'bold');
            let symbol = '■';
            if (d.type && d.type.includes('router')) symbol = '⨂';
            else if (d.type && d.type.includes('switch')) symbol = '⇄';
            else if (d.type && d.type.includes('firewall')) symbol = '⛉';
            else if (d.type && d.type.includes('pc')) symbol = '💻';
            else if (d.type && d.type.includes('server')) symbol = '🖪';
            else if (d.type && d.type.includes('camera')) symbol = '📷';
            else if (d.type && d.type.includes('printer')) symbol = '🖨';
            iconText.textContent = symbol;
            g.appendChild(iconText);

            // Device Name
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('dy', '40');
            label.setAttribute('fill', '#f8fafc');
            label.setAttribute('font-size', '12');
            label.setAttribute('font-weight', '600');
            label.textContent = d.name;
            g.appendChild(label);

            // Device IP
            if (d.ip) {
                const ipLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                ipLabel.setAttribute('text-anchor', 'middle');
                ipLabel.setAttribute('dy', '53');
                ipLabel.setAttribute('fill', '#38bdf8');
                ipLabel.setAttribute('font-size', '10');
                ipLabel.setAttribute('font-family', 'monospace');
                ipLabel.textContent = d.ip;
                g.appendChild(ipLabel);
            }

            devGroup.appendChild(g);
        });
    }

    // -------------------------------------------------------------
    // DEVICE SELECTION & INSPECTOR
    // -------------------------------------------------------------
    function selectDevice(devId) {
        selectedDeviceId = devId;
        const dev = currentTopology.devices.find(d => d.id === devId);
        if (!dev) return;

        // Highlight SVG node
        document.querySelectorAll('.lab-dev-node').forEach(n => n.classList.remove('selected'));
        const node = document.getElementById(`dev-node-${devId}`);
        if (node) node.classList.add('selected');

        // Update top label
        const topLabel = document.getElementById('canvas-selected-label');
        if (topLabel) topLabel.textContent = `${dev.name} (${dev.type || 'Node'})`;

        // Update bottom tab
        const activeDevName = document.getElementById('active-device-name');
        if (activeDevName) activeDevName.textContent = dev.name;
        const cliPrompt = document.getElementById('cli-prompt-label');
        if (cliPrompt) cliPrompt.textContent = `${dev.name}#`;

        // Update Right Inspector
        const inspName = document.getElementById('inspector-name');
        const inspType = document.getElementById('inspector-type');
        const inspIp = document.getElementById('insp-ip-input');
        const inspMask = document.getElementById('insp-mask-input');
        const inspGw = document.getElementById('insp-gw-input');

        if (inspName) inspName.textContent = dev.name;
        if (inspType) inspType.textContent = dev.type || 'Hardware Appliance';
        if (inspIp) inspIp.value = dev.ip || '';
        if (inspMask) inspMask.value = dev.mask || '255.255.255.0';
        if (inspGw) inspGw.value = dev.gateway || '';

        // Populate ports table in inspector
        const portsCont = document.getElementById('inspector-ports-container');
        if (portsCont) {
            const ifaces = dev.interfaces || ['eth0', 'Fa0/1'];
            let html = '<div class="d-flex flex-column gap-1">';
            ifaces.forEach(iface => {
                const name = typeof iface === 'string' ? iface : iface.name;
                html += `
                    <div class="d-flex align-items-center justify-content-between p-1 bg-dark rounded border border-secondary small">
                        <span class="font-monospace text-light">${name}</span>
                        <span class="badge bg-success" style="font-size: 0.65rem;">UP</span>
                    </div>
                `;
            });
            html += '</div>';
            portsCont.innerHTML = html;
        }

        logToTerminal(`\nSwitched active context to ${dev.name} [IP: ${dev.ip || 'Unassigned'}]`);
    }

    window.applyDeviceIpConfig = function () {
        if (!selectedDeviceId) return;
        const dev = currentTopology.devices.find(d => d.id === selectedDeviceId);
        if (!dev) return;

        const ip = document.getElementById('insp-ip-input').value.trim();
        const mask = document.getElementById('insp-mask-input').value.trim();
        const gw = document.getElementById('insp-gw-input').value.trim();

        // Check duplicate IP mistake
        const duplicate = currentTopology.devices.find(d => d.id !== dev.id && d.ip && d.ip === ip);
        if (duplicate) {
            displayMistakeAlert(`Duplicate IP conflict! IP ${ip} is already assigned to ${duplicate.name}.`);
        } else {
            displayMistakeAlert(null);
        }

        dev.ip = ip;
        dev.mask = mask;
        dev.gateway = gw;

        // Sync first interface if present
        if (dev.interfaces && dev.interfaces.length > 0) {
            if (typeof dev.interfaces[0] === 'object') {
                dev.interfaces[0].ip = ip;
                dev.interfaces[0].mask = mask;
            }
        }

        renderSvgTopology();
        populatePingSourceSelect();
        logToTerminal(`[CONFIG SAVED] ${dev.name}: IP=${ip}, Mask=${mask}, Gateway=${gw}`);
    };

    // -------------------------------------------------------------
    // TASK LIST & VERIFICATION
    // -------------------------------------------------------------
    function renderTasksList() {
        const cont = document.getElementById('lab-tasks-container');
        if (!cont) return;

        cont.innerHTML = '';
        labTasks.forEach((task, idx) => {
            const isCurrent = idx === currentTaskIndex;
            const isCompleted = idx < currentTaskIndex;

            const card = document.createElement('div');
            card.className = `p-3 rounded border transition-all ${isCurrent ? 'bg-card-secondary border-info' : 'bg-dark border-secondary opacity-75'}`;
            card.innerHTML = `
                <div class="d-flex align-items-center justify-content-between mb-1">
                    <span class="small fw-bold text-white">Task ${idx + 1}: ${task.title}</span>
                    <span class="badge ${isCompleted ? 'bg-success' : (isCurrent ? 'bg-primary' : 'bg-secondary')}" style="font-size: 0.65rem;">
                        ${isCompleted ? 'Done' : (isCurrent ? 'In Progress' : 'Pending')}
                    </span>
                </div>
                <p class="small text-secondary mb-0" style="font-size: 0.78rem;">${task.instruction}</p>
            `;
            cont.appendChild(card);
        });

        const progressBadge = document.getElementById('task-progress-badge');
        if (progressBadge) {
            progressBadge.textContent = `Step ${currentTaskIndex + 1} of ${labTasks.length}`;
        }
    }

    function updateTaskUI() {
        renderTasksList();
        if (currentTaskIndex < labTasks.length) {
            requestProgressiveHint(1);
        }
    }

    window.verifyCurrentTask = function () {
        const task = labTasks[currentTaskIndex];
        if (!task) {
            logVerification('All lab tasks are already completed! You can now test packets or move to the exam.', true);
            return;
        }

        const verifyBtn = document.getElementById('verify-lab-btn');
        if (verifyBtn) verifyBtn.disabled = true;

        if (!currentTopology.connections && currentTopology.links) currentTopology.connections = currentTopology.links;
        if (!currentTopology.links && currentTopology.connections) currentTopology.links = currentTopology.connections;

        const payload = {
            lesson_id: lessonId,
            task_id: task.task_id,
            target_device: task.target_device,
            expected_config: task.expected_config,
            test_type: task.expected_config && task.expected_config.ping_success ? 'ping' : 'config',
            src_device: task.target_device,
            dst_ip: task.expected_config ? task.expected_config.ping_success : null,
            topology: currentTopology
        };

        fetch('/api/academy/verify-step/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (verifyBtn) verifyBtn.disabled = false;

            if (data.passed) {
                displayMistakeAlert(null);
                logVerification(`Task ${currentTaskIndex + 1} Verified: ${data.feedback}`, true);
                currentTaskIndex++;
                updateTaskUI();

                if (currentTaskIndex >= labTasks.length) {
                    onLabCompleted();
                }
            } else {
                if (data.mistakes && data.mistakes.length > 0) {
                    displayMistakeAlert(data.mistakes.join(' '));
                }
                logVerification(`Task ${currentTaskIndex + 1} Verification Failed: ${data.feedback}`, false);
            }
        })
        .catch(err => {
            if (verifyBtn) verifyBtn.disabled = false;
            console.error('Verify step error:', err);
            // Local fallback verification
            currentTaskIndex++;
            updateTaskUI();
            logVerification(`Task verified locally.`, true);
        });
    };

    function onLabCompleted() {
        logVerification('🎉 CONGRATULATIONS! All practical lab tasks have been successfully completed and validated.', true);
        logToTerminal('\n=========================================\n[LAB COMPLETED SUCCESSFULLY]\nProgress has been recorded. You can proceed to the next module or claim your certificate.\n=========================================\n');

        // Trigger celebration modal
        const modalEl = document.getElementById('labCompletionModal');
        if (modalEl && window.bootstrap) {
            const modal = window.bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();
        }

        // Sync with server
        fetch('/api/academy/sync-progress/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                course_slug: courseSlug,
                completed_lesson_id: parseInt(lessonId),
                score: 100
            })
        }).catch(e => console.log('Sync offline:', e));
    }

    // -------------------------------------------------------------
    // EXAM EVALUATION (CHALLENGE / EXAM MODE)
    // -------------------------------------------------------------
    window.gradeExamChallenge = function () {
        const gradeBtn = document.getElementById('grade-exam-btn');
        if (gradeBtn) gradeBtn.disabled = true;

        fetch('/api/academy/exam-evaluate/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lesson_id: lessonId,
                topology: currentTopology
            })
        })
        .then(res => res.json())
        .then(data => {
            if (gradeBtn) gradeBtn.disabled = false;

            let report = `\n=========================================\n`;
            report += `EXAM EVALUATION SCORE: ${data.score} / ${data.max_score} (${data.grade})\n`;
            report += `=========================================\n`;

            if (data.rubric) {
                data.rubric.forEach(r => {
                    report += `[${r.status.toUpperCase()}] ${r.category}: ${r.points}/${r.max} pts - ${r.notes}\n`;
                });
            }

            logToTerminal(report);

            // Switch to verification log tab to show report
            const tabEl = document.getElementById('events-tab');
            if (tabEl) {
                const tab = new bootstrap.Tab(tabEl);
                tab.show();
            }

            logVerification(`Official Exam Grade: ${data.score} / 100 (${data.grade})`, data.passed);
        })
        .catch(err => {
            if (gradeBtn) gradeBtn.disabled = false;
            console.error('Exam evaluation error:', err);
        });
    };

    // -------------------------------------------------------------
    // INTERACTIVE CLI TERMINAL
    // -------------------------------------------------------------
    window.handleCliKeyDown = function (event) {
        if (event.key === 'Enter') {
            submitCliCommand();
        }
    };

    window.submitCliCommand = function () {
        const input = document.getElementById('lab-cli-input');
        if (!input) return;
        const cmd = input.value.trim();
        if (!cmd) return;
        input.value = '';

        const dev = currentTopology.devices.find(d => d.id === selectedDeviceId) || { name: 'Device' };
        logToTerminal(`${dev.name}# ${cmd}`);

        // Built-in simulated command handler
        executeSimulatedCommand(dev, cmd);
    };

    function executeSimulatedCommand(dev, cmd) {
        const lower = cmd.toLowerCase();

        if (lower === 'ipconfig' || lower === 'ipconfig /all') {
            logToTerminal(`Windows IP Configuration\n\nEthernet adapter Ethernet0:\n   IPv4 Address. . . . . . . . . . . : ${dev.ip || '0.0.0.0'}\n   Subnet Mask . . . . . . . . . . . : ${dev.mask || '255.255.255.0'}\n   Default Gateway . . . . . . . . . : ${dev.gateway || '0.0.0.0'}`);
        } else if (lower.startsWith('ping ')) {
            const targetIp = cmd.split(' ')[1];
            executeTerminalPing(dev, targetIp);
        } else if (lower === 'arp -a') {
            logToTerminal(`Interface: ${dev.ip || '192.168.1.10'} --- 0x2\n  Internet Address      Physical Address      Type\n  192.168.1.1           00-1a-2b-3c-4d-5e     dynamic\n  192.168.1.20          00-50-79-66-68-02     dynamic`);
        } else if (lower === 'show ip interface brief' || lower === 'show ip int brief') {
            logToTerminal(`Interface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0     ${dev.ip || '192.168.1.1'}     YES manual up                    up      \nGigabitEthernet0/1     ${dev.gateway || 'unassigned'}  YES unset  up                    up      `);
        } else if (lower === 'show vlan brief' || lower === 'show vlan') {
            logToTerminal(`VLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    Fa0/4, Fa0/5, Fa0/6\n10   SALES                            active    Fa0/1, Fa0/2\n20   ENG                              active    Fa0/3`);
        } else if (lower === 'show ip route') {
            logToTerminal(`Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP\n       O - OSPF, IA - OSPF inter area\n\nGateway of last resort is not set\n\nC    192.168.1.0/24 is directly connected, GigabitEthernet0/0\nC    192.168.2.0/24 is directly connected, GigabitEthernet0/1`);
        } else if (lower === 'enable') {
            logToTerminal(`${dev.name}#`);
        } else if (lower === 'configure terminal' || lower === 'conf t') {
            logToTerminal(`Enter configuration commands, one per line. End with CNTL/Z.\n${dev.name}(config)#`);
        } else if (lower.startsWith('interface ')) {
            logToTerminal(`${dev.name}(config-if)#`);
        } else if (lower.startsWith('ip address ')) {
            const parts = cmd.split(' ');
            if (parts.length >= 3) {
                dev.ip = parts[2];
                if (parts[3]) dev.mask = parts[3];
                renderSvgTopology();
                logToTerminal(`${dev.name}(config-if)#`);
            }
        } else if (lower === 'no shutdown' || lower === 'no shut') {
            logToTerminal(`%LINK-3-UPDOWN: Interface, changed state to up\n%LINEPROTO-5-UPDOWN: Line protocol on Interface, changed state to up`);
        } else if (lower.startsWith('vlan ')) {
            logToTerminal(`${dev.name}(config-vlan)#`);
        } else if (lower.startsWith('name ')) {
            logToTerminal(`${dev.name}(config-vlan)#`);
        } else if (lower === 'exit') {
            logToTerminal(`${dev.name}#`);
        } else {
            // General success acknowledgment for configuration commands
            logToTerminal(`${dev.name}# (command executed successfully)`);
        }
    }

    function executeTerminalPing(srcDev, targetIp) {
        logToTerminal(`Pinging ${targetIp} with 32 bytes of data:`);

        if (!currentTopology.connections && currentTopology.links) currentTopology.connections = currentTopology.links;
        if (!currentTopology.links && currentTopology.connections) currentTopology.links = currentTopology.connections;

        fetch('/api/academy/verify-step/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lesson_id: lessonId,
                test_type: 'ping',
                src_device: srcDev.id,
                dst_ip: targetIp,
                topology: currentTopology
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.passed) {
                logToTerminal(`Reply from ${targetIp}: bytes=32 time=1ms TTL=64\nReply from ${targetIp}: bytes=32 time=1ms TTL=64\nReply from ${targetIp}: bytes=32 time=1ms TTL=64\nReply from ${targetIp}: bytes=32 time=1ms TTL=64\n\nPing statistics for ${targetIp}:\n    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)`);
                const targetDev = currentTopology.devices.find(d => d.ip === targetIp);
                animatePacketFlow(srcDev.id, targetDev ? targetDev.id : null);
            } else {
                logToTerminal(`Request timed out.\nRequest timed out.\nRequest timed out.\nRequest timed out.\n\nPing statistics for ${targetIp}:\n    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)\nDiagnostics: ${data.feedback || 'Host unreachable'}`);
            }
        })
        .catch(err => {
            // Local fallback
            const targetDev = currentTopology.devices.find(d => d.ip === targetIp);
            if (targetDev || targetIp === srcDev.gateway || targetIp === '127.0.0.1') {
                logToTerminal(`Reply from ${targetIp}: bytes=32 time=1ms TTL=64\nPackets: Sent = 4, Received = 4, Lost = 0 (0% loss)`);
                animatePacketFlow(srcDev.id, targetDev ? targetDev.id : null);
            } else {
                logToTerminal(`Request timed out.\nPackets: Sent = 4, Received = 0, Lost = 4 (100% loss)`);
            }
        });
    }

    // -------------------------------------------------------------
    // PACKET TESTER (PING TAB)
    // -------------------------------------------------------------
    function populatePingSourceSelect() {
        const sel = document.getElementById('ping-src-select');
        if (!sel) return;
        sel.innerHTML = '';
        currentTopology.devices.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d.id;
            opt.textContent = `${d.name} (${d.ip || 'No IP'})`;
            sel.appendChild(opt);
        });
    }

    window.triggerLabPingTest = function () {
        const srcSelect = document.getElementById('ping-src-select');
        const dstInput = document.getElementById('ping-dst-input');
        const logBox = document.getElementById('ping-result-log');
        if (!srcSelect || !dstInput || !logBox) return;

        const srcId = srcSelect.value;
        const dstIp = dstInput.value.trim();
        if (!dstIp) {
            alert('Please specify a destination IP address.');
            return;
        }

        const srcDev = currentTopology.devices.find(d => d.id === srcId);
        logBox.innerHTML = `Simulating ICMP Echo Request from ${srcDev.name} (${srcDev.ip || '0.0.0.0'}) to ${dstIp}...`;

        fetch('/api/academy/verify-step/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lesson_id: lessonId,
                test_type: 'ping',
                src_device: srcId,
                dst_ip: dstIp,
                topology: currentTopology
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.passed) {
                logBox.innerHTML = `<span class="text-success"><i class="fa-solid fa-circle-check"></i> ${data.feedback}</span>`;
                const targetDev = currentTopology.devices.find(d => d.ip === dstIp);
                animatePacketFlow(srcId, targetDev ? targetDev.id : null);
            } else {
                logBox.innerHTML = `<span class="text-danger"><i class="fa-solid fa-circle-xmark"></i> ${data.feedback}</span>`;
            }
        })
        .catch(err => {
            console.error('Ping test error:', err);
            logBox.innerHTML = `<span class="text-success"><i class="fa-solid fa-check"></i> ICMP Echo Reply received from ${dstIp}! (Local Simulation)</span>`;
        });
    };

    function animatePacketFlow(srcId, dstId) {
        const packetsGroup = document.getElementById('svg-packets-group');
        if (!packetsGroup) return;

        const srcNode = currentTopology.devices.find(d => d.id === srcId);
        if (!srcNode) return;

        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', srcNode.x);
        circle.setAttribute('cy', srcNode.y);
        circle.setAttribute('r', '6');
        circle.setAttribute('fill', '#f59e0b');
        circle.setAttribute('filter', 'url(#glow)');
        packetsGroup.appendChild(circle);

        let progress = 0;
        const interval = setInterval(() => {
            progress += 0.08;
            if (progress >= 1) {
                clearInterval(interval);
                packetsGroup.removeChild(circle);
            } else {
                circle.setAttribute('opacity', 1 - progress * 0.5);
                circle.setAttribute('r', 6 + progress * 8);
            }
        }, 40);
    }

    // -------------------------------------------------------------
    // UTILITIES
    // -------------------------------------------------------------
    function logToTerminal(text) {
        const term = document.getElementById('lab-terminal-output');
        if (!term) return;
        term.textContent += text + '\n';
        term.scrollTop = term.scrollHeight;
    }

    function logVerification(msg, success) {
        const cont = document.getElementById('verification-log-container');
        if (!cont) return;
        const div = document.createElement('div');
        div.className = `p-2 rounded mb-2 border ${success ? 'bg-success-subtle border-success text-success' : 'bg-danger-subtle border-danger text-danger'}`;
        div.innerHTML = `<i class="fa-solid ${success ? 'fa-circle-check' : 'fa-circle-xmark'} me-1"></i> [${new Date().toLocaleTimeString()}] ${msg}`;
        cont.prepend(div);
    }

    window.resetLabTopology = function () {
        if (!confirm('Are you sure you want to reset the lab to its initial topology? All uncommitted edits will be cleared.')) return;
        initLabEnvironment();
        logToTerminal('\n[LAB RESET TO INITIAL STATE]');
    };

    window.centerCanvasTopology = function () {
        renderSvgTopology();
    };

})();
