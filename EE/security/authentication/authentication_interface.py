"""
Authentication Interface Router - Security Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.security.authentication.authentication_factory import AuthenticationFactory


def execute_authentication_operation(operation: str, **kwargs) -> Any:
    """
    Execute authentication operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via call_operation() only

    Args:
        operation: Operation name (hash_password, verify_password, etc.)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation not found
    """
    # EE 2.1: Get factory functions instead of instances
    get_logger = kwargs.get("get_logger")
    get_metrics = kwargs.get("get_metrics")
    call_operation = kwargs.get("call_operation")

    # Create factory instance with factory functions
    factory = AuthenticationFactory(
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'hash_password': factory.hash_password,
        'verify_password': factory.verify_password,
        'generate_token': factory.generate_token,
        'verify_token': factory.verify_token,
        'decode_token': factory.decode_token,
        'authorize': factory.authorize,
        'generate_api_key': factory.generate_api_key,
        'verify_api_key': factory.verify_api_key,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown authentication operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_authentication_operation',
]
