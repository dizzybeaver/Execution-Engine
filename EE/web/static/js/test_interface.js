/**
 * Test Interface JavaScript
 * Execute EE operations and view results
 */

let testHistory = [];

$(document).ready(function() {
    // Form submission
    $('#test-form').on('submit', function(e) {
        e.preventDefault();
        executeTest();
    });

    // Clear button
    $('#clear-btn').on('click', function() {
        $('#parameters').val('');
        $('#result-output').text('// Results will appear here');
        $('#result-timing').text('-- ms');
        $('#result-status').text('--');
    });

    // Quick test buttons
    $('.quick-test').on('click', function() {
        const interface = $(this).data('interface');
        const operation = $(this).data('operation');
        const params = $(this).data('params') || {};

        $('#interface').val(interface);
        $('#operation').val(operation);
        $('#parameters').val(JSON.stringify(params, null, 2));

        executeTest();
    });
});

function executeTest() {
    const interface = $('#interface').val();
    const operation = $('#operation').val();
    const parameters = $('#parameters').val();

    if (!interface || !operation) {
        showAlert('Please select interface and operation', 'warning');
        return;
    }

    let params = {};
    if (parameters) {
        try {
            params = JSON.parse(parameters);
        } catch (e) {
            showAlert('Invalid JSON parameters: ' + e.message, 'danger');
            return;
        }
    }

    // Show loading
    $('#result-output').text('Executing...');
    $('#result-timing').removeClass('bg-success bg-danger').addClass('bg-secondary');

    // Execute operation
    $.ajax({
        url: '/api/test/operation',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            interface: interface,
            operation: operation,
            parameters: params
        }),
        success: function(response) {
            displayResult(response, interface, operation);
        },
        error: function(xhr) {
            const error = xhr.responseJSON || { error: 'Unknown error' };
            displayError(error.error || error.message, interface, operation);
        }
    });
}

function displayResult(response, interface, operation) {
    // Format result
    let resultText = JSON.stringify(response.result, null, 2);
    if (resultText.length > 5000) {
        resultText = resultText.substring(0, 5000) + '\n... (truncated)';
    }

    $('#result-output').text(resultText);
    $('#result-timing').text(response.timing_ms + ' ms');
    $('#result-timing').removeClass('bg-secondary').addClass('bg-success');
    $('#result-status').text('Success');
    $('#result-status').removeClass('bg-secondary bg-danger').addClass('bg-success');

    // Add to history
    addToHistory(interface, operation, true, response.timing_ms);
}

function displayError(error, interface, operation) {
    $('#result-output').text('Error: ' + error);
    $('#result-timing').text('N/A');
    $('#result-timing').removeClass('bg-success bg-secondary').addClass('bg-danger');
    $('#result-status').text('Failed');
    $('#result-status').removeClass('bg-secondary bg-success').addClass('bg-danger');

    // Add to history
    addToHistory(interface, operation, false, 0);
}

function addToHistory(interface, operation, success, timing) {
    const historyItem = {
        interface: interface,
        operation: operation,
        success: success,
        timing: timing,
        timestamp: new Date()
    };

    testHistory.unshift(historyItem);

    // Keep only last 10
    if (testHistory.length > 10) {
        testHistory.pop();
    }

    renderHistory();
}

function renderHistory() {
    const historyDiv = $('#test-history');

    if (testHistory.length === 0) {
        historyDiv.html('<div class="list-group-item text-muted">No tests executed yet</div>');
        return;
    }

    let html = '';
    for (const item of testHistory) {
        const badgeClass = item.success ? 'bg-success' : 'bg-danger';
        const icon = item.success ? 'check-circle' : 'x-circle';

        html += `
            <div class="list-group-item">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">
                        <i class="bi bi-${icon}"></i>
                        <code>${item.interface}</code>.${item.operation}
                    </h6>
                    <small>${item.timestamp.toLocaleTimeString()}</small>
                </div>
                <p class="mb-1">
                    <span class="badge ${badgeClass}">${item.success ? 'Success' : 'Failed'}</span>
                    <span class="text-muted">${item.timing.toFixed(2)} ms</span>
                </p>
            </div>
        `;
    }

    historyDiv.html(html);
}
