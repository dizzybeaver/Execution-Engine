/**
 * sima-export-scan.js
 * 
 * Scanning functionality with version detection
 * Version: 4.3.1
 * Date: 2025-11-23
 * Location: /support/php/js/
 * 
 * FIXED: Proper version detection display
 */

/**
 * Scan directory for SIMA knowledge
 */
function scanDirectory() {
    const directory = document.getElementById('simaDirectory').value.trim();
    if (!directory) {
        alert('Please enter a SIMA directory path');
        return;
    }
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').classList.remove('active');
    document.getElementById('scan-btn').disabled = true;
    
    const formData = new FormData();
    formData.append('action', 'scan');
    formData.append('directory', directory);
    
    fetch('', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('scan-btn').disabled = false;
        
        if (data.success) {
            // Store globally
            window.knowledgeTree = data.tree;
            window.currentBasePath = data.base_path;
            
            // FIXED: Display version info properly
            if (data.version_info && data.version_info.version !== 'unknown') {
                const versionEl = document.getElementById('detectedVersion');
                const stats = data.stats;
                
                versionEl.textContent = `✓ Detected: SIMA v${data.version_info.version} - ${stats.total_files} files found`;
                versionEl.style.display = 'block';
                
                // Set source version dropdown
                document.getElementById('sourceVersion').value = data.version_info.version;
            }
            
            // Render tree (function from sima-export-render.js)
            renderTree();
            
            // Show sections
            document.getElementById('tree-section').classList.remove('hidden');
            document.getElementById('export-section').classList.remove('hidden');
            
            // Update summary (function from sima-export-selection.js)
            updateSummary();
        } else {
            document.getElementById('error-text').textContent = data.error;
            document.getElementById('error').classList.add('active');
        }
    })
    .catch(err => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('scan-btn').disabled = false;
        document.getElementById('error-text').textContent = 'Error: ' + err.message;
        document.getElementById('error').classList.add('active');
    });
}
