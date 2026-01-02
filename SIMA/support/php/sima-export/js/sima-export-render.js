/**
 * sima-export-render.js
 * 
 * Tree rendering functionality
 * Version: 4.3.1
 * Date: 2025-11-23
 * Location: /support/php/js/
 */

/**
 * Render knowledge tree
 */
function renderTree() {
    const container = document.getElementById('tree');
    container.innerHTML = '';
    
    if (!window.knowledgeTree || window.knowledgeTree.length === 0) {
        container.innerHTML = '<p>No files found</p>';
        return;
    }
    
    window.knowledgeTree.forEach(node => {
        container.appendChild(renderNode(node, 0));
    });
}

/**
 * Render individual tree node
 */
function renderNode(node, depth) {
    const div = document.createElement('div');
    div.style.marginLeft = (depth * 20) + 'px';
    div.style.padding = '5px';
    
    if (node.type === 'directory') {
        const label = document.createElement('div');
        label.style.cursor = 'pointer';
        label.style.fontWeight = 'bold';
        label.style.padding = '5px';
        label.style.background = '#f0f0f0';
        label.style.marginBottom = '5px';
        label.style.borderRadius = '3px';
        
        const toggle = document.createElement('span');
        toggle.textContent = '▼ ';
        label.appendChild(toggle);
        
        const name = document.createElement('span');
        name.textContent = `📁 ${node.name} (${node.total_files} files)`;
        label.appendChild(name);
        div.appendChild(label);
        
        const childrenDiv = document.createElement('div');
        if (node.children) {
            node.children.forEach(child => {
                childrenDiv.appendChild(renderNode(child, depth + 1));
            });
        }
        div.appendChild(childrenDiv);
        
        // Toggle expand/collapse
        label.onclick = () => {
            const isHidden = childrenDiv.style.display === 'none';
            childrenDiv.style.display = isHidden ? 'block' : 'none';
            toggle.textContent = isHidden ? '▼ ' : '▶ ';
        };
    } else {
        // File node
        const label = document.createElement('label');
        label.style.display = 'block';
        label.style.padding = '3px';
        label.style.cursor = 'pointer';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = node.path;
        checkbox.checked = window.selectedFiles.has(node.path);
        checkbox.onchange = () => {
            if (checkbox.checked) {
                window.selectedFiles.add(node.path);
            } else {
                window.selectedFiles.delete(node.path);
            }
            updateSummary();
        };
        
        label.appendChild(checkbox);
        label.appendChild(document.createTextNode(` 📄 ${node.name}`));
        
        if (node.ref_id) {
            const refId = document.createElement('span');
            refId.textContent = ` [${node.ref_id}]`;
            refId.style.color = '#666';
            refId.style.fontSize = '0.9em';
            label.appendChild(refId);
        }
        
        div.appendChild(label);
    }
    
    return div;
}
