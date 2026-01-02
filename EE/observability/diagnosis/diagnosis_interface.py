"""
Diagnosis Interface Router - Observability Domain

UG-ISP Architecture (EE 2.1):
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
- Receives factory functions (not instances) via DI
"""

from typing import Any, Dict, Optional, Callable
from EE.observability.diagnosis.diagnosis_factory import DiagnosisFactory


def execute_diagnosis_operation(operation: str, **kwargs) -> Any:
    """
    Execute diagnosis operation (Router Interface) - EE 2.1 Compliant.

    UG-ISP Architecture (EE 2.1):
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via execute_operation() only
    - Receives factory functions (get_logger, get_metrics) NOT instances

    Args:
        operation: Operation name (health_check, diagnose, get_stats, etc.)
        **kwargs: Operation parameters including:
                  - get_logger: Factory function to create loggers
                  - get_metrics: Factory function to create metrics
                  - call_operation: Cross-domain operation callback

    Returns:
        Operation result

    Raises:
        ValueError: If operation not found
    """
    # EE 2.1: Extract factory functions from kwargs
    get_logger = kwargs.pop("get_logger", None)
    get_metrics = kwargs.pop("get_metrics", None)
    call_operation = kwargs.pop("call_operation", None)

    # EE 2.1: Create logger and metrics instances from factory functions
    logger = get_logger("observability.diagnosis") if get_logger else None
    metrics = get_metrics("observability.diagnosis") if get_metrics else None

    # Create factory instance with instances (not factories)
    factory = DiagnosisFactory(
        logger=logger,
        metrics=metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'health_check': factory.health_check,
        'diagnose': factory.diagnose,
        'get_stats': factory.get_stats,
        'check_dependency': factory.check_dependency,
        'run_diagnostics': factory.run_diagnostics,
        'get_status': factory.get_status,
        'get_health_report': factory.get_health_report,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown diagnosis operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_diagnosis_operation',
]
