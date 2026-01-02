/**
 * sima-export-export.js
 * 
 * Export functionality
 * Version: 4.3.1
 * Date: 2025-11-23
 * Location: /support/php/js/
 */

// Initialize global state
window.knowledgeTree = {};
window.currentBasePath = '';

/**
 * Export selected files
 */
function exportFiles() {
    if (window.selectedFiles.size === 0) {
        alert('Please select at least one file');
        return;
    }
    
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').classList.remove('active');
    
    const formData = new FormData();
    formData.append('action', 'export');
    formData.append('base_directory', window.currentBasePath);
    formData.append('archive_name', document.getElementById('archiveName').value.trim() || 'SIMA-Export');
    formData.append('description', document.getElementById('description').value.trim());
    formData.append('source_version', document.getElementById('sourceVersion').value);
    formData.append('target_version', document.getElementById('targetVersion').value);
    formData.append('selected_files', JSON.stringify(Array.from(window.selectedFiles)));
    
    fetch('', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        
        if (data.success) {
            document.getElementById('result-content').innerHTML = `
                <div class="success">
                    <h3>✓ Export Created Successfully!</h3>
                    <p><strong>Archive:</strong> ${data.archive_name}</p>
                    <p><strong>Files:</strong> ${data.file_count}</p>
                    <p><strong>Converted:</strong> ${data.converted_count}</p>
                    <p><a href="${data.download_url}" download>
                        <button>📥 Download Export</button>
                    </a></p>
                </div>`;
            document.getElementById('result-section').classList.remove('hidden');
            document.getElementById('result-section').scrollIntoView({ behavior: 'smooth' });
        } else {
            document.getElementById('error-text').textContent = data.error;
            document.getElementById('error').classList.add('active');
        }
    })
    .catch(err => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error-text').textContent = 'Error: ' + err.message;
        document.getElementById('error').classList.add('active');
    });
}
