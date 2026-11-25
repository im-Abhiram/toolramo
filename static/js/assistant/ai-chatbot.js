/**
 * RAMONET AI Copilot Client Controller
 * Powers the global floating Gemini AI chatbot across all RAMONET pages.
 * Strictly relies on server-side Gemini proxy (/api/knowledgebase/chat/) so API keys
 * never reach browser code, with XSS-safe markdown formatting and session continuity.
 */

class RamonetAIChatbot {
    constructor() {
        this.endpoint = '/api/knowledgebase/chat/';
        this.storageKey = 'ramonet_ai_chat_history_v1';
        this.maxStoredTurns = 16;
        this.history = [];
        this.isOpen = false;
        this.isExpanded = false;
        this.isSending = false;

        this.panel = document.getElementById('ramonet-ai-panel');
        this.fab = document.getElementById('ramonet-ai-fab');
        this.headerBtn = document.getElementById('btn-header-ai-chat');
        this.messagesEl = document.getElementById('ai-chat-messages');
        this.formEl = document.getElementById('ai-chat-form');
        this.inputEl = document.getElementById('ai-chat-input');
        this.sendBtn = document.getElementById('ai-chat-send-btn');
        this.closeBtn = document.getElementById('ai-btn-close');
        this.clearBtn = document.getElementById('ai-btn-clear');
        this.expandBtn = document.getElementById('ai-btn-expand');
        this.quickPromptsEl = document.getElementById('ai-quick-prompts');
        this.subtitleEl = document.getElementById('ai-context-subtitle');

        if (!this.panel || !this.messagesEl || !this.formEl || !this.inputEl) {
            return;
        }

        this.loadHistory();
        this.bindEvents();
        this.renderMessages();
        this.updateContextSubtitle();
    }

