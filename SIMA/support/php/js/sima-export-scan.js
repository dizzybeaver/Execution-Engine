/**
 * sima-export-scan.js
 * 
 * Version: 5.0.0
 * Date: 2025-11-28
 * Purpose: Directory scanning functionality for SIMA Export Tool
 * 
 * REFACTORED: Works with modular backend
 */

/**
 * Scan directory
 */
function scanDirectory() {
    const directory = document.getElementById('directory').value.trim();
    
    if (!directory) {
        showStatus('error', 'Please enter a directory path');
        return;
    }
    
    // Show loading
    showLoading(true);
    hideStatus();
    hideResults();
    
    // Prepare form data
    const formData = new FormData();
    formData.append('action', 'scan');
    formData.append('directory', directory);
    
    // Send request
    fetch(window.location.href, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success === false) {
            showStatus('error', data.error || 'Scan failed');
            return;
        }
        
        if (data.tree) {
            renderTree(data.tree, data.version, data.stats);
            showStatus('success', 'Scan completed successfully');
        } else {
            showStatus('error', 'Invalid response from server');
        }
    })
    .catch(error => {
        showLoading(false);
        showStatus('error', 'Request failed: ' + error.message);
    });
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
}

/**
 * Show status message
 */
function showStatus(type, message) {
    const statusDiv = document.getElementById('status');
    if (!statusDiv) return;
    
    const icons = {
        'info': 'ℹ',
        'success': '✓',
        'warning': '⚠',
        'error': '✗'
    };
    
    const classes = {
        'info': 'status-info',
        'success': 'status-success',
        'warning': 'status-warning',
        'error': 'status-error'
    };
    
    statusDiv.className = 'sima-status ' + (classes[type] || classes['info']);
    statusDiv.innerHTML = `
        <span class="status-icon">${icons[type] || icons['info']}</span>
        <span class="status-message">${message}</span>
    `;
    statusDiv.style.display = 'block';
}

/**
 * Hide status message
 */
function hideStatus() {
    const statusDiv = document.getElementById('status');
    if (statusDiv) {
        statusDiv.style.display = 'none';
    }
}

/**
 * Hide results
 */
function hideResults() {
    const results = document.getElementById('results');
    if (results) {
        results.classList.add('hidden');
    }
    
    const exportButton = document.getElementById('exportButtonContainer');
    if (exportButton) {
        exportButton.classList.add('hidden');
    }
}

// Attach to form submit
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('exportForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            scanDirectory();
        });
    }
});
