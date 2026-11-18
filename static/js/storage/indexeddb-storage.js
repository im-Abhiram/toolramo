/**
 * Ramonet IndexedDB Storage Subsystem
 * High-performance, offline-first client storage for network projects,
 * device configurations, connection topologies, and simulation history.
 */

class RamonetDB {
    constructor() {
        this.dbName = 'RamonetStorageDB';
        this.version = 1;
        this.db = null;
        this.isReady = false;
        this.readyPromise = this.init();
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                // Object Store 1: Network Projects
                if (!db.objectStoreNames.contains('projects')) {
                    const projectStore = db.createObjectStore('projects', { keyPath: 'id' });
                    projectStore.createIndex('updated_at', 'updated_at', { unique: false });
                    projectStore.createIndex('name', 'name', { unique: false });
                }

                // Object Store 2: Snapshots & Versions
                if (!db.objectStoreNames.contains('snapshots')) {
                    const snapStore = db.createObjectStore('snapshots', { keyPath: 'id', autoIncrement: true });
                    snapStore.createIndex('project_id', 'project_id', { unique: false });
                }

                // Object Store 3: Simulation Logs
                if (!db.objectStoreNames.contains('simulation_logs')) {
                    const simStore = db.createObjectStore('simulation_logs', { keyPath: 'id', autoIncrement: true });
                    simStore.createIndex('project_id', 'project_id', { unique: false });
                }

                // Object Store 4: Offline Learning Progress
                if (!db.objectStoreNames.contains('learning_progress')) {
                    db.createObjectStore('learning_progress', { keyPath: 'topic_id' });
                }
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                this.isReady = true;
                resolve(this.db);
            };

            request.onerror = (event) => {
                console.error('Ramonet IndexedDB error:', event.target.error);
                reject(event.target.error);
            };
        });
    }

    async getProject(projectId) {
        await this.readyPromise;
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('projects', 'readonly');
            const store = tx.objectStore('projects');
            const req = store.get(projectId);
            req.onsuccess = () => resolve(req.result || null);
            req.onerror = () => reject(req.error);
        });
    }

    async getAllProjects() {
        await this.readyPromise;
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('projects', 'readonly');
            const store = tx.objectStore('projects');
            const req = store.getAll();
            req.onsuccess = () => resolve(req.result || []);
            req.onerror = () => reject(req.error);
        });
    }

    async saveProject(projectData) {
        await this.readyPromise;
        projectData.updated_at = new Date().toISOString();
        if (!projectData.created_at) {
            projectData.created_at = projectData.updated_at;
        }
        
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('projects', 'readwrite');
            const store = tx.objectStore('projects');
            const req = store.put(projectData);
            req.onsuccess = () => resolve(projectData);
            req.onerror = () => reject(req.error);
        });
    }

    async deleteProject(projectId) {
        await this.readyPromise;
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction('projects', 'readwrite');
            const store = tx.objectStore('projects');
            const req = store.delete(projectId);
            req.onsuccess = () => resolve(true);
            req.onerror = () => reject(req.error);
        });
    }

    async clearAllLocalProjects() {
        await this.readyPromise;
        return new Promise((resolve, reject) => {
            const tx = this.db.transaction(['projects', 'snapshots', 'simulation_logs'], 'readwrite');
            tx.objectStore('projects').clear();
            tx.objectStore('snapshots').clear();
            tx.objectStore('simulation_logs').clear();
            tx.oncomplete = () => resolve(true);
            tx.onerror = () => reject(tx.error);
        });
    }

    // Debounced autosave helper
    createDebouncedSaver(saveCallback, delayMs = 600) {
        let timer = null;
        return (data) => {
            this.setSaveStatusIndicator('saving');
            clearTimeout(timer);
            timer = setTimeout(async () => {
                try {
                    await saveCallback(data);
                    this.setSaveStatusIndicator('saved');
                } catch (e) {
                    console.error('Autosave failed:', e);
                    this.setSaveStatusIndicator('error');
                }
            }, delayMs);
        };
    }

    setSaveStatusIndicator(status) {
        const el = document.getElementById('save-status-indicator');
        if (!el) return;
        
        if (status === 'saving') {
            el.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-info me-1"></i> Saving...';
            el.className = 'storage-pill text-info';
        } else if (status === 'saved') {
            el.innerHTML = '<i class="fa-solid fa-check text-success me-1"></i> Saved locally';
            el.className = 'storage-pill text-success';
        } else if (status === 'error') {
            el.innerHTML = '<i class="fa-solid fa-triangle-exclamation text-danger me-1"></i> Save error';
            el.className = 'storage-pill text-danger';
        }
    }

    // Export Project to JSON string
    exportProjectJSON(projectData) {
        const payload = {
            format: 'ramonet-project',
            version: '2.0.0',
            exported_at: new Date().toISOString(),
            project: projectData
        };
        return JSON.stringify(payload, null, 2);
    }

    // Import Project JSON with validation
    validateAndImportProjectJSON(jsonString) {
        try {
            const data = JSON.parse(jsonString);
            if (!data || typeof data !== 'object') {
                return { valid: false, error: 'Invalid JSON structure' };
            }

            const proj = data.project || data;
            if (!proj.name || typeof proj.name !== 'string') {
                return { valid: false, error: 'Missing required field: project name' };
            }

            if (!Array.isArray(proj.devices)) {
                return { valid: false, error: 'Project must contain a valid devices array' };
            }

            if (!Array.isArray(proj.connections)) {
                return { valid: false, error: 'Project must contain a valid connections array' };
            }

            // Generate clean ID if missing or colliding
            if (!proj.id) {
                proj.id = 'proj_' + Date.now();
            }

            return { valid: true, project: proj };
        } catch (e) {
            return { valid: false, error: 'Malformed JSON syntax: ' + e.message };
        }
    }

    // Browser Storage Quota Inspector
    async getStorageStats() {
        let stats = {
            quotaBytes: 0,
            usageBytes: 0,
            quotaMB: 0,
            usageMB: 0,
            usagePercent: 0,
            projectCount: 0
        };

        if (navigator.storage && navigator.storage.estimate) {
            try {
                const estimate = await navigator.storage.estimate();
                stats.quotaBytes = estimate.quota || 0;
                stats.usageBytes = estimate.usage || 0;
                stats.quotaMB = Math.round(stats.quotaBytes / (1024 * 1024));
                stats.usageMB = (stats.usageBytes / (1024 * 1024)).toFixed(2);
                stats.usagePercent = stats.quotaBytes > 0 ? ((stats.usageBytes / stats.quotaBytes) * 100).toFixed(1) : 0;
            } catch (e) {
                console.warn('Storage estimate failed:', e);
            }
        }

        try {
            const projects = await this.getAllProjects();
            stats.projectCount = projects.length;
        } catch (e) {}

        return stats;
    }
}

// Global instance
window.ramonetStorage = new RamonetDB();
