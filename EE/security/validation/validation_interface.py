"""
Validation Interface Router - Security Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.security.validation.validation_factory import ValidationFactory


def execute_validation_operation(operation: str, **kwargs) -> Any:
    """
    Execute validation operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via call_operation() only

    Args:
        operation: Operation name (validate_email, sanitize_string, etc.)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation not found
    """
    # Get injected dependencies
    logger = kwargs.get("logger")
    metrics = kwargs.get("metrics")
    call_operation = kwargs.get("call_operation")

    # Create factory instance
    factory = ValidationFactory(
        logger=logger,
        metrics=metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'validate_email': factory.validate_email,
        'validate_url': factory.validate_url,
        'validate_uuid': factory.validate_uuid,
        'validate_ip': factory.validate_ip,
        'validate_phone': factory.validate_phone,
        'sanitize_string': factory.sanitize_string,
        'sanitize_html': factory.sanitize_html,
        'sanitize_sql': factory.sanitize_sql,
        'check_length': factory.check_length,
        'check_range': factory.check_range,
        'check_regex': factory.check_regex,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown validation operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_validation_operation',
]
