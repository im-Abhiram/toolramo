/**
 * Ramonet Networking Engineering Toolbox & Study Helper Suite
 * 100% offline client-side network engineering calculators, VLSM planners,
 * binary breakdowns, subnetting quiz practice, and protocol references.
 */

const RamonetCalculators = {
    // 1. IPv4 Subnet Calculator with Binary & Class Detection
    calculateSubnet(ipStr, cidr) {
        cidr = parseInt(cidr);
        if (isNaN(cidr) || cidr < 0 || cidr > 32) cidr = 24;
        
        const parts = ipStr.trim().split('.').map(p => parseInt(p, 10));
        if (parts.length !== 4 || parts.some(p => isNaN(p) || p < 0 || p > 255)) return null;

        const ipNum = ((parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]) >>> 0;
        const maskNum = cidr === 0 ? 0 : ((-1 << (32 - cidr)) >>> 0);
        const netNum = (ipNum & maskNum) >>> 0;
        const bcastNum = (netNum | (~maskNum >>> 0)) >>> 0;

        const numToIp = (num) => [
            (num >>> 24) & 255,
            (num >>> 16) & 255,
            (num >>> 8) & 255,
            num & 255
        ].join('.');

        const toBinary = (num) => {
            const b = (num >>> 0).toString(2).padStart(32, '0');
            return [b.slice(0, 8), b.slice(8, 16), b.slice(16, 24), b.slice(24, 32)].join('.');
        };

        const totalHosts = Math.pow(2, 32 - cidr);
        const usableHosts = cidr >= 31 ? (cidr === 31 ? 2 : 1) : Math.max(0, totalHosts - 2);

        const firstUsable = cidr >= 31 ? netNum : (netNum + 1) >>> 0;
        const lastUsable = cidr >= 31 ? bcastNum : (bcastNum - 1) >>> 0;

        const firstOctet = parts[0];
        let ipClass = 'Class C';
        if (firstOctet >= 1 && firstOctet <= 126) ipClass = 'Class A';
        else if (firstOctet === 127) ipClass = 'Loopback (127.0.0.0/8)';
        else if (firstOctet >= 128 && firstOctet <= 191) ipClass = 'Class B';
        else if (firstOctet >= 192 && firstOctet <= 223) ipClass = 'Class C';
        else if (firstOctet >= 224 && firstOctet <= 239) ipClass = 'Class D (Multicast)';
        else if (firstOctet >= 240 && firstOctet <= 255) ipClass = 'Class E (Research)';

        let ipScope = 'Public Routable';
        if (firstOctet === 10) ipScope = 'Private (RFC 1918: 10.0.0.0/8)';
        else if (firstOctet === 172 && parts[1] >= 16 && parts[1] <= 31) ipScope = 'Private (RFC 1918: 172.16.0.0/12)';
        else if (firstOctet === 192 && parts[1] === 168) ipScope = 'Private (RFC 1918: 192.168.0.0/16)';
        else if (firstOctet === 169 && parts[1] === 254) ipScope = 'APIPA / Link-Local (RFC 3927)';
        else if (firstOctet === 127) ipScope = 'Localhost Loopback';

        return {
            ip: ipStr,
            cidr: cidr,
            netmask: numToIp(maskNum),
            wildcard: numToIp((~maskNum) >>> 0),
            network: numToIp(netNum),
            broadcast: numToIp(bcastNum),
            firstUsable: numToIp(firstUsable),
            lastUsable: numToIp(lastUsable),
            usableHosts: usableHosts,
            totalHosts: totalHosts,
            ipClass: ipClass,
            ipScope: ipScope,
            ipBinary: toBinary(ipNum),
            maskBinary: toBinary(maskNum),
            netBinary: toBinary(netNum),
            networkBits: cidr,
            hostBits: 32 - cidr
        };
    },

    // 2. VLSM Subnet Planner
    planVLSM(baseNetwork, baseCidr, hostRequirements = []) {
        const reqs = [...hostRequirements].sort((a, b) => b.hosts - a.hosts);
        let currentIpParts = baseNetwork.split('.').map(Number);
        let currentIpNum = ((currentIpParts[0] << 24) | (currentIpParts[1] << 16) | (currentIpParts[2] << 8) | currentIpParts[3]) >>> 0;

        const numToIp = (num) => [
            (num >>> 24) & 255,
            (num >>> 16) & 255,
            (num >>> 8) & 255,
            num & 255
        ].join('.');

        const results = [];
        for (let item of reqs) {
            const neededHosts = parseInt(item.hosts, 10) || 2;
            let hostBits = Math.ceil(Math.log2(neededHosts + 2));
            hostBits = Math.max(2, hostBits);
            const prefix = 32 - hostBits;
            const blockSize = Math.pow(2, hostBits);

            const maskNum = (-1 << hostBits) >>> 0;
            const netNum = currentIpNum;
            const bcastNum = (netNum + blockSize - 1) >>> 0;

            results.push({
                name: item.name || `Subnet (${neededHosts} hosts)`,
                neededHosts: neededHosts,
                allocatedHosts: blockSize - 2,
                prefix: prefix,
                network: numToIp(netNum),
                netmask: numToIp(maskNum),
                firstUsable: numToIp((netNum + 1) >>> 0),
                lastUsable: numToIp((bcastNum - 1) >>> 0),
                broadcast: numToIp(bcastNum),
                wastedHosts: (blockSize - 2) - neededHosts
            });

            currentIpNum = (currentIpNum + blockSize) >>> 0;
        }

        return results;
    },

    // 3. Subnetting Study Quiz Generator (CCNA / Net+ Prep)
    generateQuizQuestion() {
        const prefixes = [24, 25, 26, 27, 28, 29, 30, 20, 21, 22, 23];
        const cidr = prefixes[Math.floor(Math.random() * prefixes.length)];
        const o1 = [10, 172, 192][Math.floor(Math.random() * 3)];
        const o2 = o1 === 10 ? Math.floor(Math.random() * 50) : (o1 === 172 ? 16 + Math.floor(Math.random() * 15) : 168);
        const o3 = Math.floor(Math.random() * 200);
        const o4 = Math.floor(Math.random() * 254) + 1;
        const ipStr = `${o1}.${o2}.${o3}.${o4}`;

        const details = this.calculateSubnet(ipStr, cidr);
        const qTypes = [
            { field: 'network', title: 'Network Address', answer: details.network, hint: 'Bitwise AND between IP and Subnet Mask' },
            { field: 'broadcast', title: 'Broadcast Address', answer: details.broadcast, hint: 'All host bits set to 1' },
            { field: 'firstUsable', title: 'First Usable Host IP', answer: details.firstUsable, hint: 'Network Address + 1' },
            { field: 'lastUsable', title: 'Last Usable Host IP', answer: details.lastUsable, hint: 'Broadcast Address - 1' },
            { field: 'usableHosts', title: 'Total Usable Hosts', answer: String(details.usableHosts), hint: '2^(32 - prefix) - 2' }
        ];

        const chosenQ = qTypes[Math.floor(Math.random() * qTypes.length)];

        return {
            ip: ipStr,
            cidr: cidr,
            questionText: `Given the IP host address <strong>${ipStr}/${cidr}</strong>, calculate the <strong>${chosenQ.title}</strong>:`,
            field: chosenQ.field,
            correctAnswer: chosenQ.answer,
            hint: chosenQ.hint,
            fullDetails: details
        };
    },

    // 4. PoE Power Budget Calculator
    calculatePoEBudget(switchBudgetWatts, connectedDevices = []) {
        let totalConsumed = 0;
        const breakdown = [];

        connectedDevices.forEach(d => {
            let watts = parseFloat(d.watts) || 0;
            if (d.class === '802.3af') watts = 15.4;
            else if (d.class === '802.3at') watts = 30.0;
            else if (d.class === '802.3bt') watts = 60.0;
            
            totalConsumed += watts;
            breakdown.push({ name: d.name, watts: watts, class: d.class || 'Custom' });
        });

        const remaining = switchBudgetWatts - totalConsumed;
        const percentage = switchBudgetWatts > 0 ? (totalConsumed / switchBudgetWatts) * 100 : 0;

        return {
            budget: switchBudgetWatts,
            consumed: totalConsumed.toFixed(1),
            remaining: remaining.toFixed(1),
            percentage: percentage.toFixed(1),
            isOverloaded: remaining < 0,
            breakdown: breakdown
        };
    },

    // 5. CCTV Bandwidth & Storage Calculator
    calculateCCTVStorage(cameraCount, resolution = '1080p', codec = 'H.265', fps = 25, days = 30) {
        let baseBitrate = 4.0;
        if (resolution === '720p') baseBitrate = 2.0;
        else if (resolution === '1080p') baseBitrate = 4.0;
        else if (resolution === '4MP') baseBitrate = 6.0;
        else if (resolution === '4K') baseBitrate = 12.0;

        if (codec === 'H.265' || codec === 'H.265+') baseBitrate *= 0.55;

        const totalMbps = baseBitrate * cameraCount;
        const gbPerDay = (totalMbps * 86400) / (8 * 1024);
        const totalGB = gbPerDay * days;
        const totalTB = (totalGB / 1024).toFixed(2);

        return {
            cameraCount: cameraCount,
            resolution: resolution,
            codec: codec,
            perCameraMbps: baseBitrate.toFixed(1),
            totalBandwidthMbps: totalMbps.toFixed(1),
            storageGB: Math.round(totalGB),
            storageTB: totalTB,
            days: days
        };
    },

    // 6. NAS Storage & RAID Capacity Estimator
    calculateRAIDCapacity(driveCount, driveSizeTB, raidLevel = 'RAID5') {
        const count = parseInt(driveCount) || 4;
        const size = parseFloat(driveSizeTB) || 4.0;
        const rawTotal = count * size;

        let usable = 0;
        let faultTolerance = 0;
        let efficiency = 0;
        let desc = '';

        if (raidLevel === 'RAID0') {
            usable = rawTotal;
            faultTolerance = 0;
            desc = 'Striping without parity. High speed, zero fault tolerance.';
        } else if (raidLevel === 'RAID1') {
            usable = size;
            faultTolerance = count - 1;
            desc = 'Mirroring across all drives. High redundancy, 50% capacity loss on 2 drives.';
        } else if (raidLevel === 'RAID5') {
            usable = (count - 1) * size;
            faultTolerance = 1;
            desc = 'Block-level striping with distributed parity. Can survive 1 drive failure.';
        } else if (raidLevel === 'RAID6') {
            usable = (count - 2) * size;
            faultTolerance = 2;
            desc = 'Dual distributed parity. Can survive 2 concurrent drive failures.';
        } else if (raidLevel === 'RAID10') {
            usable = (count / 2) * size;
            faultTolerance = 1;
            desc = 'Stripe of mirrors. High IOPS and fast rebuilds.';
        }

        efficiency = rawTotal > 0 ? (usable / rawTotal) * 100 : 0;

        return {
            raidLevel: raidLevel,
            driveCount: count,
            driveSizeTB: size,
            rawCapacityTB: rawTotal.toFixed(1),
            usableCapacityTB: Math.max(0, usable).toFixed(1),
            faultToleranceDrives: faultTolerance,
            storageEfficiencyPercent: efficiency.toFixed(0),
            description: desc
        };
    },

    // 7. Well-Known Ports & Protocols Reference (CCNA / Network+ Standard)
    getWellKnownPorts() {
        return [
            { port: 20, proto: 'TCP', name: 'FTP Data', layer: 'L7 Application', desc: 'File Transfer Protocol data stream' },
            { port: 21, proto: 'TCP', name: 'FTP Control', layer: 'L7 Application', desc: 'File Transfer Protocol command & authentication' },
            { port: 22, proto: 'TCP', name: 'SSH / SFTP', layer: 'L7 Application', desc: 'Secure Shell encrypted CLI administration' },
            { port: 23, proto: 'TCP', name: 'Telnet', layer: 'L7 Application', desc: 'Unencrypted plaintext remote terminal' },
            { port: 25, proto: 'TCP', name: 'SMTP', layer: 'L7 Application', desc: 'Simple Mail Transfer Protocol (email relay)' },
            { port: 53, proto: 'TCP/UDP', name: 'DNS', layer: 'L7 Application', desc: 'Domain Name System name resolution' },
            { port: 67, proto: 'UDP', name: 'DHCP Server', layer: 'L7 Application', desc: 'Dynamic Host Configuration Protocol server broadcast listener' },
            { port: 68, proto: 'UDP', name: 'DHCP Client', layer: 'L7 Application', desc: 'DHCP Client unicast/broadcast recipient' },
            { port: 69, proto: 'UDP', name: 'TFTP', layer: 'L7 Application', desc: 'Trivial FTP for Cisco IOS image/config backups' },
            { port: 80, proto: 'TCP', name: 'HTTP', layer: 'L7 Application', desc: 'Hypertext Transfer Protocol unencrypted web' },
            { port: 88, proto: 'TCP/UDP', name: 'Kerberos', layer: 'L7 Application', desc: 'Active Directory domain authentication' },
            { port: 110, proto: 'TCP', name: 'POP3', layer: 'L7 Application', desc: 'Post Office Protocol v3 email retrieval' },
            { port: 123, proto: 'UDP', name: 'NTP', layer: 'L7 Application', desc: 'Network Time Protocol clock synchronization' },
            { port: 143, proto: 'TCP', name: 'IMAP', layer: 'L7 Application', desc: 'Internet Message Access Protocol email sync' },
            { port: 161, proto: 'UDP', name: 'SNMP', layer: 'L7 Application', desc: 'Simple Network Management Protocol polling queries' },
            { port: 162, proto: 'UDP', name: 'SNMP Trap', layer: 'L7 Application', desc: 'SNMP asynchronous event notifications' },
            { port: 179, proto: 'TCP', name: 'BGP', layer: 'L7 Application', desc: 'Border Gateway Protocol inter-domain routing' },
            { port: 389, proto: 'TCP/UDP', name: 'LDAP', layer: 'L7 Application', desc: 'Lightweight Directory Access Protocol' },
            { port: 443, proto: 'TCP', name: 'HTTPS', layer: 'L7 Application', desc: 'HTTP over TLS/SSL encrypted web' },
            { port: 445, proto: 'TCP', name: 'SMB', layer: 'L7 Application', desc: 'Server Message Block Windows file sharing' },
            { port: 514, proto: 'UDP', name: 'Syslog', layer: 'L7 Application', desc: 'System event log notifications' },
            { port: 587, proto: 'TCP', name: 'SMTP Submission', layer: 'L7 Application', desc: 'Authenticated email client submission' },
            { port: 636, proto: 'TCP', name: 'LDAPS', layer: 'L7 Application', desc: 'Secure LDAP over TLS' },
            { port: 993, proto: 'TCP', name: 'IMAPS', layer: 'L7 Application', desc: 'Secure IMAP over TLS' },
            { port: 995, proto: 'TCP', name: 'POP3S', layer: 'L7 Application', desc: 'Secure POP3 over TLS' },
            { port: 3389, proto: 'TCP', name: 'RDP', layer: 'L7 Application', desc: 'Microsoft Remote Desktop Protocol' },
            { port: 5060, proto: 'TCP/UDP', name: 'SIP', layer: 'L7 Application', desc: 'Session Initiation Protocol for VoIP Telephony' }
        ];
    }
};

window.RamonetCalculators = RamonetCalculators;