    bindEvents() {
        this.fab?.addEventListener('click', () => this.toggle());
        this.headerBtn?.addEventListener('click', () => this.toggle());
        this.closeBtn?.addEventListener('click', () => this.close());
        this.clearBtn?.addEventListener('click', () => this.clearHistory());
        this.expandBtn?.addEventListener('click', () => this.toggleExpand());

        this.formEl.addEventListener('submit', (e) => {
            e.preventDefault();
            const text = this.inputEl.value.trim();
            if (text) {
                this.sendMessage(text);
            }
        });

        this.inputEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const text = this.inputEl.value.trim();
                if (text) {
                    this.sendMessage(text);
                }
            }
        });

        this.inputEl.addEventListener('input', () => {
            this.autoResizeInput();
        });

        this.quickPromptsEl?.querySelectorAll('.ai-prompt-chip').forEach((btn) => {
            btn.addEventListener('click', () => {
                const prompt = btn.getAttribute('data-prompt') || '';
                if (prompt) {
                    this.sendMessage(prompt);
                }
            });
        });

        // Delegate copy-code button clicks
        this.messagesEl.addEventListener('click', (e) => {
            const copyBtn = e.target.closest('.ai-copy-btn');
            if (!copyBtn) return;
            const codeEl = copyBtn.closest('.ai-code-block')?.querySelector('code');
            if (!codeEl) return;
            navigator.clipboard?.writeText(codeEl.textContent || '').then(() => {
                const prev = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fa-solid fa-check text-success me-1"></i>Copied';
                setTimeout(() => {
                    copyBtn.innerHTML = prev;
                }, 1500);
            });
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    autoResizeInput() {
        this.inputEl.style.height = 'auto';
        const nextHeight = Math.min(this.inputEl.scrollHeight, 120);
        this.inputEl.style.height = `${Math.max(38, nextHeight)}px`;
    }

    open() {
        this.isOpen = true;
        this.panel.classList.add('open');
        this.panel.setAttribute('aria-hidden', 'false');
        this.fab?.classList.add('active');
        this.updateContextSubtitle();
        this.scrollToBottom();
        setTimeout(() => this.inputEl?.focus(), 120);
    }

    close() {
        this.isOpen = false;
        this.panel.classList.remove('open');
        this.panel.setAttribute('aria-hidden', 'true');
        this.fab?.classList.remove('active');
    }

    toggle() {
        if (this.isOpen) this.close();
        else this.open();
    }

    toggleExpand() {
        this.isExpanded = !this.isExpanded;
        this.panel.classList.toggle('expanded', this.isExpanded);
        const icon = this.expandBtn?.querySelector('i');
        if (icon) {
            icon.className = this.isExpanded
                ? 'fa-solid fa-down-left-and-up-right-to-center'
                : 'fa-solid fa-up-right-and-down-left-from-center';
        }
    }

    askQuestion(text) {
        if (!text || !text.trim()) return;
        this.open();
        this.sendMessage(text.trim());
    }

    getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta && meta.content && meta.content !== 'NOTPROVIDED') {
            return meta.content;
        }
        const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : '';
    }

    collectWorkspaceContext() {
        const ctx = {
            page_title: (document.title || '').slice(0, 120),
            path: (window.location.pathname || '/').slice(0, 120),
        };

        const canvas = window.ramonetCanvas;
        if (canvas && canvas.project) {
            const devices = Array.isArray(canvas.project.devices) ? canvas.project.devices : [];
            const connections = Array.isArray(canvas.project.connections) ? canvas.project.connections : [];
            ctx.topology_summary = {
                device_count: devices.length,
                connection_count: connections.length,
            };
            if (canvas.selectedDevice) {
                ctx.selected_device = {
                    name: canvas.selectedDevice.name || '',
                    category: canvas.selectedDevice.category || '',
                    ip: canvas.selectedDevice.ip || '',
                    gateway: canvas.selectedDevice.gateway || '',
                };
            }
        }
        return ctx;
    }

    updateContextSubtitle() {
        if (!this.subtitleEl) return;
        const canvas = window.ramonetCanvas;
        if (canvas?.selectedDevice) {
            this.subtitleEl.textContent = `Context: ${canvas.selectedDevice.name} (${canvas.selectedDevice.ip || 'No IP'})`;
        } else if (window.location.pathname.includes('/topology/designer')) {
            const devCount = canvas?.project?.devices?.length || 0;
            this.subtitleEl.textContent = `Context: Network Designer (${devCount} devices)`;
        } else {
            this.subtitleEl.textContent = 'Networking, CLI, Labs & Platform Help';
        }
    }

    loadHistory() {
        try {
            const raw = sessionStorage.getItem(this.storageKey);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed)) {
                    this.history = parsed.slice(-this.maxStoredTurns);
                }
            }
        } catch (e) {
            this.history = [];
        }
    }

    saveHistory() {
        try {
            sessionStorage.setItem(
                this.storageKey,
                JSON.stringify(this.history.slice(-this.maxStoredTurns))
            );
        } catch (e) {
            // Ignore storage quota errors gracefully
        }
    }

    clearHistory() {
        this.history = [];
        this.saveHistory();
        this.renderMessages();
        this.inputEl?.focus();
    }

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str == null ? '' : String(str);
        return div.innerHTML;
    }

    formatSafeMarkdown(rawText) {
        const codeBlocks = [];
        const textWithPlaceholders = String(rawText || '').replace(
            /```([a-zA-Z0-9_-]*)\n?([\s\S]*?)```/g,
            (_, lang, code) => {
                const idx = codeBlocks.length;
                codeBlocks.push({
                    lang: (lang || 'cli').toLowerCase(),
                    code: code.replace(/\n$/, ''),
                });
                return `@@AI_CODE_BLOCK_${idx}@@`;
            }
        );

        let safe = this.escapeHtml(textWithPlaceholders);

        // Headings (###, ##, #)
        safe = safe.replace(/^###\s+(.+)$/gm, '<div class="ai-md-h3">$1</div>');
        safe = safe.replace(/^##\s+(.+)$/gm, '<div class="ai-md-h2">$1</div>');

        // Bold & inline code
        safe = safe.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
        safe = safe.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
        safe = safe.replace(/`([^`\n]+)`/g, '<code class="ai-inline-code">$1</code>');

        // Bullet and numbered list items
        safe = safe.replace(/^(?:[-*])\s+(.+)$/gm, '<li class="ai-md-li">$1</li>');
        safe = safe.replace(/^(\d+)\.\s+(.+)$/gm, '<li class="ai-md-li"><span class="text-cyan fw-bold me-1">$1.</span>$2</li>');
        safe = safe.replace(/(<li class="ai-md-li">[\s\S]*?<\/li>(?:\n|$))+/g, (block) => {
            return `<ul class="ai-md-list">${block.replace(/\n/g, '')}</ul>`;
        });

        // Paragraph line breaks
        safe = safe.replace(/\n{2,}/g, '<div class="ai-md-spacer"></div>');
        safe = safe.replace(/\n/g, '<br>');

        // Restore fenced code blocks securely
        codeBlocks.forEach((blk, idx) => {
            const safeLang = this.escapeHtml(blk.lang);
            const safeCode = this.escapeHtml(blk.code);
            const htmlBlock = `
                <div class="ai-code-block">
                    <div class="ai-code-header">
                        <span>${safeLang}</span>
                        <button type="button" class="ai-copy-btn"><i class="fa-regular fa-copy me-1"></i>Copy</button>
                    </div>
                    <pre><code>${safeCode}</code></pre>
                </div>
            `;
            safe = safe.replace(`@@AI_CODE_BLOCK_${idx}@@`, htmlBlock);
        });

        return safe;
    }

    renderMessages() {
        if (!this.messagesEl) return;

        if (this.history.length === 0) {
            this.messagesEl.innerHTML = `
                <div class="ai-welcome-card">
                    <div class="d-flex align-items-center gap-2 mb-2">
                        <span class="ai-welcome-icon"><i class="fa-solid fa-robot text-cyan"></i></span>
                        <div>
                            <div class="text-white fw-bold small">Welcome to RAMONET AI Copilot</div>
                            <div class="text-muted" style="font-size: 0.72rem;">Powered by Google Gemini</div>
                        </div>
                    </div>
                    <p class="text-secondary small mb-2">
                        Ask anything about <strong>computer networking</strong> (Cisco IOS CLI, VLANs, OSPF, NAT, subnetting, troubleshooting), <strong>how to use RAMONET tools</strong>, or study topics!
                    </p>
                    <div class="text-muted font-monospace" style="font-size: 0.68rem;">
                        <i class="fa-solid fa-circle-info text-cyan me-1"></i>Pick a prompt below or type your own question.
                    </div>
                </div>
            `;
            return;
        }

        const fragments = this.history.map((turn) => {
            if (turn.role === 'user') {
                return `
                    <div class="ai-msg-row ai-msg-user">
                        <div class="ai-msg-bubble user">
                            ${this.escapeHtml(turn.text).replace(/\n/g, '<br>')}
                        </div>
                    </div>
                `;
            }
            const sourceBadge = turn.source === 'fallback'
                ? '<span class="ai-model-tag fallback">Local KB</span>'
                : `<span class="ai-model-tag">${this.escapeHtml(turn.model || 'Gemini')}</span>`;

            return `
                <div class="ai-msg-row ai-msg-model">
                    <div class="ai-msg-avatar"><i class="fa-solid fa-wand-magic-sparkles"></i></div>
                    <div class="ai-msg-bubble model">
                        <div class="ai-msg-meta">
                            <span class="fw-semibold text-cyan">RAMONET AI</span>
                            ${sourceBadge}
                        </div>
                        <div class="ai-msg-body">${this.formatSafeMarkdown(turn.text)}</div>
                    </div>
                </div>
            `;
        });

        this.messagesEl.innerHTML = fragments.join('');
        this.scrollToBottom();
    }

    appendTypingIndicator() {
        const existing = document.getElementById('ai-typing-indicator');
        if (existing) existing.remove();

        const row = document.createElement('div');
        row.id = 'ai-typing-indicator';
        row.className = 'ai-msg-row ai-msg-model';
        row.innerHTML = `
            <div class="ai-msg-avatar"><i class="fa-solid fa-wand-magic-sparkles"></i></div>
            <div class="ai-msg-bubble model">
                <div class="ai-typing-dots" aria-label="AI is typing">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        this.messagesEl.appendChild(row);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        document.getElementById('ai-typing-indicator')?.remove();
    }

    scrollToBottom() {
        if (!this.messagesEl) return;
        this.messagesEl.scrollTop = this.messagesEl.scrollHeight;
    }

    async sendMessage(text) {
        if (this.isSending || !text) return;

        const cleanText = text.trim();
        if (!cleanText) return;

        // Snapshot prior history before appending the new turn
        const priorHistory = this.history.slice(-10).map((t) => ({
            role: t.role,
            text: t.text,
        }));

        this.history.push({ role: 'user', text: cleanText });
        this.saveHistory();
        this.inputEl.value = '';
        this.autoResizeInput();
        this.renderMessages();

        this.isSending = true;
        if (this.sendBtn) this.sendBtn.disabled = true;
        this.appendTypingIndicator();

        try {
            const resp = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({
                    message: cleanText,
                    history: priorHistory,
                    context: this.collectWorkspaceContext(),
                }),
            });

            const data = await resp.json().catch(() => ({}));
            this.removeTypingIndicator();

            if (!resp.ok) {
                const errMsg = data.error || `Request failed (HTTP ${resp.status}). Please try again.`;
                this.history.push({
                    role: 'model',
                    text: `⚠️ ${errMsg}`,
                    source: 'fallback',
                });
            } else {
                this.history.push({
                    role: 'model',
                    text: data.reply || 'No response received.',
                    model: data.model || 'gemini',
                    source: data.source || 'gemini',
                });
            }
        } catch (err) {
            this.removeTypingIndicator();
            this.history.push({
                role: 'model',
                text: '⚠️ Network error reaching RAMONET AI service. Please check your connection and try again.',
                source: 'fallback',
            });
        } finally {
            this.isSending = false;
            if (this.sendBtn) this.sendBtn.disabled = false;
            this.saveHistory();
            this.renderMessages();
            this.inputEl?.focus();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.ramonetAIChat = new RamonetAIChatbot();
});
