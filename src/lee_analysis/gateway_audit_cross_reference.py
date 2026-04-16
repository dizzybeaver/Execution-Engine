#!/usr/bin/env python3
"""Gateway Audit: Cross-reference declared operations with actual implementations.

Finds all declared operations in LEE and HA gateway interface routers
and verifies the target functions actually exist in implementation files.

Outputs a comprehensive report of missing implementations.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def extract_imports_from_source(source: str) -> List[Tuple[str, str, str]]:
    """Extract import statements from Python source code.

    Returns:
        List of (module_path, import_name, local_name) tuples
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, alias.name, alias.asname or alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append((module, alias.name, alias.asname or alias.name))

    return imports


def extract_dispatch_dict_from_interface(source: str, _filepath: Path) -> Dict[str, str]:
    """Extract dispatch dictionary from interface router file.

    Returns:
        Dict mapping {operation_name: target_function_name}
    """
    operations = {}

    # Pattern 1: LEE Gateway - nested dict format
    # "operation": {"func": _target_func, ...}
    pattern1 = re.compile(
        r'["\']([\w_]+)["\']\s*:\s*\{[^}]*"func"\s*:\s*([\w_]+)',
        re.MULTILINE
    )

    # Pattern 2: HA Gateway - simple format
    # "operation": _target_func
    pattern2 = re.compile(
        r'["\']([\w_]+)["\']\s*:\s*_?([\w_]+)[,\n]',
        re.MULTILINE
    )

    # Find all dispatch dictionaries
    dispatch_vars = re.findall(
        r'(\w[\w_]*)\s*=\s*\{',
        source
    )

    # Try to extract dispatch dictionary content
    for var_name in dispatch_vars:
        # Look for the dictionary assignment
        dict_match = re.search(
            rf'{var_name}\s*=\s*\{{(.*?)\n\}}',
            source,
            re.DOTALL
        )
        if dict_match:
            dict_content = dict_match.group(1)

            # Extract operations using both patterns
            for match in pattern1.finditer(dict_content):
                op_name, target_func = match.groups()
                operations[op_name] = target_func

            for match in pattern2.finditer(dict_content):
                op_name, target_func = match.groups()
                # Skip if it's a keyword or already found
                if target_func not in ['func', 'category', 'description', 'lambda']:
                    operations[op_name] = target_func

    return operations


def find_function_in_file(source: str, func_name: str) -> bool:
    """Check if a function is defined in the given source code."""
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == func_name:
                    # Check if it's a stub
                    if (len(node.body) == 1 and
                        isinstance(node.body[0], (ast.Pass, ast.Raise))):
                        return False  # Stub found
                    return True  # Real function found
            elif isinstance(node, ast.AsyncFunctionDef):
                if node.name == func_name:
                    if (len(node.body) == 1 and
                        isinstance(node.body[0], (ast.Pass, ast.Raise))):
                        return False
                    return True
        return False
    except SyntaxError:
        return False


