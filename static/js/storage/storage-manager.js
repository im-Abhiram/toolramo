/**
 * Ramonet Storage Manager Subsystem
 * Monitors browser IndexedDB storage and PythonAnywhere SQLite disk footprints.
 */

class StorageManagerUI {
    constructor() {
        this.init();
    }

    async init() {
        await this.refreshStorageStats();
        this.bindEvents();
    }

    async refreshStorageStats() {
        // Browser IndexedDB stats
        const browserStats = await window.ramonetStorage.getStorageStats();
        
        const countEl = document.getElementById('stat-local-projects-count');
        const usageEl = document.getElementById('stat-browser-usage');
        const barEl = document.getElementById('storage-usage-progress-bar');

        if (countEl) countEl.textContent = browserStats.projectCount;
        if (usageEl) usageEl.textContent = `${browserStats.usageMB} MB / ${browserStats.quotaMB} MB (${browserStats.usagePercent}%)`;
        if (barEl) {
            barEl.style.width = `${Math.min(100, Math.max(1, browserStats.usagePercent))}%`;
            barEl.setAttribute('aria-valuenow', browserStats.usagePercent);
        }

        // Fetch Server-side SQLite DB and Static asset size
        try {
            const resp = await fetch('/api/audit/storage-stats/');
            if (resp.ok) {
                const srv = await resp.json();
                const dbSizeEl = document.getElementById('stat-sqlite-size');
                const staticSizeEl = document.getElementById('stat-static-size');
                if (dbSizeEl) dbSizeEl.textContent = `${srv.db_size_kb} KB`;
                if (staticSizeEl) staticSizeEl.textContent = `${srv.static_size_mb} MB`;
            }
        } catch (e) {
            console.warn('Server storage stats fetch failed:', e);
        }
    }

    bindEvents() {
        // Backup all IndexedDB projects
        document.getElementById('btn-export-all-backup')?.addEventListener('click', async () => {
            const projects = await window.ramonetStorage.getAllProjects();
            const payload = {
                archive_type: 'ramonet-full-backup',
                exported_at: new Date().toISOString(),
                project_count: projects.length,
                projects: projects
            };
            const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ramonet_backup_${new Date().toISOString().slice(0, 10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
            window.ramonetUI?.showToast('Backup Created', `Exported ${projects.length} network projects.`, 'success');
        });

        // Clear local simulation history
        document.getElementById('btn-clear-sim-logs')?.addEventListener('click', async () => {
            if (confirm('Are you sure you want to clear temporary packet simulation history? Network designs will not be affected.')) {
                await window.ramonetStorage.readyPromise;
                const tx = window.ramonetStorage.db.transaction('simulation_logs', 'readwrite');
                tx.objectStore('simulation_logs').clear();
                tx.oncomplete = () => {
                    window.ramonetUI?.showToast('History Cleared', 'Local packet simulation logs cleared.', 'info');
                    this.refreshStorageStats();
                };
            }
        });

        // Clear all projects
        document.getElementById('btn-clear-all-projects')?.addEventListener('click', async () => {
            if (confirm('CAUTION: This will delete ALL locally stored projects from IndexedDB. Proceed?')) {
                await window.ramonetStorage.clearAllLocalProjects();
                window.ramonetUI?.showToast('Storage Reset', 'All local projects have been erased.', 'warning');
                this.refreshStorageStats();
            }
        });
    }
}

window.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('storage-manager-screen')) {
        window.storageManagerUI = new StorageManagerUI();
    }
});
