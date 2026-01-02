"""
gateway_wrappers_diagnosis.py
Version: 2025-12-13_1
Purpose: Gateway wrappers for DIAGNOSIS interface (INT-13)
License: Apache 2.0

CHANGES (2025-12-13_1):
- FIXED: Import path from interface.interface_diagnosis
"""

from typing import Any, Dict, List, Callable


def test_module_import(module_name: str, import_func: Callable = None) -> Dict[str, Any]:
    """Test importing a single module."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('test_module_import', module_name=module_name, import_func=import_func)


def test_import_sequence(modules: List[str]) -> Dict[str, Any]:
    """Test importing modules sequentially."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('test_import_sequence', modules=modules)


def format_diagnostic_response(results: List[Dict[str, Any]], message: str) -> Dict[str, Any]:
    """Format diagnostic test results into response structure."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('format_diagnostic_response', results=results, message=message)


def diagnose_import_failure(module_name: str) -> Dict[str, Any]:
    """Diagnose why a module import failed."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('diagnose_import_failure', module_name=module_name)


def diagnose_system_health(**kwargs) -> Dict[str, Any]:
    """Comprehensive system health diagnosis."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('diagnose_system_health', **kwargs)


def diagnose_component_performance(component: str = None, **kwargs) -> Dict[str, Any]:
    """Performance diagnosis for gateway or specific component."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('diagnose_component_performance', component=component, **kwargs)


def diagnose_memory_usage(**kwargs) -> Dict[str, Any]:
    """Memory usage diagnosis."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('diagnose_memory_usage', **kwargs)


def diagnose_initialization_performance(**kwargs) -> Dict[str, Any]:
    """Diagnose INITIALIZATION interface performance patterns."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('diagnose_initialization_performance', **kwargs)


def diagnose_utility_performance(**kwargs) -> Dict[str, Any]:
    """Diagnose UTILITY interface performance patterns."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('diagnose_utility_performance', **kwargs)


def diagnose_singleton_performance(**kwargs) -> Dict[str, Any]:
    """Diagnose SINGLETON interface performance patterns."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('diagnose_singleton_performance', **kwargs)


def validate_system_architecture(**kwargs) -> Dict[str, Any]:
    """Validate SUGA architecture compliance."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('validate_system_architecture', **kwargs)


def validate_imports(**kwargs) -> Dict[str, Any]:
    """Validate no direct imports between modules."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('validate_imports', **kwargs)


def validate_gateway_routing(**kwargs) -> Dict[str, Any]:
    """Validate all gateway routing works."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('validate_gateway_routing', **kwargs)


def run_diagnostic_suite(**kwargs) -> Dict[str, Any]:
    """Run comprehensive diagnostic suite."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('run_diagnostic_suite', **kwargs)


def check_component_health(**kwargs) -> Dict[str, Any]:
    """Check component health."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('check_component_health', **kwargs)


def check_gateway_health(**kwargs) -> Dict[str, Any]:
    """Check gateway health."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('check_gateway_health', **kwargs)


def generate_health_report(**kwargs) -> Dict[str, Any]:
    """Generate comprehensive health report with dispatcher metrics."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('generate_health_report', **kwargs)


def check_initialization_health(**kwargs) -> Dict[str, Any]:
    """Check INITIALIZATION interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('check_initialization_health', **kwargs)


def check_utility_health(**kwargs) -> Dict[str, Any]:
    """Check UTILITY interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('check_utility_health', **kwargs)


def check_singleton_health(**kwargs) -> Dict[str, Any]:
    """Check SINGLETON interface health (AP-08, DEC-04, LESS-17, LESS-18, LESS-21)."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('check_singleton_health', **kwargs)


def check_system_health(**kwargs) -> Dict[str, Any]:
    """Comprehensive system-wide health check for all 14 interfaces."""
    from interface.interface_diagnosis import execute_diagnosis_operation
    return execute_diagnosis_operation('check_system_health', **kwargs)


__all__ = [
    'test_module_import',
    'test_import_sequence',
    'format_diagnostic_response',
    'diagnose_import_failure',
    'diagnose_system_health',
    'diagnose_component_performance',
    'diagnose_memory_usage',
    'diagnose_initialization_performance',
    'diagnose_utility_performance',
    'diagnose_singleton_performance',
    'validate_system_architecture',
    'validate_imports',
    'validate_gateway_routing',
    'run_diagnostic_suite',
    'check_component_health',
    'check_gateway_health',
    'generate_health_report',
    'check_initialization_health',
    'check_utility_health',
    'check_singleton_health',
    'check_system_health'
]
