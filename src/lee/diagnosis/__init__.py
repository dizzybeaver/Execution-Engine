"""Error pattern recognition and diagnosis system for LEE."""

# Classes
from lee.diagnosis.classes.ErrorOccurrence import ErrorOccurrence
from lee.diagnosis.classes.ErrorPatternStats import ErrorPatternStats
from lee.diagnosis.classes.ErrorSignature import ErrorSignature
from lee.diagnosis.classes.ErrorTracker import (
    ErrorTracker,
    error_tracker_get_patterns,
    error_tracker_get_summary,
    error_tracker_record_error,
    error_tracker_reset,
    get_error_tracker,
)

# Generic diagnosis
from lee.diagnosis.diagnosis_generic import (
    run_diagnostic_suite,
    validate_gateway_routing,
    validate_imports,
    validate_system_architecture,
)

# Import diagnosis
from lee.diagnosis.diagnosis_imports import (
    diagnose_import_failure,
    format_diagnostic_response,
    test_import_sequence,
    test_module_import,
)

# Performance diagnosis
from lee.diagnosis.diagnosis_performance import (
    diagnose_component_performance,
    diagnose_initialization_performance,
    diagnose_memory_usage,
    diagnose_singleton_performance,
    diagnose_system_health,
    diagnose_utility_performance,
)

# Enums
from lee.diagnosis.enums.ErrorPattern import ErrorPattern
from lee.diagnosis.enums.ErrorSeverity import ErrorSeverity

# Health checks
from lee.diagnosis.health import (
    check_component_health,
    check_gateway_health,
    check_initialization_health,
    check_singleton_health,
    check_system_health,
    check_utility_health,
    generate_health_report,
)

__all__ = [
    # Classes
    "ErrorOccurrence",
    "ErrorPatternStats",
    "ErrorSignature",
    "ErrorTracker",
    "error_tracker_get_patterns",
    "error_tracker_get_summary",
    "error_tracker_record_error",
    "error_tracker_reset",
    "get_error_tracker",
    # Enums
    "ErrorPattern",
    "ErrorSeverity",
    # Health checks
    "check_component_health",
    "check_gateway_health",
    "check_initialization_health",
    "check_singleton_health",
    "check_system_health",
    "check_utility_health",
    "generate_health_report",
    # Generic diagnosis
    "validate_system_architecture",
    "validate_imports",
    "validate_gateway_routing",
    "run_diagnostic_suite",
    # Import diagnosis
    "test_import_sequence",
    "test_module_import",
    "diagnose_import_failure",
    "format_diagnostic_response",
    # Performance diagnosis
    "diagnose_system_health",
    "diagnose_utility_performance",
    "diagnose_component_performance",
    "diagnose_memory_usage",
    "diagnose_initialization_performance",
    "diagnose_singleton_performance",
]
