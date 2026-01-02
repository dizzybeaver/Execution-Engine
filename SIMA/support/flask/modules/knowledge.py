"""
modules/knowledge.py

Version: 1.0.0
Date: 2025-11-29
Purpose: Knowledge file parsing and conversion
Project: SIMA

ADDED: KnowledgeFile parser
ADDED: JSONToMD converter
"""

from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
import re

from modules.config import Config, LANGUAGE_PATTERNS

class KnowledgeFile:
    """Parse and analyze SIMA knowledge files"""
    
    def __init__(self, path: Path):
        self.path = path
        self.content = path.read_text(encoding='utf-8')
        self.metadata = {}
        self.languages = set()
        self.parse()
    
    def parse(self):
        """Parse MD file and extract metadata"""
        lines = self.content.split('\n')
        
        # Extract metadata from header
        for line in lines[:20]:
            if line.startswith('**Version:**'):
                self.metadata['version'] = line.split('**Version:**')[1].strip()
            elif line.startswith('**Date:**'):
                self.metadata['date'] = line.split('**Date:**')[1].strip()
            elif line.startswith('**Purpose:**'):
                self.metadata['purpose'] = line.split('**Purpose:**')[1].strip()
            elif line.startswith('**Category:**'):
                self.metadata['category'] = line.split('**Category:**')[1].strip()
            elif line.startswith('**REF-ID:**'):
                self.metadata['ref_id'] = line.split('**REF-ID:**')[1].strip()
        
        # Detect languages
        self.languages = self.detect_languages()
    
    def detect_languages(self) -> Set[str]:
        """Detect programming languages from code blocks"""
        detected = set()
        for lang, pattern in LANGUAGE_PATTERNS.items():
            if re.search(pattern, self.content):
                detected.add(lang)
        return detected
    
    def to_json(self) -> Dict:
        """Convert to JSON format"""
        # Extract title from first heading
        title_match = re.search(r'^# (.+)$', self.content, re.MULTILINE)
        title = title_match.group(1) if title_match else self.path.stem
        
        # Extract keywords if present
        keywords_match = re.search(r'\*\*Keywords:\*\* (.+)$', self.content, re.MULTILINE)
        keywords = []
        if keywords_match:
            keywords = [k.strip() for k in keywords_match.group(1).split(',')]
        
        # Extract related refs
        related_match = re.search(r'\*\*Related:\*\* (.+)$', self.content, re.MULTILINE)
        related = []
        if related_match:
            related = [r.strip() for r in related_match.group(1).split(',')]
        
        return {
            "format_version": "1.0.0",
            "sima_version": "4.2.2",
            "title": title,
            "ref_id": self.metadata.get('ref_id', ''),
            "metadata": {
                "version": self.metadata.get('version', '1.0.0'),
                "date": self.metadata.get('date', datetime.now().strftime('%Y-%m-%d')),
                "purpose": self.metadata.get('purpose', ''),
                "category": self.metadata.get('category', ''),
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            },
            "languages": sorted(list(self.languages)),
            "keywords": keywords,
            "related": related,
            "content": {
                "markdown": self.content,
                "sections": self.extract_sections()
            },
            "flags": {
                "has_code": len(self.languages) > 0,
                "line_count": len(self.content.split('\n')),
                "exceeds_limit": len(self.content.split('\n')) > Config.MAX_FILE_LINES
            }
        }
    
    def extract_sections(self) -> List[Dict]:
        """Extract markdown sections"""
        sections = []
        current_section = None
        current_content = []
        
        for line in self.content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections.append({
                        "heading": current_section,
                        "content": '\n'.join(current_content)
                    })
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections.append({
                "heading": current_section,
                "content": '\n'.join(current_content)
            })
        
        return sections


class JSONToMD:
    """Convert JSON format to Markdown"""
    
    @staticmethod
    def convert(data: Dict) -> str:
        """Convert JSON format to MD"""
        md_lines = []
        
        # Title
        md_lines.append(f"# {data['title']}")
        md_lines.append("")
        
        # Metadata
        meta = data['metadata']
        md_lines.append(f"**Version:** {meta.get('version', '1.0.0')}")
        md_lines.append(f"**Date:** {meta.get('date', datetime.now().strftime('%Y-%m-%d'))}")
        md_lines.append(f"**Purpose:** {meta.get('purpose', '')}")
        
        if meta.get('category'):
            md_lines.append(f"**Category:** {meta['category']}")
        
        if data.get('ref_id'):
            md_lines.append(f"**REF-ID:** {data['ref_id']}")
        
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # Content sections
        if 'sections' in data.get('content', {}):
            for section in data['content']['sections']:
                md_lines.append(f"## {section['heading']}")
                md_lines.append("")
                md_lines.append(section['content'])
                md_lines.append("")
        elif 'markdown' in data.get('content', {}):
            # Extract body (skip header)
            content = data['content']['markdown']
            lines = content.split('\n')
            in_header = True
            for line in lines:
                if in_header and line == '---':
                    in_header = False
                    continue
                if not in_header:
                    md_lines.append(line)
        
        # Footer metadata
        if data.get('keywords'):
            md_lines.append("")
            md_lines.append(f"**Keywords:** {', '.join(data['keywords'])}")
        
        if data.get('related'):
            md_lines.append(f"**Related:** {', '.join(data['related'])}")
        
        if data.get('languages'):
            md_lines.append(f"**Languages:** {', '.join(data['languages'])}")
        
        return '\n'.join(md_lines)
