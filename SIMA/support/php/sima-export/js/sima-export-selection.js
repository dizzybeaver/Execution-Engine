/**
 * sima-export-selection.js
 * 
 * Selection management functionality
 * Version: 4.3.1
 * Date: 2025-11-23
 * Location: /support/php/js/
 */

// Initialize global state
window.selectedFiles = new Set();

/**
 * Update selection summary
 */
function updateSummary() {
    const count = window.selectedFiles.size;
    document.getElementById('summary').textContent = 
        `Selection: ${count} file${count !== 1 ? 's' : ''} selected`;
}

/**
 * Expand all tree nodes
 */
function expandAll() {
    document.querySelectorAll('.tree-container > div').forEach(d => {
        setExpanded(d, true);
    });
}

/**
 * Collapse all tree nodes
 */
function collapseAll() {
    document.querySelectorAll('.tree-container > div').forEach(d => {
        setExpanded(d, false);
    });
}

/**
 * Set expanded state for a node
 */
function setExpanded(div, expanded) {
    const childDiv = div.querySelector('div > div');
    const toggle = div.querySelector('span');
    
    if (childDiv && toggle) {
        childDiv.style.display = expanded ? 'block' : 'none';
        toggle.textContent = expanded ? '▼ ' : '▶ ';
    }
}

/**
 * Select all files
 */
function selectAll() {
    document.querySelectorAll('#tree input[type="checkbox"]').forEach(cb => {
        cb.checked = true;
        window.selectedFiles.add(cb.value);
    });
    updateSummary();
}

/**
 * Clear all selections
 */
function clearSelection() {
    document.querySelectorAll('#tree input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
    });
    window.selectedFiles.clear();
    updateSummary();
}
