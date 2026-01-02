#!/usr/bin/env python
"""Find missing __init__.py files."""

import pathlib

ee_root = pathlib.Path('D:/Code/LEE/EE')
missing = []

for py_file in ee_root.rglob('*.py'):
    package_dir = py_file.parent
    init_file = package_dir / '__init__.py'
    if not init_file.exists() and package_dir != ee_root:
        rel_path = init_file.relative_to(ee_root)
        if str(rel_path) not in missing:
            missing.append(str(rel_path))

if missing:
    print(f"Found {len(missing)} missing __init__.py files:")
    for m in sorted(missing):
        print(f"  - {m}")
else:
    print("All packages have __init__.py files")