def audit_lee_gateway(project_root: Path) -> Dict[str, List[Dict]]:
    """Audit LEE gateway for missing implementations.

    Returns:
        Dict with 'missing', 'stubs', and 'found' lists
    """
    # pylint: disable=too-many-branches,too-many-locals,too-many-nested-blocks
    results = {
        'missing': [],
        'stubs': [],
        'found': [],
        'errors': []
    }

    # Scan LEE interface router files
    interface_dir = project_root / 'interface'
    interface_files = list(interface_dir.glob('interface_*.py'))

    for interface_file in interface_files:
        try:
            source = interface_file.read_text(encoding='utf-8')
            operations = extract_dispatch_dict_from_interface(source, interface_file)

            # Extract imports to find where functions should be
            imports = extract_imports_from_source(source)

            # Build import mapping
            import_map = {}
            for module_path, import_name, local_name in imports:
                import_map[local_name] = (module_path, import_name)

            # Check each operation's target function
            for op_name, target_func in operations.items():
                # Skip lambda functions (inline implementations)
                if 'lambda' in str(target_func):
                    results['found'].append({
                        'interface': interface_file.name,
                        'operation': op_name,
                        'target': 'lambda (inline)',
                        'status': 'inline'
                    })
                    continue

                # Find the target function in imports or implementation files
                func_found = False
                is_stub = False

                # Check if target is in import map
                if target_func in import_map:
                    module_path, import_name = import_map[target_func]

                    # Convert module path to file path
                    if module_path.startswith('interface.wrappers'):
                        # Validate module_path before using
                        if not module_path:
                            # Skip empty module paths
                            continue
                        module_name = module_path.split('.')[-1]
                        if not module_name:
                            # Handle edge case where split returns empty
                            continue
                        wrapper_file = project_root / 'interface' / 'wrappers' / f"{module_name}.py"
                        if wrapper_file.exists():
                            wrapper_source = wrapper_file.read_text(encoding='utf-8')
                            if find_function_in_file(wrapper_source, import_name):
                                func_found = True
                            elif import_name in wrapper_source:  # Exists but might be stub
                                is_stub = True
                else:
                    # Search in wrapper files
                    wrapper_dir = project_root / 'interface' / 'wrappers'
                    for wrapper_file in wrapper_dir.glob('*.py'):
                        wrapper_source = wrapper_file.read_text(encoding='utf-8')
                        if find_function_in_file(wrapper_source, target_func):
                            func_found = True
                            break
                        if target_func in wrapper_source:
                            is_stub = True

                if func_found:
                    results['found'].append({
                        'interface': interface_file.name,
                        'operation': op_name,
                        'target': target_func,
                        'status': 'found'
                    })
                elif is_stub:
                    results['stubs'].append({
                        'interface': interface_file.name,
                        'operation': op_name,
                        'target': target_func,
                        'status': 'stub'
                    })
                else:
                    results['missing'].append({
                        'interface': interface_file.name,
                        'operation': op_name,
                        'target': target_func,
                        'status': 'missing'
                    })

        except (OSError, UnicodeDecodeError, ValueError) as e:
            results['errors'].append({
                'file': interface_file.name,
                'error': str(e)
            })

    return results


def audit_ha_gateway(project_root: Path) -> Dict[str, List[Dict]]:
    """Audit HA-SUGA gateway for missing implementations.

    Returns:
        Dict with 'missing', 'stubs', and 'found' lists
    """
    # pylint: disable=too-many-branches,too-many-locals,too-many-nested-blocks
    results = {
        'missing': [],
        'stubs': [],
        'found': [],
        'errors': []
    }

    # Scan HA interface router files
    interface_dir = project_root / 'home_assistant' / 'interface'
    interface_files = list(interface_dir.glob('ha_*.py'))

    for interface_file in interface_files:
        # Skip wrapper files
        if 'wrappers' in str(interface_file):
            continue

        try:
            source = interface_file.read_text(encoding='utf-8')
            operations = extract_dispatch_dict_from_interface(source, interface_file)

            # Extract imports
            imports = extract_imports_from_source(source)

            # Build import mapping
            import_map = {}
            for module_path, import_name, local_name in imports:
                import_map[local_name] = (module_path, import_name)

            # Check each operation's target function
            for op_name, target_func in operations.items():
                func_found = False
                is_stub = False

                # Check if target is in import map
                if target_func in import_map:
                    module_path, import_name = import_map[target_func]

                    # Convert to file path
                    if 'wrappers' in module_path:
                        # Search in wrapper files
                        wrapper_dir = project_root / 'home_assistant' / 'interface' / 'wrappers'
                        wrapper_file = wrapper_dir / f"{module_path.split('.')[-1]}.py"
                        if wrapper_file.exists():
                            wrapper_source = wrapper_file.read_text(encoding='utf-8')
                            if find_function_in_file(wrapper_source, import_name):
                                func_found = True
                            elif import_name in wrapper_source:
                                is_stub = True
                    else:
                        # Search in core files
                        ha_dir = project_root / 'home_assistant'
                        for core_file in ha_dir.rglob('*.py'):
                            if 'core' in core_file.name:
                                core_source = core_file.read_text(encoding='utf-8')
                                if find_function_in_file(core_source, import_name):
                                    func_found = True
                                    break
                                if import_name in core_source:
                                    is_stub = True

                if func_found:
                    results['found'].append({
                        'interface': interface_file.name,
                        'operation': op_name,
                        'target': target_func,
                        'status': 'found'
                    })
                elif is_stub:
                    results['stubs'].append({
                        'interface': interface_file.name,
                        'operation': op_name,
                        'target': target_func,
                        'status': 'stub'
                    })
                else:
                    results['missing'].append({
                        'interface': interface_file.name,
                        'operation': op_name,
                        'target': target_func,
                        'status': 'missing'
                    })

        except (OSError, UnicodeDecodeError, ValueError) as e:
            results['errors'].append({
                'file': interface_file.name,
                'error': str(e)
            })

    return results


