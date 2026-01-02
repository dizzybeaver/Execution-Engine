#!/usr/bin/env python3
"""
Factory Generator Script
------------------------

Creates a new factory module, error class, test stub, and documentation stub
following the Unified Gateway Platform conventions.

Usage:
    python factory_generator.py <subsystem> <factory_name>

Example:
    python factory_generator.py execution retry_policy
"""

import os
import sys
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "unified_gateway"


def create_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"[SKIP] {path} already exists")
        return
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[OK] Created {path}")


def append_to_init(init_path: Path, import_line: str):
    if not init_path.exists():
        init_path.write_text("", encoding="utf-8")

    content = init_path.read_text(encoding="utf-8")
    if import_line in content:
        print(f"[SKIP] {init_path} already contains import")
        return

    with init_path.open("a", encoding="utf-8") as f:
        f.write(import_line + "\n")
    print(f"[OK] Updated {init_path}")


def generate_factory(subsystem: str, factory_name: str):
    subsystem_dir = SRC / subsystem
    if not subsystem_dir.exists():
        print(f"[ERROR] Subsystem '{subsystem}' does not exist.")
        sys.exit(1)

    class_name = "".join(part.capitalize() for part in factory_name.split("_"))
    error_class = f"{class_name}Error"

    # -----------------------------
    # 1. Factory module
    # -----------------------------
    factory_path = subsystem_dir / f"{factory_name}_factory.py"
    factory_content = dedent(f"""
    from dataclasses import dataclass
    from typing import Any
    from .{subsystem}_common import {error_class}

    @dataclass
    class {class_name}:
        \"\"\"Factory: {class_name}
        Auto-generated factory for subsystem '{subsystem}'.
        \"\"\"
        config: dict

        def create(self) -> Any:
            try:
                # TODO: Implement factory logic
                return {{}}
            except Exception as e:
                raise {error_class}(f"Failed to create {{self.__class__.__name__}}: {{e}}") from e


    def create_{factory_name}(**config) -> {class_name}:
        return {class_name}(config=config)
    """)

    create_file(factory_path, factory_content)

    # -----------------------------
    # 2. Error class
    # -----------------------------
    common_path = subsystem_dir / f"{subsystem}_common.py"
    if not common_path.exists():
        common_path.write_text(f"class {error_class}(Exception): pass\n", encoding="utf-8")
        print(f"[OK] Created {common_path}")
    else:
        append_to_init(common_path, f"class {error_class}(Exception): pass")

    # -----------------------------
    # 3. Test stub
    # -----------------------------
    test_dir = SRC / "tests"
    test_path = test_dir / f"test_{factory_name}_factory.py"
    test_content = dedent(f"""
    import unittest
    from unified_gateway.{subsystem}.{factory_name}_factory import create_{factory_name}

    class Test{class_name}Factory(unittest.TestCase):
        def test_create(self):
            factory = create_{factory_name}(example=True)
            result = factory.create()
            self.assertIsInstance(result, dict)

    if __name__ == "__main__":
        unittest.main()
    """)

    create_file(test_path, test_content)

    # -----------------------------
    # 4. Documentation stub
    # -----------------------------
    docs_dir = SRC / "docs"
    doc_path = docs_dir / f"{factory_name}_factory.md"
    doc_content = dedent(f"""
    # {class_name} Factory

    **Subsystem:** `{subsystem}`  
    **Factory:** `{factory_name}`

    ## Purpose
    Auto-generated factory. Fill in the purpose here.

    ## Configuration
    Document configuration options here.

    ## Behavior
    Describe what this factory produces.

    ## Error Handling
    - Raises `{error_class}` on failure.

    ## Tests
    See `tests/test_{factory_name}_factory.py`.
    """)

    create_file(doc_path, doc_content)

    # -----------------------------
    # 5. Update __init__.py
    # -----------------------------
    init_path = subsystem_dir / "__init__.py"
    append_to_init(init_path, f"from .{factory_name}_factory import create_{factory_name}, {class_name}")

    print("\n[DONE] Factory generation complete.")
    print(f"Generated factory: {subsystem}.{factory_name}")
    print("You can now implement the factory logic.")
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python factory_generator.py <subsystem> <factory_name>")
        sys.exit(1)

    subsystem = sys.argv[1]
    factory_name = sys.argv[2]
    generate_factory(subsystem, factory_name)