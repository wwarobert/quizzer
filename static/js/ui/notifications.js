/**
 * Notification System
 * Overlay notification with focus trap and keyboard navigation
 */

/**
 * Show notification overlay with custom icon, title, message, and buttons
 * @param {string} icon - Emoji icon to display
 * @param {string} title - Notification title
 * @param {string} message - Notification message
 * @param {Array} buttons - Array of button configurations {text, primary, onClick}
 */
export function showNotification(icon, title, message, buttons = [{ text: 'OK', primary: true }]) {
    const overlay = document.getElementById('notificationOverlay');
    const iconEl = document.getElementById('notificationIcon');
    const titleEl = document.getElementById('notificationTitle');
    const messageEl = document.getElementById('notificationMessage');
    const buttonsEl = document.getElementById('notificationButtons');
    const closeBtn = document.getElementById('notificationCloseBtn');

    iconEl.textContent = icon;
    titleEl.textContent = title;
    messageEl.textContent = message;
    buttonsEl.innerHTML = '';

    buttons.forEach(btn => {
        const button = document.createElement('button');
        button.className = `notification-btn ${btn.primary ? 'notification-btn-primary' : 'notification-btn-secondary'}`;
        button.textContent = btn.text;
        button.onclick = () => {
            overlay.classList.add('hidden');
            if (btn.onClick) btn.onClick();
        };
        buttonsEl.appendChild(button);
    });

    overlay.classList.remove('hidden');

    // Focus trap and Esc-to-close for dialog
    const focusable = overlay.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    (first || closeBtn)?.focus();

    function onKeyDown(e) {
        if (e.key === 'Escape') {
            overlay.classList.add('hidden');
            overlay.removeEventListener('keydown', onKeyDown);
        }
        if (e.key === 'Tab') {
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        }
    }
    overlay.addEventListener('keydown', onKeyDown);
}

/**
 * Show confirmation dialog with Cancel and Confirm buttons
 * @param {string} icon - Emoji icon to display
 * @param {string} title - Dialog title
 * @param {string} message - Dialog message
 * @param {Function} onConfirm - Callback when confirmed
 * @param {Function} onCancel - Callback when cancelled
 */
export function showConfirm(icon, title, message, onConfirm, onCancel) {
    showNotification(icon, title, message, [
        { text: 'Cancel', primary: false, onClick: onCancel },
        { text: 'Confirm', primary: true, onClick: onConfirm }
    ]);
}
