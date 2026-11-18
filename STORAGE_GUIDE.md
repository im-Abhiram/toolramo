# Ramonet Hybrid Storage & PythonAnywhere Optimization Guide

## 1. Overview & Constraints

The PythonAnywhere hosting environment allocates approximately **512 MB** of disk quota for free-tier web applications. To ensure Ramonet remains robust, responsive, and lightweight without approaching or exceeding this boundary, Ramonet utilizes an enterprise **Hybrid Storage Architecture**.

---

## 2. Storage Tier Architecture

```
+-------------------------------------------------------------------------+
|                              CLIENT BROWSER                             |
|                                                                         |
|  [localStorage]                     [IndexedDB: RamonetStorageDB]       |
|  - Theme Preferences                - Network Topology Node Graphs      |
|  - Sidebar State                    - Device Configurations & SVIs      |
|  - Recent CLI Commands              - Cable Connections & Pinouts       |
|  - Active Inspector Tabs            - Packet Simulation Snapshots       |
|  - Snap-to-Grid Toggles             - Offline Learning Topic Progress   |
+-------------------------------------------------------------------------+
                                     | (Optional Sync / JSON Export)
                                     v
+-------------------------------------------------------------------------+
|                        PYTHONANYWHERE SERVER HOST                       |
|                                                                         |
|  [SQLite Database: db.sqlite3]      [Static Assets: staticfiles/]       |
|  - User Authentication Accounts     - Bootstrap 5.3.3 CSS/JS Bundle     |
|  - Minimal User Profiles            - FontAwesome 6 Webfonts            |
|  - Server-Sync Project Metadata     - Chart.js 4.4.7 Engine             |
|  - Minimal Audit Records            - Ramonet Dark Navy Custom Themes   |
|  - Knowledge Base Index             - Prebuilt Seed JSON Data           |
|  (Typical Size: < 500 KB)           (Total Size: ~4.5 MB)               |
+-------------------------------------------------------------------------+
```

### Tier A: Browser `localStorage`
- **Scope:** Fast, key-value storage for transient UI state.
- **Data Stored:**
  - `ramonet_theme`: Active dark navy theme identifier.
  - `ramonet_sidebar_collapsed`: Boolean sidebar state.
  - `ramonet_recent_commands`: Array of recently typed terminal commands.
  - `ramonet_grid_enabled`: Canvas grid snap toggle.
- **Footprint:** Less than **50 KB**.

### Tier B: Browser `IndexedDB` (`RamonetStorageDB`)
- **Scope:** High-capacity structured client-side database.
- **Data Stored:**
  - Object Store `projects`: Complete network topologies, node coordinates, port connections, interface IPs, and VLAN tables.
  - Object Store `snapshots`: Undo/redo history states and saved revision points.
  - Object Store `simulation_logs`: Packet traversal traces, hop timestamps, and drop diagnostics.
- **Key Storage Principle:** *Browser IndexedDB storage lives entirely on the user's local machine and does NOT consume or reduce the server's 512 MB disk quota.*

### Tier C: Server-Side SQLite (`db.sqlite3`)
- **Scope:** Relational database for authentication and core metadata.
- **Data Stored:**
  - Django User and UserProfile models.
  - Catalog definitions for 10 hardware categories and device models.
  - Command Reference library entries.
  - Troubleshooting scenario specifications.
  - Structured 20-topic learning curriculum.
- **Disk Footprint:** **~320 KB** on disk.

### Tier D: Static Data & Vendor Assets (`staticfiles/`)
- **Scope:** Locally hosted frontend frameworks and illustrations.
- **Vendor Assets:**
  - Bootstrap 5.3.3 CSS & JS bundle.
  - FontAwesome 6.5.1 CSS and WOFF2/TTF fonts.
  - Chart.js 4.4.7 UMD minified script.
- **Disk Footprint:** **~4.5 MB** total.

---

## 3. Total PythonAnywhere Storage Footprint

| Component | Storage Allocation | Actual Utilization | % of 512 MB Quota |
| :--- | :--- | :--- | :--- |
| **SQLite Database (`db.sqlite3`)** | 512 MB | ~0.32 MB | 0.06% |
| **Static Assets (`staticfiles/`)** | 512 MB | ~4.50 MB | 0.88% |
| **Media Uploads (`media/`)** | 512 MB | ~0.00 MB | 0.00% |
| **Total Disk Footprint** | **512 MB** | **~4.82 MB** | **0.94%** |

*Ramonet consumes less than 1% of the PythonAnywhere free tier storage quota!*

---

## 4. Storage Maintenance & Cleanup Tools

1. **Storage Manager UI:** Access `/storage/` to inspect real-time server database size, static asset sizes, and browser IndexedDB usage.
2. **Export Full Backup:** Click "Export Complete Backup" to download a clean JSON archive of all local projects.
3. **Purge Simulation History:** Click "Clear Packet Simulation History" to purge temporary simulation trace logs from IndexedDB without affecting active topologies.
