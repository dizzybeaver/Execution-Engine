/**
 * sima-export-render.js
 * 
 * Version: 5.0.0
 * Date: 2025-11-28
 * Purpose: Tree rendering and display for SIMA Export Tool
 * 
 * REFACTORED: Works with UI module generated HTML
 */

/**
 * Render tree and show results
 */
function renderTree(treeHtml, versionInfo, stats) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    
    // Build version info HTML
    let versionHtml = '<div class="version-info">';
    versionHtml += '<h3>Detected Version</h3>';
    versionHtml += '<p><strong>Version:</strong> ' + (versionInfo.version || 'Unknown') + '</p>';
    versionHtml += '<p><strong>Format:</strong> ' + (versionInfo.format || 'Unknown') + '</p>';
    versionHtml += '</div>';
    
    // Build stats HTML
    let statsHtml = '<div class="stats-info">';
    statsHtml += '<h3>Statistics</h3>';
    statsHtml += '<p><strong>Total Files:</strong> ' + (stats.total || 0) + '</p>';
    statsHtml += '<p><strong>Total Size:</strong> ' + formatSize(stats.total_size || 0) + '</p>';
    statsHtml += '</div>';
    
    // Build select all checkbox
    let selectAllHtml = '<div class="select-all">';
    selectAllHtml += '<label>';
    selectAllHtml += '<input type="checkbox" id="selectAll" onchange="selectAll(this.checked)">';
    selectAllHtml += ' Select All';
    selectAllHtml += '</label>';
    selectAllHtml += '</div>';
    
    // Combine all HTML
    resultsDiv.innerHTML = versionHtml + statsHtml + selectAllHtml + 
                          '<div class="tree-container">' + treeHtml + '</div>';
    
    // Show results
    resultsDiv.classList.remove('hidden');
    
    // Show export button
    const exportButton = document.getElementById('exportButtonContainer');
    if (exportButton) {
        exportButton.classList.remove('hidden');
    }
}

/**
 * Select/deselect all checkboxes
 */
function selectAll(checked) {
    const checkboxes = document.querySelectorAll('.tree-container input[type="checkbox"]');
    checkboxes.forEach(cb => {
        cb.checked = checked;
    });
}

/**
 * Format file size
 */
function formatSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const units = ['B', 'KB', 'MB', 'GB'];
    const k = 1024;
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i];
}
