"""Validate interface router (UG-ISP Router).

Architecture validation operations.

UG-ISP Pattern: Gateway -> Interface (Router) -> Implementation
"""

from typing import Any


def _validate_architecture(path: str = '.') -> dict:
    """Validate UG-ISP architecture compliance.

    Args:
        path: Path to validate

    Returns:
        Validation result dict
    """
    # Delegate to SCAN interface
    from scanner.gateway import execute_operation
    from scanner.gateway.gateway_enums import ScannerInterface

    result = execute_operation(
        ScannerInterface.SCAN,
        'scan',
        path=path,
        report_dir='reports/validation'
    )

    # Determine compliance
    violations = result.get('violations_found', 0)
    critical = sum(1 for v in result.get('violations', [])
                   if v.get('severity') == 'CRITICAL')
    high = sum(1 for v in result.get('violations', [])
               if v.get('severity') == 'HIGH')

    # Architecture compliance requires:
    # - No CRITICAL violations (gateway bypass, cross-interface imports)
    # - No HIGH violations (forbidden imports, debug helpers)
    is_compliant = (critical == 0 and high == 0)

    return {
        'success': True,
        'compliant': is_compliant,
        'violation_count': violations,
        'critical_violations': critical,
        'high_violations': high,
        'compliance_score': max(0, 100 - (critical * 20) - (high * 10)),
        'scan_result': result
    }


def _validate_imports(path: str = '.') -> dict:
    """Validate import patterns only.

    Args:
        path: Path to validate

    Returns:
        Validation result dict
    """
    from scanner.gateway import execute_operation
    from scanner.gateway.gateway_enums import ScannerInterface

    result = execute_operation(
        ScannerInterface.SCAN,
        'scan',
        path=path,
        report_dir='reports/validation/imports'
    )

    # Filter for import violations only
    import_violations = [
        v for v in result.get('violations', [])
        if v.get('violation_type') in [
            'FORBIDDEN_IMPORT',
            'CROSS_INTERFACE_IMPORT'
        ]
    ]

    critical_imports = sum(1 for v in import_violations
                           if v.get('severity') == 'CRITICAL')

    return {
        'success': True,
        'import_compliant': critical_imports == 0,
        'import_violations': len(import_violations),
        'critical_imports': critical_imports,
        'violations': import_violations
    }


def _validate_patterns(path: str = '.') -> dict:
    """Validate against known UG-ISP patterns.

    Args:
        path: Path to validate

    Returns:
        Validation result dict
    """
    from scanner.gateway import execute_operation
    from scanner.gateway.gateway_enums import ScannerInterface

    result = execute_operation(
        ScannerInterface.SCAN,
        'scan',
        path=path,
        report_dir='reports/validation/patterns'
    )

    # Categorize violations by pattern
    violations = result.get('violations', [])

    pattern_violations = {
        'internal_debug_helpers': [
            v for v in violations
            if v.get('violation_type') == 'INTERNAL_DEBUG_HELPER'
        ],
        'gateway_bypass': [
            v for v in violations
            if v.get('violation_type') == 'FORBIDDEN_IMPORT'
            and 'gateway' in v.get('description', '').lower()
        ],
        'cross_interface': [
            v for v in violations
            if v.get('violation_type') == 'CROSS_INTERFACE_IMPORT'
        ],
        'interface_imports': [
            v for v in violations
            if v.get('description', '').startswith('Direct interface import')
        ]
    }

    # Pattern compliance check
    pattern_compliance = {
        pattern: len(violations_list) == 0
        for pattern, violations_list in pattern_violations.items()
    }

    return {
        'success': True,
        'patterns_compliant': all(pattern_compliance.values()),
        'pattern_compliance': pattern_compliance,
        'pattern_violations': {
            pattern: len(violations_list)
            for pattern, violations_list in pattern_violations.items()
        },
        'violations_by_pattern': pattern_violations
    }


# Dispatch dictionary - O(1) operation routing
_VALIDATE_DISPATCH = {
    'architecture': lambda **kw: _validate_architecture(kw.get('path', '.')),
    'imports': lambda **kw: _validate_imports(kw.get('path', '.')),
    'patterns': lambda **kw: _validate_patterns(kw.get('path', '.')),
}


def execute_validate_operation(operation: str, **kwargs) -> Any:
    """Route validate operation requests.

    Args:
        operation: Operation name (architecture, imports, patterns)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation unknown
    """
    if operation not in _VALIDATE_DISPATCH:
        raise ValueError(
            f"Unknown validate operation: '{operation}'. "
            f"Valid: {', '.join(_VALIDATE_DISPATCH.keys())}"
        )

    handler = _VALIDATE_DISPATCH[operation]
    return handler(**kwargs)


__all__ = ['execute_validate_operation']
