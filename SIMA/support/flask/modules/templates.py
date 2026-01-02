"""
modules/templates.py

Version: 1.0.0
Date: 2025-11-29
Purpose: HTML templates for SIMA Manager
Project: SIMA

ADDED: Main HTML template with all UI
"""

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SIMA Knowledge Manager</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        h1 { color: #333; margin-bottom: 10px; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #ddd; }
        .tab { padding: 10px 20px; cursor: pointer; background: #f0f0f0; border: none; }
        .tab.active { background: #007bff; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .split-view { display: flex; gap: 20px; }
        .tree-panel { flex: 1; background: #f9f9f9; padding: 15px; border-radius: 4px; max-height: 600px; overflow-y: auto; }
        .selection-panel { flex: 1; background: #f9f9f9; padding: 15px; border-radius: 4px; }
        .tree-item { margin-left: 20px; cursor: pointer; user-select: none; }
        .tree-folder { font-weight: bold; color: #333; }
        .tree-folder::before { content: '📁 '; }
        .tree-file { color: #666; }
        .tree-file::before { content: '📄 '; }
        .tree-file.selected { background: #e7f3ff; }
        .button { 
            background: #007bff; color: white; padding: 10px 20px; 
            border: none; border-radius: 4px; cursor: pointer; margin: 5px;
        }
        .button:hover { background: #0056b3; }
        .button.secondary { background: #6c757d; }
        .button.success { background: #28a745; }
        input[type="text"] { padding: 8px; margin: 5px; width: 300px; }
        .result { margin-top: 15px; padding: 10px; background: #e7f3ff; border-radius: 4px; }
        .language-tag { 
            display: inline-block; padding: 2px 6px; margin: 2px; 
            background: #28a745; color: white; border-radius: 3px; font-size: 11px;
        }
        .selected-list { max-height: 400px; overflow-y: auto; }
        .selected-item { padding: 8px; margin: 5px 0; background: white; border-radius: 3px; display: flex; justify-content: space-between; align-items: center; }
        .remove-btn { background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 3px; cursor: pointer; }
        .stats { background: #fff3cd; padding: 10px; border-radius: 4px; margin: 10px 0; }
        .collapse-toggle { cursor: pointer; }
        .section { margin: 30px 0; padding: 20px; background: #f9f9f9; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🗂️ SIMA Knowledge Manager</h1>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('export')">Export</button>
            <button class="tab" onclick="showTab('import')">Import</button>
            <button class="tab" onclick="showTab('tools')">Tools</button>
        </div>
        
        <div id="export-tab" class="tab-content active">
            <h2>📤 Export Files</h2>
            <div class="split-view">
                <div class="tree-panel">
                    <h3>Browse Files</h3>
                    <input type="text" id="export-root" placeholder="Root path (e.g., ./sima)" value="./sima" />
                    <button class="button" onclick="loadExportTree()">Load</button>
                    <div id="export-tree" style="margin-top: 15px;"></div>
                </div>
                <div class="selection-panel">
                    <h3>Selected Files (<span id="export-count">0</span>)</h3>
                    <div class="stats">
                        <strong>Total size:</strong> <span id="export-size">0 KB</span><br>
                        <strong>Languages:</strong> <span id="export-langs">None</span>
                    </div>
                    <div class="selected-list" id="export-selected"></div>
                    <button class="button success" onclick="exportSelected()">Export Selected</button>
                    <button class="button secondary" onclick="clearExportSelection()">Clear All</button>
                    <div id="export-result" class="result" style="display:none;"></div>
                </div>
            </div>
        </div>
        
        <div id="import-tab" class="tab-content">
            <h2>📥 Import Files</h2>
            <div class="split-view">
                <div class="tree-panel">
                    <h3>Import Source</h3>
                    <input type="file" id="import-file" accept=".json" onchange="loadImportPreview()" />
                    <div id="import-preview" style="margin-top: 15px;"></div>
                </div>
                <div class="selection-panel">
                    <h3>Import Destination</h3>
                    <input type="text" id="import-root" placeholder="Root path (e.g., ./sima)" value="./sima" />
                    <button class="button" onclick="loadImportTree()">Browse</button>
                    <div id="import-tree" style="margin-top: 15px;"></div>
                    <div class="stats" style="margin-top: 15px;">
                        <strong>Target:</strong> <span id="import-target">Not selected</span>
                    </div>
                    <button class="button success" onclick="importToSelected()">Import to Selected</button>
                    <label><input type="checkbox" id="update-indexes" checked /> Update indexes after import</label>
                    <div id="import-result" class="result" style="display:none;"></div>
                </div>
            </div>
        </div>
        
        <div id="tools-tab" class="tab-content">
            <h2>🔧 Tools</h2>
            <div class="section">
                <h3>Generate Index</h3>
                <input type="text" id="index-path" placeholder="Directory path" />
                <input type="text" id="index-title" placeholder="Index title" value="Index" />
                <button class="button" onclick="generateIndex()">Generate</button>
                <div id="index-result" class="result" style="display:none;"></div>
            </div>
            
            <div class="section" style="margin-top: 20px;">
                <h3>Analyze File</h3>
                <input type="text" id="analyze-path" placeholder="File path" />
                <button class="button" onclick="analyzeFile()">Analyze</button>
                <div id="analyze-result" class="result" style="display:none;"></div>
            </div>
        </div>
    </div>
    
    <script>
        let exportSelection = new Set();
        let importPreviewData = null;
        let importTargetPath = null;
        
        function showTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
        }
        
        async function loadExportTree() {
            const path = document.getElementById('export-root').value;
            const response = await fetch('/api/tree', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: path})
            });
            const tree = await response.json();
            renderTree(tree, 'export-tree', true);
        }
        
        async function loadImportTree() {
            const path = document.getElementById('import-root').value;
            const response = await fetch('/api/tree', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: path})
            });
            const tree = await response.json();
            renderTree(tree, 'import-tree', false);
        }
        
        async function loadImportPreview() {
            const file = document.getElementById('import-file').files[0];
            const reader = new FileReader();
            reader.onload = (e) => {
                importPreviewData = JSON.parse(e.target.result);
                const div = document.getElementById('import-preview');
                div.innerHTML = `
                    <div class="stats">
                        <strong>Files:</strong> ${importPreviewData.files.length}<br>
                        <strong>Version:</strong> ${importPreviewData.manifest.sima_version}<br>
                        <strong>Created:</strong> ${new Date(importPreviewData.manifest.created).toLocaleString()}
                    </div>
                    <div style="max-height: 400px; overflow-y: auto;">
                        ${importPreviewData.files.map(f => `
                            <div style="padding: 5px; margin: 3px 0; background: white; border-radius: 3px;">
                                📄 ${f.path}
                                ${f.languages.map(l => '<span class="language-tag">' + l + '</span>').join('')}
                            </div>
                        `).join('')}
                    </div>
                `;
            };
            reader.readAsText(file);
        }
        
        function renderTree(node, containerId, selectable) {
            const container = document.getElementById(containerId);
            container.innerHTML = renderNode(node, selectable);
        }
        
        function renderNode(node, selectable, level = 0) {
            if (node.type === 'file') {
                const langs = node.languages ? node.languages.map(l => 
                    '<span class="language-tag">' + l + '</span>'
                ).join('') : '';
                const refId = node.ref_id ? '[' + node.ref_id + '] ' : '';
                
                if (selectable) {
                    const selected = exportSelection.has(node.path) ? 'selected' : '';
                    return `<div class="tree-item tree-file ${selected}" onclick="toggleExportFile('${node.path}', ${node.size})">
                        ${refId}${node.name} ${langs}
                    </div>`;
                } else {
                    return `<div class="tree-item tree-file">${refId}${node.name} ${langs}</div>`;
                }
            } else {
                const childrenHtml = node.children ? node.children.map(c => 
                    renderNode(c, selectable, level + 1)
                ).join('') : '';
                
                const onClick = selectable ? '' : `onclick="selectImportTarget('${node.path}')"`;
                
                return `
                    <div>
                        <div class="tree-item tree-folder collapse-toggle" onclick="toggleFolder(event)">
                            ${node.name}
                        </div>
                        <div class="tree-children" ${onClick}>
                            ${childrenHtml}
                        </div>
                    </div>
                `;
            }
        }
        
        function toggleFolder(e) {
            e.stopPropagation();
            const children = e.target.nextElementSibling;
            children.style.display = children.style.display === 'none' ? 'block' : 'none';
        }
        
        function toggleExportFile(path, size) {
            if (exportSelection.has(path)) {
                exportSelection.delete(path);
            } else {
                exportSelection.add(path);
            }
            updateExportSelection();
            loadExportTree();
        }
        
        function selectImportTarget(path) {
            importTargetPath = path;
            document.getElementById('import-target').textContent = path;
        }
        
        function updateExportSelection() {
            const div = document.getElementById('export-selected');
            const paths = Array.from(exportSelection);
            
            div.innerHTML = paths.map(path => `
                <div class="selected-item">
                    <span>📄 ${path.split('/').pop()}</span>
                    <button class="remove-btn" onclick="removeExportFile('${path}')">Remove</button>
                </div>
            `).join('');
            
            document.getElementById('export-count').textContent = paths.length;
        }
        
        function removeExportFile(path) {
            exportSelection.delete(path);
            updateExportSelection();
            loadExportTree();
        }
        
        function clearExportSelection() {
            exportSelection.clear();
            updateExportSelection();
            loadExportTree();
        }
        
        async function exportSelected() {
            const paths = Array.from(exportSelection);
            if (paths.length === 0) {
                alert('No files selected');
                return;
            }
            
            const response = await fetch('/api/export-selected', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({paths: paths})
            });
            const result = await response.json();
            const div = document.getElementById('export-result');
            div.style.display = 'block';
            div.innerHTML = `<strong>✅ Exported:</strong> ${result.file_count} files<br>
                            <strong>Output:</strong> ${result.output_file}<br>
                            <a href="/download/${result.filename}" class="button">Download</a>`;
        }
        
        async function importToSelected() {
            if (!importPreviewData) {
                alert('No import file selected');
                return;
            }
            if (!importTargetPath) {
                alert('No target directory selected');
                return;
            }
            
            const updateIndexes = document.getElementById('update-indexes').checked;
            
            const response = await fetch('/api/import-to-target', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    data: importPreviewData,
                    target: importTargetPath,
                    update_indexes: updateIndexes
                })
            });
            const result = await response.json();
            const div = document.getElementById('import-result');
            div.style.display = 'block';
            div.innerHTML = `<strong>✅ Imported:</strong> ${result.imported_count} files<br>
                            ${result.indexes_updated ? '<strong>✅ Indexes updated</strong><br>' : ''}
                            <strong>Target:</strong> ${result.target}`;
        }
        
        async function generateIndex() {
            const path = document.getElementById('index-path').value;
            const title = document.getElementById('index-title').value;
            const response = await fetch('/api/index', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: path, title: title})
            });
            const result = await response.json();
            const div = document.getElementById('index-result');
            div.style.display = 'block';
            div.innerHTML = `<strong>✅ Generated:</strong> ${result.output_file}<br>
                            <strong>Entries:</strong> ${result.entry_count}`;
        }
        
        async function analyzeFile() {
            const path = document.getElementById('analyze-path').value;
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({path: path})
            });
            const result = await response.json();
            const div = document.getElementById('analyze-result');
            div.style.display = 'block';
            
            const langs = result.languages.map(l => 
                `<span class="language-tag">${l}</span>`
            ).join('');
            
            div.innerHTML = `
                <strong>File:</strong> ${result.path}<br>
                <strong>REF-ID:</strong> ${result.ref_id || 'None'}<br>
                <strong>Languages:</strong> ${langs || 'None detected'}<br>
                <strong>Lines:</strong> ${result.line_count}<br>
                <strong>Exceeds Limit:</strong> ${result.exceeds_limit ? '⚠️ Yes' : '✅ No'}
            `;
        }
    </script>
</body>
</html>
'''
