/**
 * Common JavaScript Functions
 * Shared utilities for all pages
 */

// WebSocket connection
let socket = null;

// Initialize WebSocket connection
function initWebSocket() {
    socket = io();

    socket.on('connect', function() {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
    });

    socket.on('disconnect', function() {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
    });

    socket.on('status_update', function(data) {
        handleStatusUpdate(data);
    });

    socket.on('metrics_update', function(data) {
        handleMetricsUpdate(data);
    });

    socket.on('plugin_update', function(data) {
        handlePluginUpdate(data);
    });
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    const statusIcon = $('#connection-status');
    const statusText = $('#connection-text');

    if (connected) {
        statusIcon.removeClass('text-danger').addClass('text-success');
        statusText.text('Connected');
    } else {
        statusIcon.removeClass('text-success').addClass('text-danger');
        statusText.text('Disconnected');
    }
}

// Handle status updates (override in page-specific scripts)
function handleStatusUpdate(data) {
    console.log('Status update:', data);
}

// Handle metrics updates (override in page-specific scripts)
function handleMetricsUpdate(data) {
    console.log('Metrics update:', data);
}

// Handle plugin updates (override in page-specific scripts)
function handlePluginUpdate(data) {
    console.log('Plugin update:', data);
}

// Format milliseconds to human-readable
function formatUptime(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
        return `${days}d ${hours % 24}h ${minutes % 60}m`;
    } else if (hours > 0) {
        return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${seconds % 60}s`;
    } else {
        return `${seconds}s`;
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertDiv = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    );

    $('body').prepend(alertDiv);

    setTimeout(function() {
        alertDiv.alert('close');
    }, 5000);
}

// Format bytes to human-readable
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Initialize on document ready
$(document).ready(function() {
    initWebSocket();

    // Periodic status updates
    setInterval(updateEEStatus, 5000);
});

// Update EE status in footer
function updateEEStatus() {
    $.get('/api/status')
        .done(function(data) {
            $('#ee-status').text(data.status);
            if (data.uptime) {
                $('#ee-uptime').text(formatUptime(data.uptime * 1000));
            }
        })
        .fail(function() {
            $('#ee-status').text('Disconnected');
        });
}
