"""
modules/managers.py

Version: 1.0.0
Date: 2025-11-29
Purpose: Export/import managers and utilities
Project: SIMA

ADDED: ExportManager
ADDED: IndexGenerator
ADDED: FileBrowser
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

from modules.config import Config
from modules.knowledge import KnowledgeFile, JSONToMD

class ExportManager:
    """Manage export operations"""
    
    @staticmethod
    def export_to_json(source_dir: Path, output_file: Path):
        """Export knowledge files to JSON archive"""
        export_data = {
            "manifest": {
                "version": "1.0.0",
                "sima_version": "4.2.2",
                "created": datetime.now().isoformat(),
                "source": str(source_dir),
                "file_count": 0
            },
            "files": []
        }
        
        for file_path in source_dir.rglob("*.md"):
            try:
                kf = KnowledgeFile(file_path)
                json_data = kf.to_json()
                json_data['path'] = str(file_path.relative_to(source_dir))
                export_data['files'].append(json_data)
            except Exception as e:
                print(f"Error exporting {file_path}: {e}")
        
        export_data['manifest']['file_count'] = len(export_data['files'])
        
        output_file.write_text(json.dumps(export_data, indent=2), encoding='utf-8')
        return export_data['manifest']
    
    @staticmethod
    def import_from_json(json_file: Path, target_dir: Path):
        """Import JSON archive to MD files"""
        data = json.loads(json_file.read_text(encoding='utf-8'))
        
        imported = []
        for file_data in data['files']:
            try:
                md_content = JSONToMD.convert(file_data)
                target_path = target_dir / file_data['path']
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(md_content, encoding='utf-8')
                imported.append(str(target_path))
            except Exception as e:
                print(f"Error importing {file_data.get('path', 'unknown')}: {e}")
        
        return imported


class IndexGenerator:
    """Generate index files"""
    
    @staticmethod
    def generate(directory: Path, title: str = "Index") -> str:
        """Generate index MD file for directory"""
        md_lines = [
            f"# {title}",
            "",
            f"**Version:** 1.0.0",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
            f"**Purpose:** Auto-generated index",
            "",
            "---",
            ""
        ]
        
        # Group by category
        entries = {}
        for file_path in sorted(directory.rglob("*.md")):
            if file_path.name.endswith('-Index.md'):
                continue
            
            try:
                kf = KnowledgeFile(file_path)
                category = kf.metadata.get('category', 'Uncategorized')
                
                if category not in entries:
                    entries[category] = []
                
                rel_path = file_path.relative_to(directory)
                ref_id = kf.metadata.get('ref_id', '')
                purpose = kf.metadata.get('purpose', '')
                langs = ', '.join(sorted(kf.languages)) if kf.languages else ''
                
                entry = {
                    'path': rel_path,
                    'ref_id': ref_id,
                    'purpose': purpose,
                    'languages': langs
                }
                entries[category].append(entry)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        # Write entries
        for category in sorted(entries.keys()):
            md_lines.append(f"## {category}")
            md_lines.append("")
            
            for entry in entries[category]:
                ref_id = f"[{entry['ref_id']}] " if entry['ref_id'] else ""
                langs = f" `{entry['languages']}`" if entry['languages'] else ""
                md_lines.append(f"- {ref_id}[{entry['path'].stem}]({entry['path']}){langs} - {entry['purpose']}")
            
            md_lines.append("")
        
        md_lines.append("---")
        md_lines.append(f"**Total Files:** {sum(len(e) for e in entries.values())}")
        
        return '\n'.join(md_lines)


class FileBrowser:
    """Browse file system for UI"""
    
    @staticmethod
    def get_tree(root_path: Path) -> Dict:
        """Get directory tree structure"""
        def build_tree(path: Path) -> Dict:
            item = {
                'name': path.name,
                'path': str(path),
                'type': 'directory' if path.is_dir() else 'file'
            }
            
            if path.is_dir():
                children = []
                try:
                    for child in sorted(path.iterdir()):
                        if child.name.startswith('.'):
                            continue
                        children.append(build_tree(child))
                    item['children'] = children
                except PermissionError:
                    item['error'] = 'Permission denied'
            else:
                item['size'] = path.stat().st_size
                if path.suffix == '.md':
                    try:
                        kf = KnowledgeFile(path)
                        item['languages'] = sorted(list(kf.languages))
                        item['ref_id'] = kf.metadata.get('ref_id', '')
                    except:
                        pass
            
            return item
        
        return build_tree(root_path)
