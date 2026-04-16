"""interface/interface_diagnosis.py
Version: 2025-12-08_2
Purpose: DIAGNOSIS interface router (INT-13) with Static DDS pattern
License: Apache 2.0

CHANGES (2025-12-08_2):
- Converted to Static Dictionary Dispatch System (DDS-1)
- Added metadata (func, category, description) for each operation
- Zero breaking changes - all existing operations preserved
"""

from collections.abc import Callable
from typing import Any

from lee.interface.interface_common import validate_module_available

_DIAGNOSIS_AVAILABLE = True
_DIAGNOSIS_IMPORT_ERROR = None

try:
    from lee.diagnosis import (
        check_component_health,
        check_gateway_health,
        check_initialization_health,
        check_singleton_health,
        check_system_health,
        check_utility_health,
        diagnose_component_performance,
        diagnose_import_failure,
        diagnose_initialization_performance,
        diagnose_memory_usage,
        diagnose_singleton_performance,
        diagnose_system_health,
        diagnose_utility_performance,
        format_diagnostic_response,
        generate_health_report,
        run_diagnostic_suite,
        test_import_sequence,
        test_module_import,
        validate_gateway_routing,
        validate_imports,
        validate_system_architecture,
    )
    from lee.diagnosis.health.health_checker import (
        _clear_health_status_implementation,
        _execute_all_health_checks_implementation,
        _execute_health_check_implementation,
        _get_health_status_implementation,
        _list_health_checks_implementation,
        _register_health_check_implementation,
        _unregister_health_check_implementation,
    )
    # Error tracker imports (will be moved from singleton/ to diagnosis/)
    try:
        from lee.singleton.error_tracker import (
            error_tracker_get_patterns,
            error_tracker_get_summary,
            error_tracker_record_error,
            error_tracker_reset,
        )
        _ERROR_TRACKER_AVAILABLE = True
    except (ImportError, ModuleNotFoundError):
        # Error tracker not yet moved to diagnosis/ - create stubs
        _ERROR_TRACKER_AVAILABLE = False

        def error_tracker_record_error(**kwargs):  # pylint: disable=unused-argument
            """Stub for error tracker record error when not yet available."""
            return {"error": "Error tracker not yet available"}

        def error_tracker_get_patterns(**kwargs):  # pylint: disable=unused-argument
            """Stub for error tracker get patterns when not yet available."""
            return []

        def error_tracker_get_summary(**kwargs):  # pylint: disable=unused-argument
            """Stub for error tracker get summary when not yet available."""
            return {"total_occurrences": 0, "total_patterns": 0}

        def error_tracker_reset(**kwargs):  # pylint: disable=unused-argument
            """Stub for error tracker reset when not yet available - no-op."""
            return {"status": "stub", "message": "Error tracker not yet available"}
except ImportError as e:
    _DIAGNOSIS_AVAILABLE = False
    _DIAGNOSIS_IMPORT_ERROR = str(e)
    _ERROR_TRACKER_AVAILABLE = False

    # Create stubs for when DIAGNOSIS is unavailable
    def error_tracker_record_error(**kwargs):  # pylint: disable=unused-argument
        """Stub for error tracker when DIAGNOSIS unavailable."""
        raise RuntimeError(f"DIAGNOSIS unavailable: {_DIAGNOSIS_IMPORT_ERROR}")

    def error_tracker_get_patterns(**kwargs):  # pylint: disable=unused-argument
        """Stub for error tracker when DIAGNOSIS unavailable."""
        raise RuntimeError(f"DIAGNOSIS unavailable: {_DIAGNOSIS_IMPORT_ERROR}")

    def error_tracker_get_summary(**kwargs):  # pylint: disable=unused-argument
        """Stub for error tracker when DIAGNOSIS unavailable."""
        raise RuntimeError(f"DIAGNOSIS unavailable: {_DIAGNOSIS_IMPORT_ERROR}")

    def error_tracker_reset(**kwargs):  # pylint: disable=unused-argument
        """Stub for error tracker when DIAGNOSIS unavailable."""
        raise RuntimeError(f"DIAGNOSIS unavailable: {_DIAGNOSIS_IMPORT_ERROR}")


