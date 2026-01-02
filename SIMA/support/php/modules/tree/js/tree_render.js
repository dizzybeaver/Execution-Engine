/**
 * tree_render.js
 * 
 * Tree rendering functionality
 * Version: 1.0.0
 * Date: 2025-11-27
 */

const TreeRender = {
    config: {
        indentPixels: 20,
        showCheckboxes: true,
        collapsible: true,
        defaultCollapsed: false,
        showIcons: true,
        icons: {
            directory: '📁',
            file: '📄',
            expand: '▼',
            collapse: '▶'
        }
    },
    
    tree: null,
    container: null,
    
    /**
     * Initialize tree rendering
     */
    init: function(containerId, config = {}) {
        this.config = {...this.config, ...config};
        this.container = document.getElementById(containerId);
        
        if (!this.container) {
            console.error('Tree container not found:', containerId);
            return false;
        }
        
        return true;
    },
    
    /**
     * Render tree structure
     */
    render: function(tree) {
        if (!this.container) {
            console.error('Tree not initialized');
            return;
        }
        
        this.tree = tree;
        this.container.innerHTML = '';
        
        if (!tree || tree.length === 0) {
            this.container.innerHTML = '<p>No files found</p>';
            return;
        }
        
        tree.forEach(node => {
            this.container.appendChild(this.renderNode(node, 0));
        });
    },
    
    /**
     * Render individual node
     */
    renderNode: function(node, depth) {
        const div = document.createElement('div');
        div.className = 'tree-node';
        div.style.marginLeft = (depth * this.config.indentPixels) + 'px';
        div.dataset.type = node.type;
        div.dataset.path = node.path;
        
        if (node.type === 'directory') {
            div.appendChild(this.renderDirectory(node, depth));
        } else {
            div.appendChild(this.renderFile(node));
        }
        
        return div;
    },
    
    /**
     * Render directory node
     */
    renderDirectory: function(node, depth) {
        const wrapper = document.createElement('div');
        wrapper.className = 'tree-directory';
        
        const header = document.createElement('div');
        header.className = 'tree-directory-header';
        
        if (this.config.collapsible) {
            const toggle = document.createElement('span');
            toggle.className = 'tree-toggle';
            toggle.textContent = this.config.defaultCollapsed ? 
                this.config.icons.collapse : this.config.icons.expand;
            toggle.onclick = () => this.toggleDirectory(wrapper, toggle);
            header.appendChild(toggle);
        }
        
        if (this.config.showCheckboxes) {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'tree-checkbox';
            checkbox.dataset.path = node.path;
            checkbox.onchange = (e) => this.handleCheckboxChange(e, node);
            header.appendChild(checkbox);
        }
        
        const label = document.createElement('span');
        label.className = 'tree-label';
        
        if (this.config.showIcons) {
            label.textContent = `${this.config.icons.directory} ${node.name} (${node.total_files} files)`;
        } else {
            label.textContent = `${node.name} (${node.total_files} files)`;
        }
        
        header.appendChild(label);
        wrapper.appendChild(header);
        
        const childrenDiv = document.createElement('div');
        childrenDiv.className = 'tree-children';
        
        if (this.config.defaultCollapsed) {
            childrenDiv.style.display = 'none';
        }
        
        if (node.children) {
            node.children.forEach(child => {
                childrenDiv.appendChild(this.renderNode(child, depth + 1));
            });
        }
        
        wrapper.appendChild(childrenDiv);
        return wrapper;
    },
    
    /**
     * Render file node
     */
    renderFile: function(node) {
        const wrapper = document.createElement('div');
        wrapper.className = 'tree-file';
        
        if (this.config.showCheckboxes) {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.className = 'tree-checkbox';
            checkbox.dataset.path = node.path;
            checkbox.onchange = (e) => this.handleCheckboxChange(e, node);
            wrapper.appendChild(checkbox);
        }
        
        const label = document.createElement('span');
        label.className = 'tree-label';
        
        if (this.config.showIcons) {
            label.textContent = `${this.config.icons.file} ${node.name}`;
        } else {
            label.textContent = node.name;
        }
        
        wrapper.appendChild(label);
        
        if (node.ref_id) {
            const refId = document.createElement('span');
            refId.className = 'tree-ref-id';
            refId.textContent = ` [${node.ref_id}]`;
            wrapper.appendChild(refId);
        }
        
        return wrapper;
    },
    
    /**
     * Toggle directory expand/collapse
     */
    toggleDirectory: function(wrapper, toggle) {
        const children = wrapper.querySelector('.tree-children');
        const isHidden = children.style.display === 'none';
        
        children.style.display = isHidden ? 'block' : 'none';
        toggle.textContent = isHidden ? 
            this.config.icons.expand : this.config.icons.collapse;
    },
    
    /**
     * Handle checkbox change
     */
    handleCheckboxChange: function(event, node) {
        const checkbox = event.target;
        
        if (node.type === 'directory') {
            this.setChildCheckboxes(checkbox.checked, checkbox.closest('.tree-node'));
        }
        
        this.updateParentCheckboxes(checkbox);
        
        if (this.config.onSelectionChange) {
            this.config.onSelectionChange(this.getSelectedPaths());
        }
    },
    
    /**
     * Set all child checkboxes
     */
    setChildCheckboxes: function(checked, node) {
        const checkboxes = node.querySelectorAll('.tree-checkbox');
        checkboxes.forEach(cb => {
            cb.checked = checked;
        });
    },
    
    /**
     * Update parent checkboxes
     */
    updateParentCheckboxes: function(checkbox) {
        let parent = checkbox.closest('.tree-node').parentElement;
        
        while (parent && parent.classList.contains('tree-children')) {
            const parentNode = parent.parentElement;
            const parentCheckbox = parentNode.querySelector(':scope > .tree-directory-header .tree-checkbox');
            
            if (parentCheckbox) {
                const siblings = parent.querySelectorAll(':scope > .tree-node > .tree-checkbox, :scope > .tree-node > .tree-directory-header .tree-checkbox');
                const allChecked = Array.from(siblings).every(cb => cb.checked);
                parentCheckbox.checked = allChecked;
            }
            
            parent = parentNode.parentElement;
        }
    },
    
    /**
     * Get selected file paths
     */
    getSelectedPaths: function() {
        const paths = [];
        const checkboxes = this.container.querySelectorAll('.tree-file .tree-checkbox:checked');
        
        checkboxes.forEach(cb => {
            paths.push(cb.dataset.path);
        });
        
        return paths;
    },
    
    /**
     * Select all files
     */
    selectAll: function(checked) {
        const checkboxes = this.container.querySelectorAll('.tree-checkbox');
        checkboxes.forEach(cb => {
            cb.checked = checked;
        });
        
        if (this.config.onSelectionChange) {
            this.config.onSelectionChange(this.getSelectedPaths());
        }
    },
    
    /**
     * Expand all directories
     */
    expandAll: function() {
        const children = this.container.querySelectorAll('.tree-children');
        const toggles = this.container.querySelectorAll('.tree-toggle');
        
        children.forEach(child => {
            child.style.display = 'block';
        });
        
        toggles.forEach(toggle => {
            toggle.textContent = this.config.icons.expand;
        });
    },
    
    /**
     * Collapse all directories
     */
    collapseAll: function() {
        const children = this.container.querySelectorAll('.tree-children');
        const toggles = this.container.querySelectorAll('.tree-toggle');
        
        children.forEach(child => {
            child.style.display = 'none';
        });
        
        toggles.forEach(toggle => {
            toggle.textContent = this.config.icons.collapse;
        });
    }
};
