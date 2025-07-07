// alert.js (jQuery version) with alert types

// Inject styles
$(`<style>
.alert-overlay-container {
    position: fixed;
    top: 32px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    pointer-events: none;
}
.alert-panel {
    min-width: 240px;
    max-width: 360px;
    margin-top: 12px;
    background: rgba(40, 40, 40, 0.7);
    color: #fff;
    backdrop-filter: blur(8px);
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.12);
    padding: 16px 24px;
    font-size: 1rem;
    opacity: 0;
    transform: translateY(-24px) scale(0.98);
    transition: opacity 0.3s cubic-bezier(.4,0,.2,1), 
                transform 0.3s cubic-bezier(.4,0,.2,1);
    pointer-events: auto;
    user-select: none;
    cursor: pointer;
}
.alert-panel.show {
    opacity: 1;
    transform: translateY(0) scale(1);
}
.alert-panel.hide {
    opacity: 0;
    transform: translateY(-24px) scale(0.98);
    transition: opacity 0.25s, transform 0.25s;
}
/* Alert types */
.alert-panel.info {
    background: rgba(30, 144, 255, 0.7);
}
.alert-panel.success {
    background: rgba(46, 204, 113, 0.7);
}
.alert-panel.warning {
    background: rgba(241, 196, 15, 0.85);
    color: #222;
}
.alert-panel.error {
    background: rgba(231, 76, 60, 0.8);
}
</style>`).appendTo('head');

// Create container if not exists
let $container = $('.alert-overlay-container');
if ($container.length === 0) {
    $container = $('<div class="alert-overlay-container"></div>').appendTo('body');
}

/**
 * Show a minimalistic alert.
 * @param {string} message - The alert message.
 * @param {number} [duration=3000] - Duration in ms before auto-dismiss.
 * @param {'info'|'success'|'warning'|'error'} [type='info'] - Alert type.
 */
function showAlert(message, duration = 3000, type = 'info') {
    const validTypes = ['info', 'success', 'warning', 'error'];
    const alertType = validTypes.includes(type) ? type : 'info';
    const $panel = $('<div class="alert-panel"></div>')
        .addClass(alertType)
        .text(message);

    // Show animation
    setTimeout(() => $panel.addClass('show'), 10);

    // Dismiss on click
    $panel.on('click', () => removePanel($panel));

    // Auto-dismiss
    const timeout = setTimeout(() => removePanel($panel), duration);

    // Remove panel with animation
    function removePanel($panel) {
        clearTimeout(timeout);
        $panel.removeClass('show').addClass('hide');
        $panel.one('transitionend', () => $panel.remove());
    }

    $container.append($panel);
}

/**
 * Remove all alert panels immediately.
 */
function clearAlerts() {
    $container.find('.alert-panel').remove();
}