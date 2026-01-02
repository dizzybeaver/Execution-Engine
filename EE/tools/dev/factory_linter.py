# factory_linter.py

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "unified_gateway"

REQUIRED_DOCSTRING_SECTIONS = [
    "Factory:",
    "Subsystem:",
    "Purpose:",
]

REQUIRED_METHODS = {
    "factory": ["create"],
    "gateway": ["execute"],
    "operation": ["execute"],
    "serializer": ["dumps", "loads"],
}

def lint_factory(path: Path):
    text = path.read_text()

    errors = []

    # 1. Check docstring sections
    for section in REQUIRED_DOCSTRING_SECTIONS:
        if section not in text:
            errors.append(f"Missing docstring section: {section}")

    # 2. Check required methods
    category = None
    if "class" in text and "Gateway" in text:
        category = "gateway"
    elif "Operation" in text:
        category = "operation"
    elif "Serializer" in text:
        category = "serializer"
    else:
        category = "factory"

    for method in REQUIRED_METHODS[category]:
        if f"def {method}" not in text:
            errors.append(f"Missing required method: {method}")

    return errors


def lint_all_factories():
    failures = {}

    for path in SRC.rglob("*_factory.py"):
        errors = lint_factory(path)
        if errors:
            failures[str(path)] = errors

    return failures


if __name__ == "__main__":
    failures = lint_all_factories()
    if not failures:
        print("All factories pass linting.")
    else:
        print("Factory linting failures:")
        for path, errors in failures.items():
            print(f"\n{path}:")
            for err in errors:
                print(f"  - {err}")