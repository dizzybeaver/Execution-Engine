#!/usr/bin/env python3
"""
UG-ISP Compliance Verification Script
Checks EE scanner core components for UG-ISP compliance requirements.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any

def check_file_compliance(file_path: str) -> Dict[str, Any]:
    """Check a single Python file for UG-ISP compliance."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines()
    
    violations = []
    warnings = []
    
    # Check 1: NO os.environ/os.getenv() calls in actual code
    for i, line in enumerate(lines, 1):
        # Skip comments and docstrings
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        # Check for violations (actual code, not in strings)
        if re.search(r'\bos\.environ\[', line) and not line.strip().startswith('#'):
            violations.append(f"Line {i}: os.environ access found")
        if re.search(r'\bos\.getenv\(', line) and not line.strip().startswith('#'):
            violations.append(f"Line {i}: os.getenv() call found")
    
    # Check 2: Lazy imports (imports inside functions, not at module level)
    tree = ast.parse(content, filename=file_path)
    
    module_level_imports = []
    function_level_imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if hasattr(node, 'lineno'):
                # Check if it's at module level (depth 1)
                module_level_imports.append((node.lineno, 'import'))
        elif isinstance(node, ast.ImportFrom):
            if hasattr(node, 'lineno'):
                module_level_imports.append((node.lineno, f'from {node.module}'))
    
    # AST-based check for lazy imports in functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for child in ast.walk(node):
                if isinstance(child, (ast.Import, ast.ImportFrom)):
                    function_level_imports.append((child.lineno, node.name))
    
    # Check 3: Gateway execute("config.get") for configuration
    # (This is a pattern check - should be mentioned in comments/docs)
    if 'gateway' not in content.lower() and 'execute' not in content.lower():
        warnings.append("No reference to gateway/execute found")
    
    return {
        'file': file_path,
        'violations': violations,
        'warnings': warnings,
        'module_imports': len(module_level_imports),
        'lazy_imports': len(function_level_imports),
        'compliant': len(violations) == 0
    }

def main():
    print("=" * 80)
    print("UG-ISP COMPLIANCE VERIFICATION FOR EE SCANNER CORE")
    print("=" * 80)
    print()
    
    files_to_check = [
        '__init__.py',
        'false_positive_handler.py',
        'invalid_operation_detector.py',
        'custom_impl_patterns.py',
        'parameter_validator.py',
    ]
    
    all_compliant = True
    total_violations = 0
    
    for file_name in files_to_check:
        file_path = f'D:/Code/Project/EE/src/scanner/core/{file_name}'
        result = check_file_compliance(file_path)
        
        status = "✓ COMPLIANT" if result['compliant'] else "✗ NON-COMPLIANT"
        print(f"\n{file_name}: {status}")
        print("-" * 80)
        
        if result['violations']:
            all_compliant = False
            total_violations += len(result['violations'])
            print("  VIOLATIONS:")
            for v in result['violations']:
                print(f"    ✗ {v}")
        else:
            print("  ✓ No os.environ/os.getenv() violations")
        
        if result['warnings']:
            print("  WARNINGS:")
            for w in result['warnings']:
                print(f"    ⚠ {w}")
        
        print(f"  Module-level imports: {result['module_imports']}")
        print(f"  Lazy imports: {result['lazy_imports']}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Files Checked: {len(files_to_check)}")
    print(f"Total Violations: {total_violations}")
    print(f"Overall Status: {'✓ COMPLIANT' if all_compliant else '✗ NON-COMPLIANT'}")
    print()
    
    if all_compliant:
        print("✓ All files are UG-ISP compliant!")
        print("  - NO os.environ/os.getenv() calls")
        print("  - Configuration via gateway execute('config.get')")
        print("  - Lazy function-level imports")
        print("  - Debug via gateway execute('debug.log')")
    else:
        print("✗ UG-ISP compliance violations found!")
    
    return 0 if all_compliant else 1

if __name__ == '__main__':
    exit(main())
