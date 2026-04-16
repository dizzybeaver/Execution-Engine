"""diagnosis/diagnosis_imports.py

Version: 2025-12-17_1
Purpose: Moved to TEST interface - file kept for backward compatibility
License: Apache 2.0

NOTE: All import testing functions have been moved to:
- lee_test.test_imports module
- Access via TEST interface: test_module_import, test_import_sequence, diagnose_import_failure

This file remains for backward compatibility only.

Exports:
    test_import_sequence: Backward compatibility wrapper for TEST interface
    test_module_import: Backward compatibility wrapper for TEST interface
    diagnose_import_failure: Backward compatibility wrapper for TEST interface
    format_diagnostic_response: Format diagnostic response (backward compatibility)
"""

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id


def test_import_sequence(*args, **kwargs):
    """Backward compatibility wrapper - use TEST interface instead."""
    return execute_operation(GatewayInterface.TEST, "test_import_sequence", *args, **kwargs)


# SUGA-ISP Compliant Debug Functions


def test_module_import(*args, **kwargs):
    """Backward compatibility wrapper - use TEST interface instead."""
    module_name = kwargs.get("module_name", args[0] if args else "unknown")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         message="Testing module import (backward compatibility wrapper)",
                         module_name=module_name)
    except ImportError:
        # Optional dependency - continue if unavailable
        ...
    return execute_operation(GatewayInterface.TEST, "test_module_import", *args, **kwargs)

def diagnose_import_failure(*args, **kwargs):
    """Backward compatibility wrapper - use TEST interface instead."""
    return execute_operation(GatewayInterface.TEST, "diagnose_import_failure", *args, **kwargs)

def format_diagnostic_response(diagnostic_data: dict, status: str = None, severity: str = None, **kwargs) -> dict:
    """Format diagnostic response (backward compatibility wrapper)."""
    # Generate correlation ID with fallback
    # Note: execute_operation and GatewayInterface are imported at module level (line 16)
    try:
        corr_id = generate_correlation_id("diag")
    except (ImportError, AttributeError, RuntimeError):
        corr_id = generate_correlation_id("diag")

    try:
        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=corr_id, scope="DIAGNOSIS",
                         message="Formatting diagnostic response (backward compatibility wrapper)",
                         has_data=diagnostic_data is not None, status=status, severity=severity)
    except ImportError:
        # Optional dependency - continue if unavailable
        ...

    # Basic formatting - in real implementation this would be more sophisticated
    formatted_response = {
        "diagnostic_data": diagnostic_data or {},
        "status": status or "completed",
        "severity": severity or "info",
        "timestamp": kwargs.get("timestamp"),
        "correlation_id": corr_id,
    }

    return formatted_response

__all__ = [
    "diagnose_import_failure",
    "format_diagnostic_response",
    "test_import_sequence",
    "test_module_import",
]
