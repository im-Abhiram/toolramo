/**
 * Ramonet 20-in-1 Networking Tools & Calculators Suite
 * 100% offline client-side network engineering calculations.
 */

const RamonetCalculators = {
    // 1. IPv4 Subnet Calculator
    calculateSubnet(ipStr, cidr) {
        cidr = parseInt(cidr) || 24;
        const parts = ipStr.split('.').map(p => parseInt(p) || 0);
        if (parts.length !== 4) return null;

        const ipNum = (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3];
        const maskNum = cidr === 0 ? 0 : (-1 << (32 - cidr)) >>> 0;
        const netNum = (ipNum & maskNum) >>> 0;
        const bcastNum = (netNum | (~maskNum >>> 0)) >>> 0;

        const numToIp = (num) => [
            (num >>> 24) & 255,
            (num >>> 16) & 255,
            (num >>> 8) & 255,
            num & 255
        ].join('.');

        const totalHosts = Math.pow(2, 32 - cidr);
        const usableHosts = cidr >= 31 ? (cidr === 31 ? 2 : 1) : Math.max(0, totalHosts - 2);

        const firstUsable = cidr >= 31 ? netNum : netNum + 1;
        const lastUsable = cidr >= 31 ? bcastNum : bcastNum - 1;

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
            totalHosts: totalHosts
        };
    },

    // 2. VLSM Subnet Planner
    planVLSM(baseNetwork, baseCidr, hostRequirements = []) {
        // Sort descending
        const reqs = [...hostRequirements].sort((a, b) => b.hosts - a.hosts);
        let currentIpParts = baseNetwork.split('.').map(Number);
        let currentIpNum = (currentIpParts[0] << 24) | (currentIpParts[1] << 16) | (currentIpParts[2] << 8) | currentIpParts[3];

        const numToIp = (num) => [
            (num >>> 24) & 255,
            (num >>> 16) & 255,
            (num >>> 8) & 255,
            num & 255
        ].join('.');

        const results = [];
        for (let item of reqs) {
            const neededHosts = item.hosts;
            // Find power of 2
            let hostBits = Math.ceil(Math.log2(neededHosts + 2));
            hostBits = Math.max(2, hostBits);
            const prefix = 32 - hostBits;
            const blockSize = Math.pow(2, hostBits);

            const maskNum = (-1 << hostBits) >>> 0;
            const netNum = currentIpNum;
            const bcastNum = netNum + blockSize - 1;

            results.push({
                name: item.name || `Subnet ${neededHosts} hosts`,
                neededHosts: neededHosts,
                allocatedHosts: blockSize - 2,
                prefix: prefix,
                network: numToIp(netNum),
                netmask: numToIp(maskNum),
                firstUsable: numToIp(netNum + 1),
                lastUsable: numToIp(bcastNum - 1),
                broadcast: numToIp(bcastNum)
            });

            currentIpNum += blockSize;
        }

        return results;
    },

    // 3. PoE Power Budget Calculator
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

    // 4. CCTV Bandwidth & Storage Calculator
    calculateCCTVStorage(cameraCount, resolution = '1080p', codec = 'H.265', fps = 25, days = 30) {
        // Bitrate in Mbps per camera
        let baseBitrate = 4.0;
        if (resolution === '720p') baseBitrate = 2.0;
        else if (resolution === '1080p') baseBitrate = 4.0;
        else if (resolution === '4MP') baseBitrate = 6.0;
        else if (resolution === '4K') baseBitrate = 12.0;

        if (codec === 'H.265' || codec === 'H.265+') baseBitrate *= 0.55;

        const totalMbps = baseBitrate * cameraCount;
        // Gigabytes per day = Mbps * 3600 * 24 / 8 / 1000
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

    // 5. NAS Storage & RAID Capacity Estimator
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

    // 6. Well-Known Ports & Protocols Reference
    getWellKnownPorts() {
        return [
            { port: 20, proto: 'TCP', name: 'FTP-Data', desc: 'File Transfer Protocol data transfer' },
            { port: 21, proto: 'TCP', name: 'FTP-Control', desc: 'File Transfer Protocol command control' },
            { port: 22, proto: 'TCP', name: 'SSH', desc: 'Secure Shell remote administration' },
            { port: 23, proto: 'TCP', name: 'Telnet', desc: 'Unencrypted remote terminal protocol' },
            { port: 25, proto: 'TCP', name: 'SMTP', desc: 'Simple Mail Transfer Protocol' },
            { port: 53, proto: 'TCP/UDP', name: 'DNS', desc: 'Domain Name System name resolution' },
            { port: 67, proto: 'UDP', name: 'DHCP Server', desc: 'Bootstrap / DHCP Server listener' },
            { port: 68, proto: 'UDP', name: 'DHCP Client', desc: 'Bootstrap / DHCP Client listener' },
            { port: 80, proto: 'TCP', name: 'HTTP', desc: 'HyperText Transfer Protocol (Web)' },
            { port: 110, proto: 'TCP', name: 'POP3', desc: 'Post Office Protocol email retrieval' },
            { port: 123, proto: 'UDP', name: 'NTP', desc: 'Network Time Protocol clock synchronization' },
            { port: 143, proto: 'TCP', name: 'IMAP', desc: 'Internet Message Access Protocol' },
            { port: 161, proto: 'UDP', name: 'SNMP', desc: 'Simple Network Management Protocol queries' },
            { port: 443, proto: 'TCP', name: 'HTTPS', desc: 'HTTP over TLS/SSL secure web' },
            { port: 445, proto: 'TCP', name: 'SMB', desc: 'Server Message Block Windows file sharing' },
            { port: 514, proto: 'UDP', name: 'Syslog', desc: 'System log messaging protocol' },
            { port: 554, proto: 'TCP/UDP', name: 'RTSP', desc: 'Real Time Streaming Protocol for CCTV cameras' },
            { port: 631, proto: 'TCP', name: 'IPP', desc: 'Internet Printing Protocol' },
            { port: 9100, proto: 'TCP', name: 'RAW / JetDirect', desc: 'Standard network printer direct port' },
            { port: 3389, proto: 'TCP', name: 'RDP', desc: 'Remote Desktop Protocol' },
            { port: 3702, proto: 'UDP', name: 'ONVIF WS-Discovery', desc: 'IP Camera discovery broadcast' },
        ];
    }
};

window.RamonetCalculators = RamonetCalculators;
