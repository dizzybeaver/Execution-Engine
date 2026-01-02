/**
 * sima-export-export.js
 * 
 * Version: 5.0.0
 * Date: 2025-11-28
 * Purpose: Export execution for SIMA Export Tool
 * 
 * REFACTORED: Works with packaging module
 */

/**
 * Export selected files
 */
function exportFiles() {
    // Validate selection
    if (!validateSelection()) {
        return;
    }
    
    // Get form values
    const directory = document.getElementById('directory').value.trim();
    const archiveName = document.getElementById('archiveName').value.trim() || 'SIMA-Export';
    const description = document.getElementById('description').value.trim();
    
    // Get selected files
    const selectedFiles = getSelectedFiles();
    
    // Show loading
    showLoading(true);
    hideStatus();
    
    // Prepare form data
    const formData = new FormData();
    formData.append('action', 'export');
    formData.append('directory', directory);
    formData.append('archive_name', archiveName);
    formData.append('description', description);
    formData.append('selected_files', JSON.stringify(selectedFiles));
    formData.append('source_version', 'auto');
    formData.append('target_version', 'auto');
    
    // Send request
    fetch(window.location.href, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success === false) {
            showStatus('error', data.error || 'Export failed');
            return;
        }
        
        // Show success message with download link
        displayExportResult(data);
        showStatus('success', 'Export completed successfully!');
    })
    .catch(error => {
        showLoading(false);
        showStatus('error', 'Export failed: ' + error.message);
    });
}

/**
 * Display export result with download link
 */
function displayExportResult(data) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    
    // Create result HTML
    let resultHtml = '<div class="export-result">';
    resultHtml += '<h3>Export Complete</h3>';
    resultHtml += '<p><strong>Archive:</strong> ' + data.archive_name + '</p>';
    resultHtml += '<p><strong>Files Exported:</strong> ' + data.file_count + '</p>';
    
    if (data.converted_count && data.converted_count > 0) {
        resultHtml += '<p><strong>Files Converted:</strong> ' + data.converted_count + '</p>';
    }
    
    resultHtml += '<p><a href="' + data.download_url + '" class="download-link" download>';
    resultHtml += '⬇ Download Export Package</a></p>';
    resultHtml += '</div>';
    
    // Append to results
    const resultDiv = document.createElement('div');
    resultDiv.innerHTML = resultHtml;
    resultsDiv.appendChild(resultDiv);
}
