/**
 * tree_interact.js
 * 
 * Tree interaction and AJAX functionality
 * Version: 1.0.0
 * Date: 2025-11-27
 */

const TreeInteract = {
    config: {
        endpoint: '',
        scanAction: 'scan',
        onScanStart: null,
        onScanComplete: null,
        onScanError: null
    },
    
    currentTree: null,
    currentBasePath: null,
    
    /**
     * Initialize tree interaction
     */
    init: function(config = {}) {
        this.config = {...this.config, ...config};
        return true;
    },
    
    /**
     * Scan directory
     */
    scanDirectory: function(directory) {
        if (!directory) {
            this.handleError('Directory path required');
            return;
        }
        
        if (this.config.onScanStart) {
            this.config.onScanStart();
        }
        
        const formData = new FormData();
        formData.append('action', this.config.scanAction);
        formData.append('directory', directory);
        
        fetch(this.config.endpoint, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.currentTree = data.tree;
                this.currentBasePath = data.base_path;
                
                if (this.config.onScanComplete) {
                    this.config.onScanComplete(data);
                }
            } else {
                this.handleError(data.error || 'Scan failed');
            }
        })
        .catch(error => {
            this.handleError('Network error: ' + error.message);
        });
    },
    
    /**
     * Handle error
     */
    handleError: function(message) {
        console.error('Tree error:', message);
        
        if (this.config.onScanError) {
            this.config.onScanError(message);
        }
    },
    
    /**
     * Get current tree
     */
    getTree: function() {
        return this.currentTree;
    },
    
    /**
     * Get base path
     */
    getBasePath: function() {
        return this.currentBasePath;
    }
};
