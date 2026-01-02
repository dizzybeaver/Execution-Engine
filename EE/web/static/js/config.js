/**
 * Configuration JavaScript
 * Configuration editor with 150+ variables
 */

let currentConfig = {};
let currentCategory = 'core';
let configModified = false;

$(document).ready(function() {
    loadConfiguration();

    // Category selection
    $('#category-list a').on('click', function(e) {
        e.preventDefault();
        $('#category-list a').removeClass('active');
        $(this).addClass('active');

        currentCategory = $(this).data('category');
        renderCategory(currentCategory);
    });

    // Profile selection
    $('#profile-select').on('change', function() {
        const profile = $(this).val();
        updateProfileDescription(profile);
    });

    // Track configuration changes
    $(document).on('change', '#config-form input, #config-form select', function() {
        configModified = true;
        updateSaveButton();
    });
});

function loadConfiguration() {
    $.get('/api/config')
        .done(function(response) {
            currentConfig = response.config;
            renderCategory(currentCategory);
        })
        .fail(function() {
            showAlert('Failed to load configuration', 'danger');
        });
}

function renderCategory(category) {
    const configFields = $('#config-fields');
    const categoryTitle = $('#category-title');

    // Update title
    const titles = {
        'core': 'Core Foundation Settings',
        'observability': 'Observability Settings',
        'security': 'Security Settings',
        'communication': 'Communication Settings',
        'operations': 'Operations Settings',
        'infrastructure': 'Infrastructure Settings',
        'optimization': 'Optimization Settings',
        'aws': 'AWS Settings',
        'features': 'Feature Flags'
    };
    categoryTitle.text(titles[category] || category);

    // Get category config
    const categoryConfig = currentConfig[category] || {};

    // Render fields
    let html = renderConfigFields(category, categoryConfig, '');
    configFields.html(html);
}

function renderConfigFields(category, config, prefix) {
    let html = '';

    for (const [key, value] of Object.entries(config)) {
        const fullKey = prefix ? `${prefix}.${key}` : key;

        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            // Nested object - render as section
            html += `
                <div class="mb-3">
                    <h6 class="text-primary">${key}</h6>
                    <div class="ms-3 border-start ps-3">
                        ${renderConfigFields(category, value, fullKey)}
                    </div>
                </div>
            `;
        } else {
            // Render field based on type
            html += renderField(fullKey, key, value);
        }
    }

    return html;
}

function renderField(fullKey, key, value) {
    const fieldType = typeof value;

    if (fieldType === 'boolean') {
        return `
            <div class="mb-3">
                <label for="${fullKey}" class="form-label">${key}</label>
                <select class="form-select" id="${fullKey}" name="${fullKey}">
                    <option value="true" ${value ? 'selected' : ''}>True</option>
                    <option value="false" ${!value ? 'selected' : ''}>False</option>
                </select>
            </div>
        `;
    } else if (fieldType === 'number') {
        return `
            <div class="mb-3">
                <label for="${fullKey}" class="form-label">${key}</label>
                <input type="number" class="form-control" id="${fullKey}"
                       name="${fullKey}" value="${value}">
            </div>
        `;
    } else if (Array.isArray(value)) {
        return `
            <div class="mb-3">
                <label for="${fullKey}" class="form-label">${key}</label>
                <input type="text" class="form-control" id="${fullKey}"
                       name="${fullKey}" value="${value.join(', ')}">
                <small class="form-text text-muted">Comma-separated values</small>
            </div>
        `;
    } else {
        return `
            <div class="mb-3">
                <label for="${fullKey}" class="form-label">${key}</label>
                <input type="text" class="form-control" id="${fullKey}"
                       name="${fullKey}" value="${value}">
            </div>
        `;
    }
}

function updateSaveButton() {
    const saveBtn = $('#save-btn');
    const restartBtn = $('#restart-btn');

    if (configModified) {
        saveBtn.prop('disabled', false);
        restartBtn.prop('disabled', false);
    } else {
        saveBtn.prop('disabled', true);
        restartBtn.prop('disabled', true);
    }
}

function saveConfiguration() {
    // Gather form data
    const formData = {};
    $('#config-form [name]').each(function() {
        const name = $(this).attr('name');
        let value = $(this).val();

        // Parse value based on type
        if ($(this).is('select')) {
            value = value === 'true';
        } else if ($(this).attr('type') === 'number') {
            value = parseFloat(value);
        }

        // Set nested value
        const parts = name.split('.');
        let current = formData;
        for (let i = 0; i < parts.length - 1; i++) {
            if (!current[parts[i]]) {
                current[parts[i]] = {};
            }
            current = current[parts[i]];
        }
        current[parts[parts.length - 1]] = value;
    });

    // Update current config
    Object.assign(currentConfig, formData);

    // Save to server
    $.ajax({
        url: '/api/config',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ config: currentConfig }),
        success: function(response) {
            showAlert(response.message, 'success');
            $('#save-status').text('Saved at ' + new Date().toLocaleTimeString());
            configModified = false;
            updateSaveButton();
        },
        error: function(xhr) {
            const error = xhr.responseJSON || { error: 'Unknown error' };
            showAlert('Failed to save configuration: ' + error.error, 'danger');
        }
    });
}

function cancelEdit() {
    loadConfiguration();
    configModified = false;
    updateSaveButton();
    $('#save-status').text('');
}

function restartServer() {
    if (!confirm('Are you sure you want to restart the server?')) {
        return;
    }

    $.ajax({
        url: '/api/restart',
        method: 'POST',
        success: function(response) {
            showAlert('Server restart requested. Page will refresh in 5 seconds...', 'warning');
            setTimeout(function() {
                location.reload();
            }, 5000);
        },
        error: function(xhr) {
            const error = xhr.responseJSON || { error: 'Unknown error' };
            showAlert('Failed to restart server: ' + error.error, 'danger');
        }
    });
}

function updateProfileDescription(profile) {
    const descriptions = {
        'development': 'Development profile with debug logging enabled',
        'testing': 'Testing profile optimized for automated tests',
        'staging': 'Staging profile for pre-production testing',
        'production': 'Production profile with minimal logging'
    };

    $('#profile-description').text(descriptions[profile] || '');
}
