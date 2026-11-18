# Ramonet — Advanced Web-Based Network Simulator & Infrastructure Management Learning Platform

![Ramonet Banner](https://raw.githubusercontent.com/ramonet/assets/main/banner.png)

**Ramonet** is a professional, browser-based network simulation engine and enterprise networking knowledge platform. It combines Cisco Packet Tracer-style visual network topology design, GNS3-inspired infrastructure virtualization, a real-time multi-platform CLI terminal, and an interactive Network Configuration Assistant into a unified web application.

---

## 🎓 RamoNet Academy — Interactive Practical Networking Training

RamoNet Academy is a fully integrated teaching and practical certification module embedded within RamoNet:

- **Dedicated Academy Dashboard (`/academy/`):** Real-time KPIs tracking total courses, active lessons, completed modules, simulation labs finished, average quiz score, study streaks, and XP points.
- **Three Progressive Learning Tiers:** Beginner, Intermediate, and Advanced curricula.
- **14 Comprehensive Core Courses:**
  1. Introduction to Computer Networking
  2. Ethernet, Cabling & Network Devices
  3. Switch Configuration & VLAN Administration
  4. Router Configuration & IP Subnetting
  5. Routing Protocols (Static & Dynamic)
  6. Network Security & Firewall Administration
  7. Wireless Networking & Access Points
  8. Network Attached Storage (NAS) & SAN
  9. Network Printers & Print Server Configuration
  10. CCTV & Surveillance Networking (IP Cameras & NVR)
  11. Server Networking (Windows & Linux Infrastructure)
  12. Enterprise Network Design & High Availability
  13. Network Troubleshooting & Diagnostics Lab
  14. Practical Network Administration & Hands-on Exam
- **27 Device-Specific In-Depth Guides (`/academy/devices/`):** Full engineering guides for 27 enterprise hardware devices covering all 17 standard sections: purpose, applications, appearance, interfaces, cables, PoE, IP config, commands, verification, common mistakes, and capstone projects.
- **Standard 8-Section Lesson Structure:** Section A (Intro), B (How It Works), C (Device Connection), D (Configuration), E (Command Training), F (Practical Lab), G (Troubleshooting), H (Assessment Quiz).
- **Integrated 4-Pane Practical Lab:**
  - *Left Pane:* Objectives, step checklist, 4 learning mode switches, 3-tier progressive hints, mistake detection banner.
  - *Center Pane:* Interactive SVG network canvas with device selection and animated packet pulses.
  - *Right Pane:* Live device inspector, IP configuration, and port status.
  - *Bottom Pane:* Tabbed console featuring an interactive CLI terminal, packet tester (ping), and verification audit log.
- **Four Distinct Learning Modes:**
  - `Mode 1: Show Me`: Automated demonstration executing CLI commands and illustrating concepts.
  - `Mode 2: Guided Practice`: Step-by-step guidance with instant validation and parameter checking.
  - `Mode 3: Independent Practice`: Self-directed configuration against high-level specifications.
  - `Mode 4: Challenge / Exam`: Timed capstone exams scored out of 100 with detailed multi-point rubrics.
- **Progressive Hint Engine (Tiers 1, 2, 3):** Concept hints, target component hints, and exact CLI syntax.
- **Mistake Detection System:** Identifies subnet mask mismatches, duplicate IP conflicts, unroutable gateways, and down interfaces.
- **Printable Completion Certificates (`/academy/course/<slug>/certificate/`):** Professional digital certificates with unique credential IDs and official verification badges.

---

## 🌟 Key Capabilities & Modules

### 1. Interactive Network Topology Designer
- **Cisco Packet Tracer / GNS3 hybrid workspace:** Full SVG & Canvas canvas with pan, zoom, snap-to-grid, minimap, undo/redo, and drag-and-drop palette.
- **Port-to-Port Cabling:** Copper Straight-Through (Cat6), Crossover, Single/Multimode Fiber Optic, Serial WAN, 802.11 Wireless, and Console cables.
- **Port Status & Badges:** Real-time link states (Up, Down, Administratively Disabled), interface speed, and PoE negotiation markers.
- **Real-Time Autosave:** Debounced autosave directly into browser **IndexedDB** (`RamonetStorageDB`).

### 2. Advanced Network Configuration Assistant
- **15-Section Device Learning Guides:** Complete hardware, cabling, protocol, troubleshooting, and security breakdowns for all 10 device categories.
- **Interactive Configuration Wizards:** Multi-step guided wizards with CLI previews that directly mutate underlying simulated devices.
- **Two-Device "How to Connect" Analyzer:** Evaluates interface compatibility, recommended cabling, pinouts, power/PoE requirements, and step-by-step connection instructions between any two devices.
- **Internal Natural Language Knowledge Search:** Curated question-and-answer search answering common operational queries without external paid AI APIs.

### 3. Multi-Platform Interactive CLI Terminal
- **Cisco IOS Engine:** Realistic mode hierarchy (`Router>`, `Router#`, `Router(config)#`, `Router(config-if)#`, `Router(config-vlan)#`), tab autocomplete, `?` context-sensitive help, command history, and real state mutations (`ip address`, `no shutdown`, `show ip interface brief`, `show ip route`).
- **Linux Shell:** `ip addr`, `ip route`, `iptables`, `ping`, `traceroute`.
- **Windows Command Prompt:** `ipconfig /all`, `route print`, `ping`, `tracert`.
- **MikroTik RouterOS:** `/ip address print`, `/ip route print`.

### 4. Modular Python Network Simulation Engine
- **Layer 2:** Ethernet frame forwarding, MAC learning tables, CAM table aging, ARP cache resolution, 802.1Q VLAN tagging (Access, Trunk, Native VLANs).
- **Layer 3:** IPv4 address validation, CIDR/Netmask calculations, Longest Prefix Match (LPM) routing tables, default routes, TTL decrement, NAT/PAT translation.
- **Layer 4 & 7:** Stateful firewall filtering, connection tracking (`conntrack`), ICMP Echo Request/Reply (ping), TCP 3-way handshake simulation, DNS resolution, DHCP DORA allocation, RTSP video streams, and SMB file shares.
- **Drop Diagnostics:** Pinpoints exact failure reasons (`GATEWAY_MISSING`, `NO_ROUTE_TO_HOST`, `FIREWALL_DENY`, `CABLE_DISCONNECTED`, `VLAN_ISOLATION`).

### 5. Specialized Device Configuration Managers
- **Switch Manager:** VLAN database, Access vs Trunk port configuration, MAC table inspector, RSTP bridge status, Port Security policies.
- **Router Manager:** Routing table viewer, Static route installer, NAT overload pool monitor, Extended ACLs.
- **Firewall Manager:** LAN/WAN/DMZ zone isolation, Ordered stateful packet filter rules, Netfilter connection tracking table, Port forwarding (DNAT).
- **Wireless Manager:** Dual-band radios (2.4 GHz & 5 GHz), Channel selection, WPA2/WPA3 security, SSID-to-VLAN mapping, Connected client RSSI table.
- **Server Manager:** BIND9 DNS records, DHCP scope IP pools, Nginx web services, SMB Samba shares, Service daemons start/stop.
- **NAS & Storage Manager:** RAID 0, 1, 5, 6, 10 capacity estimator, SMB/NFS file share permissions, LACP link aggregation.
- **CCTV & NVR Manager:** 16-channel NVR registrations, ONVIF discovery, RTSP stream endpoints, PoE power budget meter, CCTV bandwidth & storage retention calculator.
- **IP Address Manager (IPAM):** Enterprise subnet hierarchy, usable IP ranges, and utilization tracking.

### 6. 20-in-1 Network Engineering Toolbox
1. IPv4 Subnet Calculator
2. IPv6 Address Calculator
3. CIDR to Netmask Calculator
4. IP Range Calculator
5. Usable Host Calculator
6. Network & Broadcast Address Calculator
7. VLSM Subnet Planner
8. MAC Address Reference Tool
9. Ports & Protocols Reference (Well-known IANA table)
10. TCP/UDP Port Lookup
11. DNS Record Reference
12. DHCP Configuration Planner
13. VLAN Planner
14. Routing Table Viewer
15. NAT & PAT Calculator
16. Bandwidth Calculator
17. PoE Power Budget Calculator
18. CCTV Bandwidth & Storage Estimator
19. NAS Storage & RAID Capacity Estimator
20. TIA/EIA-568-A vs TIA/EIA-568-B RJ45 Cable Pinout Reference

### 7. Network Troubleshooting Lab
- 15+ hands-on incident fault scenarios across **Beginner**, **Intermediate**, and **Advanced** tiers.
- Automated solution verification engine tests whether student fixes restore end-to-end connectivity.
- Explains root cause analysis upon resolution.

### 8. 20-Topic Learning Center & 18 Prebuilt Templates
- Structured curriculum covering OSI, TCP/IP, Ethernet, Subnetting, Switching, VLANs, Routing, OSPF, Firewalls, NAT, DNS, DHCP, Wireless, Security, NAS, CCTV, and Troubleshooting.
- 18 production starter templates ready to load into the designer in 1 click.

---

## 🛠 Technology Stack

- **Backend:** Python 3.10+ / Django 5+ / Django REST Framework
- **Database:** SQLite (optimized for PythonAnywhere 512 MB disk quota)
- **Frontend:** Vanilla JavaScript (ES6+), HTML5, CSS3, Bootstrap 5.3.3, Font Awesome 6.5.1, Chart.js 4.4.7
- **Storage:** Hybrid Architecture (localStorage for preferences, IndexedDB for topologies/simulations, SQLite for auth/metadata)
- **Zero Runtime CDNs:** 100% of static vendor libraries are locally hosted in `static/vendor/`.

---

## 🚀 Quickstart (Local Development)

```bash
# 1. Clone repository
git clone https://github.com/ramonet/ramonet.git
cd ramonet

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Seed complete device definitions, commands, learning topics & templates
python manage.py seed_data

# 5. Run automated test suite
python manage.py test

# 6. Start development server
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

- **Admin Login:** `admin` / `admin123`
- **Student Login:** `student` / `student123`

---

## 📁 Repository & Architecture Structure

```
d:\ramonet\
├── manage.py
├── requirements.txt
├── wsgi_pythonanywhere.py
├── README.md
├── DEPLOYMENT.md
├── STORAGE_GUIDE.md
├── db.sqlite3
├── ramonet/                     # Project Configuration
│   ├── settings.py
│   ├── urls.py
│   ├── api_urls.py
│   ├── views.py
│   └── wsgi.py
├── static/                      # Locally Hosted Static Assets
│   ├── css/
│   │   ├── ramonet-theme.css    # Enterprise Dark Navy Palette (#0B1120)
│   │   ├── topology.css         # Canvas, SVG Cables & Node Badges
│   │   └── terminal.css         # Interactive CLI Monospace Terminal
│   ├── js/
│   │   ├── app.js               # Main App Controller
│   │   ├── topology/            # Canvas, Panning, Zoom & Connections
│   │   ├── simulation/          # Packet Tracer & Flow Visualizer
│   │   ├── cli/                 # Terminal Emulator & Autocomplete
│   │   ├── assistant/           # 15-Section Guides & Wizards
│   │   ├── tools/               # 20-in-1 Networking Calculators
│   │   └── storage/             # IndexedDB & LocalStorage Subsystems
│   └── vendor/                  # Offline Bootstrap, FontAwesome & ChartJS
├── templates/                   # Clean Django HTML5 Templates
│   ├── base.html
│   ├── dashboard.html
│   ├── topology/
│   ├── devices/
│   ├── configuration/
│   ├── commands/
│   ├── simulation/
│   ├── networktools/
│   ├── monitoring/
│   ├── troubleshooting/
│   ├── learning/
│   ├── projects/
│   ├── audit/
│   └── accounts/
├── simulation/                  # Modular Python Simulation Engine
│   ├── engine.py                # L2-L7 Forwarding, ARP, Route & Firewall Logic
│   └── tests.py                 # Multi-Hop E2E Ping & Drop Tests
├── commands/                    # CLI Simulator Engine
│   ├── cli_engine.py            # Cisco IOS / Linux / Windows Shell Session
│   └── tests.py
├── devices/                     # Complete Hardware Specifications
├── knowledgebase/               # Guides & "How to Connect" Matrix
├── troubleshooting/             # Incident Scenarios & Solution Verifier
├── learning/                    # 20-Topic Structured Curriculum
└── audit/                       # PythonAnywhere Storage Quota Inspector
```

---

## 🔒 Security & Safe Execution
- **Strictly Sandboxed:** Never executes arbitrary shell commands on the host operating system.
- **Client-Side Simulation:** Simulated commands modify the virtual in-memory network graph, safely isolated from the hosting environment.
- **Input Sanitized:** Comprehensive validation on all imported JSON project designs.

---

## 📄 License
Licensed under the Apache 2.0 License.
