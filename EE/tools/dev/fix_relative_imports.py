"""
Fix Relative Imports to Absolute Imports
Author: CI Repair Cycle
Date: 2026-01-01
Purpose: Convert all relative imports to absolute EE imports for Lambda deployment compliance
"""

import os
import re

def fix_relative_imports(filepath):
    """Convert relative imports to absolute imports in a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Get the module path from file path
    rel_path = os.path.relpath(filepath, 'd:/Code/Project')
    if not rel_path.startswith('EE' + os.sep):
        return False  # Not in EE directory

    # Get the module path (e.g., EE/foundation/config -> EE.foundation.config)
    module_path = rel_path.replace(os.sep, '.').replace('.py', '')

    lines = content.split('\n')
    modified = False
    new_lines = []

    for line in lines:
        new_line = line
        stripped = line.strip()

        # Skip comments and templates
        if stripped.startswith('#') or '{' in stripped:
            new_lines.append(line)
            continue

        # Pattern: from .module.submodule import something (multi-level)
        match = re.match(r'^(\s*)from\s+\.([\w\.]+)\s+import\s+(.*)$', line)
        if match:
            indent, module_path_rel, imports = match.groups()
            # Get parent directory path
            parent_path = '.'.join(module_path.split('.')[:-1])
            absolute_import = f"{indent}from {parent_path}.{module_path_rel} import {imports}"
            new_line = absolute_import
            modified = True

        # Pattern: from ..module.submodule import something (multi-level parent)
        match = re.match(r'^(\s*)from\s+\.\.([\w\.]+)\s+import\s+(.*)$', line)
        if match:
            indent, module_path_rel, imports = match.groups()
            # Get grandparent directory path
            grandparent_path = '.'.join(module_path.split('.')[:-2])
            absolute_import = f"{indent}from {grandparent_path}.{module_path_rel} import {imports}"
            new_line = absolute_import
            modified = True

        # Pattern: from . import module
        match = re.match(r'^(\s*)from\s+\.\s+import\s+(.*)$', line)
        if match:
            indent, imports = match.groups()
            # Get parent directory path
            parent_path = '.'.join(module_path.split('.')[:-1])
            absolute_import = f"{indent}from {parent_path} import {imports}"
            new_line = absolute_import
            modified = True

        new_lines.append(new_line)

    if modified:
        # Write back with CRLF preservation for now
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(new_lines))
        return True

    return False


def main():
    """Main repair function."""
    root_dir = 'd:/Code/Project/EE'

    if not os.path.exists(root_dir):
        print(f"Error: {root_dir} not found")
        return

    repaired_count = 0
    error_count = 0

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in ['.pytest_cache', '__pycache__', '.mypy_cache']]

        for file in files:
            if not file.endswith('.py'):
                continue

            filepath = os.path.join(root, file)

            try:
                if fix_relative_imports(filepath):
                    rel_path = os.path.relpath(filepath, 'd:/Code/Project')
                    print(f"Fixed: {rel_path}")
                    repaired_count += 1
            except Exception as e:
                rel_path = os.path.relpath(filepath, 'd:/Code/Project')
                print(f"Error: {rel_path} - {e}")
                error_count += 1

    print()
    print(f"Repaired: {repaired_count} files")
    print(f"Errors: {error_count} files")


if __name__ == '__main__':
    main()
