"""
modules/routes.py

Version: 1.0.0
Date: 2025-11-29
Purpose: Flask routes for SIMA Manager
Project: SIMA

ADDED: All Flask routes
ADDED: HTML template
"""

from flask import request, jsonify, render_template_string, send_file
from pathlib import Path
from datetime import datetime
import json

from modules.config import Config
from modules.knowledge import KnowledgeFile, JSONToMD
from modules.managers import ExportManager, IndexGenerator, FileBrowser
from modules.templates import HTML_TEMPLATE

def register_routes(app):
    """Register all Flask routes"""
    
    @app.route('/')
    def index():
        """Main dashboard"""
        return render_template_string(HTML_TEMPLATE)
    
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
                
                # Use filename from path
                filename = Path(file_data['path']).name
                target_path = target_dir / filename
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(md_content, encoding='utf-8')
                imported.append(str(target_path))
            except Exception as e:
                print(f"Error importing {file_data.get('path', 'unknown')}: {e}")
        
        # Update indexes if requested
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
