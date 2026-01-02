/**
 * sima-export-selection.js
 * 
 * Version: 5.0.0
 * Date: 2025-11-28
 * Purpose: File selection management for SIMA Export Tool
 * 
 * REFACTORED: Works with tree module output
 */

/**
 * Get selected files
 */
function getSelectedFiles() {
    const checkboxes = document.querySelectorAll('.tree-container input[type="checkbox"]:checked');
    const files = [];
    
    checkboxes.forEach(cb => {
        // Get file info from data attributes
        const path = cb.getAttribute('data-path');
        const refId = cb.getAttribute('data-ref-id');
        const size = cb.getAttribute('data-size');
        const checksum = cb.getAttribute('data-checksum');
        
        if (path) {
            files.push({
                path: path,
                ref_id: refId || '',
                size: parseInt(size) || 0,
                checksum: checksum || ''
            });
        }
    });
    
    return files;
}

/**
 * Count selected files
 */
function countSelected() {
    const checkboxes = document.querySelectorAll('.tree-container input[type="checkbox"]:checked');
    return checkboxes.length;
}

/**
 * Validate selection
 */
function validateSelection() {
    const count = countSelected();
    
    if (count === 0) {
        showStatus('warning', 'Please select at least one file to export');
        return false;
    }
    
    return true;
}