# Static Dictionary Dispatch System (DDS-1)
# Each operation entry: {'func': callable, 'category': str, 'description': str}
_DISPATCH: dict[str, dict[str, Any]] = {
    # Import Testing
    "test_module_import": {
        "func": test_module_import,
        "category": "import_testing",
        "description": "Test if a module can be imported",
    },
    "test_import_sequence": {
        "func": test_import_sequence,
        "category": "import_testing",
        "description": "Test sequence of module imports",
    },

    # Diagnostic Response
    "format_diagnostic_response": {
        "func": format_diagnostic_response,
        "category": "response",
        "description": "Format diagnostic response for output",
    },

    # Import Diagnosis
    "diagnose_import_failure": {
        "func": diagnose_import_failure,
        "category": "import_diagnosis",
        "description": "Diagnose module import failures",
    },

    # System Health
    "diagnose_system_health": {
        "func": diagnose_system_health,
        "category": "system_health",
        "description": "Diagnose overall system health",
    },
    "check_system_health": {
        "func": check_system_health,
        "category": "system_health",
        "description": "Check system health status",
    },

    # Component Performance
    "diagnose_component_performance": {
        "func": diagnose_component_performance,
        "category": "performance",
        "description": "Diagnose component performance",
    },
    "diagnose_initialization_performance": {
        "func": diagnose_initialization_performance,
        "category": "performance",
        "description": "Diagnose initialization performance",
    },
    "diagnose_utility_performance": {
        "func": diagnose_utility_performance,
        "category": "performance",
        "description": "Diagnose utility performance",
    },
    "diagnose_singleton_performance": {
        "func": diagnose_singleton_performance,
        "category": "performance",
        "description": "Diagnose singleton performance",
    },

    # Memory Diagnosis
    "diagnose_memory_usage": {
        "func": diagnose_memory_usage,
        "category": "memory",
        "description": "Diagnose memory usage",
    },

    # Architecture Validation
    "validate_system_architecture": {
        "func": validate_system_architecture,
        "category": "validation",
        "description": "Validate system architecture",
    },
    "validate_imports": {
        "func": validate_imports,
        "category": "validation",
        "description": "Validate module imports",
    },
    "validate_gateway_routing": {
        "func": validate_gateway_routing,
        "category": "validation",
        "description": "Validate gateway routing",
    },

    # Diagnostic Suites
    "run_diagnostic_suite": {
        "func": run_diagnostic_suite,
        "category": "suite",
        "description": "Run comprehensive diagnostic suite",
    },

    # Component Health Checks
    "check_component_health": {
        "func": check_component_health,
        "category": "health_check",
        "description": "Check health of specific component",
    },
    "check_gateway_health": {
        "func": check_gateway_health,
        "category": "health_check",
        "description": "Check gateway health",
    },
    "check_initialization_health": {
        "func": check_initialization_health,
        "category": "health_check",
        "description": "Check initialization health",
    },
    "check_utility_health": {
        "func": check_utility_health,
        "category": "health_check",
        "description": "Check utility health",
    },
    "check_singleton_health": {
        "func": check_singleton_health,
        "category": "health_check",
        "description": "Check singleton health",
    },

    # Reports
    "generate_health_report": {
        "func": generate_health_report,
        "category": "report",
        "description": "Generate comprehensive health report",
    },

    # Dynamic Health Registry (NEW 2026-03-08)
    "register_health_check": {
        "func": _register_health_check_implementation,
        "category": "health_registry",
        "description": "Register a dynamic health check",
    },
    "unregister_health_check": {
        "func": _unregister_health_check_implementation,
        "category": "health_registry",
        "description": "Unregister a dynamic health check",
    },
    "list_health_checks": {
        "func": _list_health_checks_implementation,
        "category": "health_registry",
        "description": "List all registered health checks",
    },
    "execute_health_check": {
        "func": lambda **kwargs: _execute_health_check_implementation(
            name=kwargs.get('name', kwargs.get('check_name', 'default')),
            correlation_id=kwargs.get('correlation_id'),
            **{k: v for k, v in kwargs.items() if k not in ['name', 'check_name', 'correlation_id']}
        ),
        "category": "health_registry",
        "description": "Execute a specific health check",
    },
    "execute_all_health_checks": {
        "func": _execute_all_health_checks_implementation,
        "category": "health_registry",
        "description": "Execute all registered health checks",
    },
    "get_health_status": {
        "func": _get_health_status_implementation,
        "category": "health_registry",
        "description": "Get health status of components",
    },
    "clear_health_status": {
        "func": _clear_health_status_implementation,
        "category": "health_registry",
        "description": "Clear all health status",
    },
} if _DIAGNOSIS_AVAILABLE else {}

