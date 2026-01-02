/**
 * Dashboard JavaScript
 * Real-time dashboard updates and metrics
 */

let metricsData = {
    labels: [],
    datasets: [{
        label: 'Response Time (ms)',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
    }]
};

let metricsChart = null;

$(document).ready(function() {
    // Initialize dashboard
    loadDashboardData();

    // Update every 2 seconds
    setInterval(loadDashboardData, 2000);
});

function loadDashboardData() {
    $.get('/api/status')
        .done(function(data) {
            updateEngineStatus(data);
            updateInterfaceTable(data);
            updatePluginStatus(data);
            updateMetrics(data);
        })
        .fail(function(xhr) {
            if (xhr.status === 503) {
                $('#engine-status').text('Stopped');
                $('#engine-status-card').removeClass('bg-success').addClass('bg-danger');
            }
        });
}

function updateEngineStatus(data) {
    const statusCard = $('#engine-status-card');
    const statusText = $('#engine-status');

    if (data.status === 'running') {
        statusCard.removeClass('bg-danger bg-warning').addClass('bg-success');
        statusText.text('Running');
    } else if (data.status === 'stopped') {
        statusCard.removeClass('bg-success bg-warning').addClass('bg-danger');
        statusText.text('Stopped');
    } else {
        statusCard.removeClass('bg-success bg-danger').addClass('bg-warning');
        statusText.text('Error');
    }

    // Update gateway stats
    if (data.gateway_stats) {
        const stats = data.gateway_stats;
        $('#gateway-calls').text(stats.total_calls || 0);
        $('#avg-response').text((stats.avg_response_time || 0).toFixed(2) + 'ms');
    }

    // Update memory usage
    if (data.memory_usage) {
        $('#memory-usage').text(formatBytes(data.memory_usage));
    }
}

function updateInterfaceTable(data) {
    const tbody = $('#interface-table');

    if (!data.interfaces || Object.keys(data.interfaces).length === 0) {
        tbody.html('<tr><td colspan="4" class="text-center">No interfaces available</td></tr>');
        return;
    }

    let html = '';
    for (const [name, info] of Object.entries(data.interfaces)) {
        const statusBadge = info.status === 'healthy'
            ? '<span class="badge bg-success">Healthy</span>'
            : '<span class="badge bg-danger">Unhealthy</span>';

        html += `
            <tr>
                <td><code>${name}</code></td>
                <td>${statusBadge}</td>
                <td>${info.operations || 'N/A'}</td>
                <td>${info.health || 'N/A'}</td>
            </tr>
        `;
    }

    tbody.html(html);
}

function updatePluginStatus(data) {
    const pluginDiv = $('#plugin-status');

    if (!data.plugins || Object.keys(data.plugins).length === 0) {
        return;
    }

    let html = '';
    for (const [name, info] of Object.entries(data.plugins)) {
        const statusClass = info.status === 'active' || info.status === 'enabled'
            ? 'border-success'
            : 'border-danger';

        const badgeClass = info.status === 'active' || info.status === 'enabled'
            ? 'bg-success'
            : 'bg-danger';

        html += `
            <div class="col-md-4">
                <div class="card ${statusClass}">
                    <div class="card-body">
                        <h6 class="card-title">${name}</h6>
                        <p class="card-text">
                            <span class="badge ${badgeClass}">${info.status}</span>
                            <span class="text-muted">${info.version || 'N/A'}</span>
                        </p>
                    </div>
                </div>
            </div>
        `;
    }

    pluginDiv.html(html);
}

function updateMetrics(data) {
    if (!data.gateway_stats) return;

    const responseTime = data.gateway_stats.avg_response_time || 0;
    const now = new Date().toLocaleTimeString();

    // Add data point
    metricsData.labels.push(now);
    metricsData.datasets[0].data.push(responseTime);

    // Keep only last 10 data points
    if (metricsData.labels.length > 10) {
        metricsData.labels.shift();
        metricsData.datasets[0].data.shift();
    }

    // Create or update chart
    if (!metricsChart) {
        const ctx = document.getElementById('metricsChart').getContext('2d');
        metricsChart = new Chart(ctx, {
            type: 'line',
            data: metricsData,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Response Time (ms)'
                        }
                    }
                }
            }
        });
    } else {
        metricsChart.update();
    }
}

// Override status update handler
function handleStatusUpdate(data) {
    loadDashboardData();
}
