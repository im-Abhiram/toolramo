/**
 * Ramonet Viral Social Sharing & Growth Utility
 * Generates one-click pre-populated shares to Reddit, Twitter/X, LinkedIn, WhatsApp, Telegram,
 * clipboard copy, and Markdown embed badges for GitHub/Docs.
 */
(function() {
    window.openShareModal = function(customTitle, customUrl) {
        const title = customTitle || document.title || 'RAMONET — Enterprise Network Simulator & Lab';
        const url = customUrl || window.location.href;
        
        const modalEl = document.getElementById('ramonetShareModal');
        if (!modalEl) return;

        const inputUrl = document.getElementById('share-modal-url');
        const inputBadge = document.getElementById('share-modal-badge');
        if (inputUrl) inputUrl.value = url;
        if (inputBadge) {
            inputBadge.value = `[![Designed with Ramonet](https://img.shields.io/badge/Network_Simulator-RAMONET_2.0-00f0ff?style=for-the-badge&logo=cisco)](${url})`;
        }

        // Configure Reddit button
        const redditBtn = document.getElementById('share-btn-reddit');
        if (redditBtn) {
            redditBtn.href = `https://www.reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title + ' - Free Online Network Simulator & CCNA Lab')}`;
        }

        // Configure Twitter/X button
        const twitterBtn = document.getElementById('share-btn-twitter');
        if (twitterBtn) {
            twitterBtn.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent('Check out ' + title + ' — interactive network simulator, Cisco IOS CLI, subnet calculator, and CCNA labs:')}&url=${encodeURIComponent(url)}&hashtags=networking,ccna,cisco,sysadmin`;
        }

        // Configure LinkedIn button
        const linkedinBtn = document.getElementById('share-btn-linkedin');
        if (linkedinBtn) {
            linkedinBtn.href = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
        }

        // Configure WhatsApp button
        const whatsappBtn = document.getElementById('share-btn-whatsapp');
        if (whatsappBtn) {
            whatsappBtn.href = `https://api.whatsapp.com/send?text=${encodeURIComponent(title + ': ' + url)}`;
        }

        // Configure Telegram button
        const telegramBtn = document.getElementById('share-btn-telegram');
        if (telegramBtn) {
            telegramBtn.href = `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
        }

        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    };

    window.copyShareLink = function() {
        const input = document.getElementById('share-modal-url');
        if (!input) return;
        navigator.clipboard.writeText(input.value).then(() => {
            showToast('Link copied to clipboard!');
        }).catch(() => {
            input.select();
            document.execCommand('copy');
            showToast('Link copied to clipboard!');
        });
    };

    window.copyShareBadge = function() {
        const input = document.getElementById('share-modal-badge');
        if (!input) return;
        navigator.clipboard.writeText(input.value).then(() => {
            showToast('Markdown embed badge copied!');
        }).catch(() => {
            input.select();
            document.execCommand('copy');
            showToast('Markdown embed badge copied!');
        });
    };

    window.showToast = function(msg) {
        let toastContainer = document.getElementById('ramonet-toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'ramonet-toast-container';
            toastContainer.style.cssText = 'position: fixed; bottom: 24px; right: 24px; z-index: 1090; display: flex; flex-direction: column; gap: 8px; pointer-events: none;';
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        toast.style.cssText = 'background: rgba(6, 9, 19, 0.95); border: 1px solid #00f0ff; color: #00f0ff; padding: 10px 18px; border-radius: 8px; font-size: 0.85rem; font-family: Manrope, sans-serif; box-shadow: 0 4px 20px rgba(0, 240, 255, 0.25); display: flex; align-items: center; gap: 8px; opacity: 0; transform: translateY(10px); transition: all 0.25s ease-out;';
        toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>${msg}</span>`;
        toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 20);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 250);
        }, 2500);
    };
})();