# Add error tracker operations (Phase 2)
# These are always added - stubs are used if error tracker not yet moved
_ERROR_TRACKER_OPERATIONS: dict[str, dict[str, Any]] = {
    # Error Tracker Operations (Phase 2)
    "record_error": {
        "func": error_tracker_record_error,
        "category": "error_tracker",
        "description": "Record new error with pattern classification",
    },
    "get_error_patterns": {
        "func": error_tracker_get_patterns,
        "category": "error_tracker",
        "description": "Get all error patterns with optional filtering",
    },
    "get_error_summary": {
        "func": error_tracker_get_summary,
        "category": "error_tracker",
        "description": "Get error summary statistics",
    },
    "get_error_details": {
        "func": error_tracker_get_patterns,
        "category": "error_tracker",
        "description": "Get specific error details by signature",
    },
    "get_error_frequency": {
        "func": lambda **kwargs: {"error_count": len(error_tracker_get_patterns())},
        "category": "error_tracker",
        "description": "Get error frequency in time window",
    },
    "is_error_chronic": {
        "func": lambda **kwargs: any(
            p.get("pattern") == "chronic"
            for p in error_tracker_get_patterns(
                pattern_filter="chronic",
                category_filter=kwargs.get("category")
            )
        ),
        "category": "error_tracker",
        "description": "Check if error is chronic",
    },
    "get_recent_errors": {
        "func": lambda **kwargs: {
            "recent_errors": error_tracker_get_summary().get("recent_errors", [])[:kwargs.get("count", 10)]
        },
        "category": "error_tracker",
        "description": "Get recent errors",
    },
    "get_errors_by_component": {
        "func": lambda **kwargs: error_tracker_get_patterns(
            category_filter=kwargs.get("component")
        ),
        "category": "error_tracker",
        "description": "Get errors by component",
    },
    "reset_error_tracker": {
        "func": error_tracker_reset,
        "category": "error_tracker",
        "description": "Clear all errors",
    },
    "run_diagnostic_test": {
        "func": check_component_health if _DIAGNOSIS_AVAILABLE else lambda **kwargs: {"error": "DIAGNOSIS unavailable"},
        "category": "error_tracker",
        "description": "Run diagnostic test on component",
    },
}

# Merge error tracker operations into main dispatch
if _DIAGNOSIS_AVAILABLE:
    _DISPATCH.update(_ERROR_TRACKER_OPERATIONS)


def execute_diagnosis_operation(operation: str, **kwargs) -> Any:
    """Route diagnosis operations to core implementations using Static DDS.

    Args:
        operation: Diagnosis operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result

    Raises:
        RuntimeError: If DIAGNOSIS interface unavailable
        ValueError: If operation unknown

    """
    validate_module_available("diagnosis", _DIAGNOSIS_AVAILABLE, _DIAGNOSIS_IMPORT_ERROR)

    operation_entry = _DISPATCH.get(operation)
    if not operation_entry:
        valid_ops = ", ".join(_DISPATCH.keys())
        raise ValueError(
            f"Unknown diagnosis operation: '{operation}'. "
            f"Valid: {valid_ops}",
        )

    handler: Callable = operation_entry["func"]
    return handler(**kwargs)


__all__ = ["execute_diagnosis_operation"]
