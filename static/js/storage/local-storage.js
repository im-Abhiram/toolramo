/**
 * Ramonet Local Storage Preferences Subsystem
 * Manages lightweight client state (theme, sidebar, active tabs, recent commands).
 */

const RamonetPreferences = {
    KEYS: {
        THEME: 'ramonet_theme',
        SIDEBAR: 'ramonet_sidebar_collapsed',
        RECENT_COMMANDS: 'ramonet_recent_commands',
        ACTIVE_DEVICE_TAB: 'ramonet_device_tab',
        GRID_ENABLED: 'ramonet_grid_enabled',
        LAST_PROJECT_ID: 'ramonet_last_project_id'
    },

    get(key, defaultValue = null) {
        try {
            const val = localStorage.getItem(key);
            if (val === null) return defaultValue;
            return JSON.parse(val);
        } catch (e) {
            return localStorage.getItem(key) || defaultValue;
        }
    },

    set(key, value) {
        try {
            const serialized = typeof value === 'string' ? value : JSON.stringify(value);
            localStorage.setItem(key, serialized);
        } catch (e) {
            console.warn('LocalStorage write failed:', e);
        }
    },

    remove(key) {
        localStorage.removeItem(key);
    },

    addRecentCommand(cmd) {
        if (!cmd || !cmd.trim()) return;
        let recents = this.get(this.KEYS.RECENT_COMMANDS, []);
        if (!Array.isArray(recents)) recents = [];
        recents = [cmd.trim(), ...recents.filter(c => c !== cmd.trim())].slice(0, 30);
        this.set(this.KEYS.RECENT_COMMANDS, recents);
    },

    getRecentCommands() {
        return this.get(this.KEYS.RECENT_COMMANDS, []);
    }
};

window.RamonetPrefs = RamonetPreferences;
