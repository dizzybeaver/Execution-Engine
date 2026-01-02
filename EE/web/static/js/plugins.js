/**
 * Plugins JavaScript
 * Plugin management and status
 */

$(document).ready(function() {
    loadPluginStatus();

    // Update every 5 seconds
    setInterval(loadPluginStatus, 5000);
});

function loadPluginStatus() {
    $.get('/api/plugins')
        .done(function(response) {
            updatePluginUI(response.plugins);
        })
        .fail(function() {
            showAlert('Failed to load plugin status', 'danger');
        });
}

function updatePluginUI(plugins) {
    if (!plugins) return;

    // Update FaaS plugin
    if (plugins.FaaS) {
        const faasStatus = plugins.FaaS.status === 'active' || plugins.FaaS.status === 'enabled';
        $('#faas-status-badge').text(faasStatus ? 'Enabled' : 'Disabled');
        $('#faas-status-badge').removeClass('bg-success bg-danger')
            .addClass(faasStatus ? 'bg-success' : 'bg-danger');
        $('#faas-info-status').text(faasStatus ? 'Enabled' : 'Disabled');
        $('#faas-info-status').removeClass('bg-success bg-danger')
            .addClass(faasStatus ? 'bg-success' : 'bg-danger');
    }

    // Update HA plugin
    if (plugins.HA) {
        const haStatus = plugins.HA.status === 'active' || plugins.HA.status === 'enabled';
        $('#ha-status-badge').text(haStatus ? 'Enabled' : 'Disabled');
        $('#ha-status-badge').removeClass('bg-success bg-danger')
            .addClass(haStatus ? 'bg-success' : 'bg-danger');
        $('#ha-info-status').text(haStatus ? 'Enabled' : 'Disabled');
        $('#ha-info-status').removeClass('bg-success bg-danger')
            .addClass(haStatus ? 'bg-success' : 'bg-danger');
    }
}

function togglePlugin(pluginName, enabled) {
    $.ajax({
        url: `/api/plugins/${pluginName}/toggle`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ enabled: enabled }),
        success: function(response) {
            showAlert(response.message, 'success');
            loadPluginStatus();
        },
        error: function(xhr) {
            const error = xhr.responseJSON || { error: 'Unknown error' };
            showAlert('Failed to toggle plugin: ' + error.error, 'danger');
        }
    });
}

// Override plugin update handler
function handlePluginUpdate(data) {
    if (data.plugin === 'FaaS' || data.plugin === 'HA') {
        loadPluginStatus();
    }
}
