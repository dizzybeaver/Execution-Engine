"""
sima_manager.py

Version: 1.0.0
Date: 2025-11-29
Purpose: Flask application for SIMA knowledge management (main entry point)
Project: SIMA

MODIFIED: Split into modules to comply with 350-line limit
"""

from flask import Flask
from pathlib import Path

# MODIFIED: Import from modules
from modules.config import Config
from modules.routes import register_routes

app = Flask(__name__)

# ADDED: Initialize directories
Config.EXPORT_DIR.mkdir(exist_ok=True)
Config.ARCHIVE_DIR.mkdir(exist_ok=True)

# ADDED: Register all routes
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# ADDED: Flask routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string('''
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
    ''')

@app.route('/api/tree', methods=['POST'])
def api_tree():
    """Get directory tree"""
    data = request.json
    root_path = Path(data['path'])
    
    if not root_path.exists():
        return jsonify({'error': 'Path does not exist'}), 404
    
    tree = FileBrowser.get_tree(root_path)
    return jsonify(tree)

@app.route('/api/export-selected', methods=['POST'])
def api_export_selected():
    """Export selected files to JSON"""
    data = request.json
    paths = [Path(p) for p in data['paths']]
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Config.EXPORT_DIR / f"sima_export_{timestamp}.json"
    
    export_data = {
        "manifest": {
            "version": "1.0.0",
            "sima_version": "4.2.2",
            "created": datetime.now().isoformat(),
            "file_count": 0
        },
        "files": []
    }
    
    for file_path in paths:
        try:
            kf = KnowledgeFile(file_path)
            json_data = kf.to_json()
            json_data['path'] = str(file_path)
            export_data['files'].append(json_data)
        except Exception as e:
            print(f"Error exporting {file_path}: {e}")
    
    export_data['manifest']['file_count'] = len(export_data['files'])
    
    output_file.write_text(json.dumps(export_data, indent=2), encoding='utf-8')
    
    return jsonify({
        'status': 'success',
        'file_count': export_data['manifest']['file_count'],
        'output_file': str(output_file),
        'filename': output_file.name
    })

@app.route('/api/import-to-target', methods=['POST'])
def api_import_to_target():
    """Import JSON data to target directory"""
    data = request.json
    import_data = data['data']
    target_dir = Path(data['target'])
    update_indexes = data.get('update_indexes', False)
    
    imported = []
    for file_data in import_data['files']:
        try:
            md_content = JSONToMD.convert(file_data)
            
            # MODIFIED: Use filename from path
            filename = Path(file_data['path']).name
            target_path = target_dir / filename
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(md_content, encoding='utf-8')
            imported.append(str(target_path))
        except Exception as e:
            print(f"Error importing {file_data.get('path', 'unknown')}: {e}")
    
    # ADDED: Update indexes if requested
    indexes_updated = False
    if update_indexes and imported:
        try:
            index_content = IndexGenerator.generate(target_dir, f"{target_dir.name} Index")
            index_file = target_dir / f"{target_dir.name}-Index.md"
            index_file.write_text(index_content, encoding='utf-8')
            indexes_updated = True
        except Exception as e:
            print(f"Error updating index: {e}")
    
    return jsonify({
        'status': 'success',
        'imported_count': len(imported),
        'files': imported,
        'target': str(target_dir),
        'indexes_updated': indexes_updated
    })

@app.route('/api/export', methods=['POST'])
def api_export():
    """Export directory to JSON"""
    data = request.json
    source_dir = Path(data['path'])
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Config.EXPORT_DIR / f"sima_export_{timestamp}.json"
    
    manifest = ExportManager.export_to_json(source_dir, output_file)
    
    return jsonify({
        'status': 'success',
        'file_count': manifest['file_count'],
        'output_file': str(output_file),
        'filename': output_file.name
    })

@app.route('/api/import', methods=['POST'])
def api_import():
    """Import JSON file"""
    file = request.files['file']
    target = Path(request.form['target'])
    
    json_file = Config.EXPORT_DIR / file.filename
    file.save(json_file)
    
    imported = ExportManager.import_from_json(json_file, target)
    
    return jsonify({
        'status': 'success',
        'imported_count': len(imported),
        'files': imported
    })

@app.route('/api/index', methods=['POST'])
def api_index():
    """Generate index"""
    data = request.json
    directory = Path(data['path'])
    title = data.get('title', 'Index')
    
    index_content = IndexGenerator.generate(directory, title)
    output_file = directory / f"{directory.name}-Index.md"
    output_file.write_text(index_content, encoding='utf-8')
    
    entry_count = index_content.count('\n- ')
    
    return jsonify({
        'status': 'success',
        'output_file': str(output_file),
        'entry_count': entry_count
    })

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze file"""
    data = request.json
    file_path = Path(data['path'])
    
    kf = KnowledgeFile(file_path)
    
    return jsonify({
        'path': str(file_path),
        'ref_id': kf.metadata.get('ref_id', ''),
        'languages': sorted(list(kf.languages)),
        'line_count': len(kf.content.split('\n')),
        'exceeds_limit': len(kf.content.split('\n')) > Config.MAX_FILE_LINES,
        'metadata': kf.metadata
    })

@app.route('/download/<filename>')
def download(filename):
    """Download exported file"""
    file_path = Config.EXPORT_DIR / filename
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