def generate_report(lee_results: Dict, ha_results: Dict) -> str:
    """Generate comprehensive audit report."""
    # pylint: disable=too-many-statements
    report = []
    report.append("=" * 80)
    report.append("GATEWAY AUDIT REPORT: Missing Implementations")
    report.append("=" * 80)
    report.append("")

    # LEE Gateway Summary
    report.append("## LEE Gateway Summary")
    report.append(f"  - Found:    {len(lee_results['found'])} operations")
    report.append(f"  - Stubs:    {len(lee_results['stubs'])} operations")
    report.append(f"  - Missing:  {len(lee_results['missing'])} operations")
    report.append(f"  - Errors:   {len(lee_results['errors'])} files")
    report.append("")

    # HA Gateway Summary
    report.append("## HA-SUGA Gateway Summary")
    report.append(f"  - Found:    {len(ha_results['found'])} operations")
    report.append(f"  - Stubs:    {len(ha_results['stubs'])} operations")
    report.append(f"  - Missing:  {len(ha_results['missing'])} operations")
    report.append(f"  - Errors:   {len(ha_results['errors'])} files")
    report.append("")

    # Missing Implementations - LEE
    if lee_results['missing']:
        report.append("## LEE Gateway: MISSING IMPLEMENTATIONS")
        report.append("")
        for item in lee_results['missing']:
            report.append(f"  {item['interface']}:")
            report.append(f"    Operation: {item['operation']}")
            report.append(f"    Target:    {item['target']}")
            report.append("")

    # Missing Implementations - HA
    if ha_results['missing']:
        report.append("## HA-SUGA Gateway: MISSING IMPLEMENTATIONS")
        report.append("")
        for item in ha_results['missing']:
            report.append(f"  {item['interface']}:")
            report.append(f"    Operation: {item['operation']}")
            report.append(f"    Target:    {item['target']}")
            report.append("")

    # Stub Implementations - LEE
    if lee_results['stubs']:
        report.append("## LEE Gateway: STUB IMPLEMENTATIONS")
        report.append("")
        for item in lee_results['stubs']:
            report.append(f"  {item['interface']}:")
            report.append(f"    Operation: {item['operation']}")
            report.append(f"    Target:    {item['target']}")
            report.append("")

    # Stub Implementations - HA
    if ha_results['stubs']:
        report.append("## HA-SUGA Gateway: STUB IMPLEMENTATIONS")
        report.append("")
        for item in ha_results['stubs']:
            report.append(f"  {item['interface']}:")
            report.append(f"    Operation: {item['operation']}")
            report.append(f"    Target:    {item['target']}")
            report.append("")

    # Errors
    if lee_results['errors'] or ha_results['errors']:
        report.append("## ERRORS")
        report.append("")
        for error in lee_results['errors'] + ha_results['errors']:
            report.append(f"  {error['file']}: {error['error']}")
            report.append("")

    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)

    return "\n".join(report)


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent

    print(f"Auditing LEE gateway at: {project_root}")
    print("")

    # Audit LEE Gateway
    print("Auditing LEE Gateway...")
    lee_results = audit_lee_gateway(project_root)
    print(f"  Found: {len(lee_results['found'])} operations")
    print(f"  Stubs: {len(lee_results['stubs'])} operations")
    print(f"  Missing: {len(lee_results['missing'])} operations")
    print("")

    # Audit HA Gateway
    print("Auditing HA-SUGA Gateway...")
    ha_results = audit_ha_gateway(project_root)
    print(f"  Found: {len(ha_results['found'])} operations")
    print(f"  Stubs: {len(ha_results['stubs'])} operations")
    print(f"  Missing: {len(ha_results['missing'])} operations")
    print("")

    # Generate report
    report = generate_report(lee_results, ha_results)

    # Save report
    report_file = project_root / 'gateway_audit_report.txt'
    report_file.write_text(report, encoding='utf-8')
    print(f"Report saved to: {report_file}")
    print("")

    # Exit code
    total_missing = len(lee_results['missing']) + len(ha_results['missing'])
    total_stubs = len(lee_results['stubs']) + len(ha_results['stubs'])

    if total_missing > 0:
        print(f"WARNING: Found {total_missing} missing implementations!")
        sys.exit(1)
    elif total_stubs > 0:
        print(f"WARNING: Found {total_stubs} stub implementations!")
        sys.exit(2)
    else:
        print("SUCCESS: All operations have implementations!")
        sys.exit(0)


if __name__ == '__main__':
    main()
