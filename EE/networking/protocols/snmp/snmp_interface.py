"""
SNMP Interface Router - Networking Domain

UG-ISP Architecture:
- This is the Interface Layer (Router)
- Uses DISPATCH dictionary for O(1) operation routing
- Factory contains actual implementation
- Cross-domain via call_operation() ONLY
"""

from typing import Any, Dict, Optional, Callable
from EE.networking.protocols.snmp.snmp_factory import SNMPFactory


def execute_snmp_operation(operation: str, **kwargs) -> Any:
    """
    Execute SNMP operation (Router Interface).

    UG-ISP Architecture:
    - Interface IS the router (not gateway to factory)
    - Uses DISPATCH dictionary for O(1) routing
    - Factory contains implementation
    - Cross-interface via call_operation() only

    Args:
        operation: Operation name (connect, get, set, walk, disconnect)
        **kwargs: Operation parameters

    Returns:
        Operation result

    Raises:
        ValueError: If operation not found
    """
    # Get injected dependencies
    get_logger = kwargs.get("get_logger")
    get_metrics = kwargs.get("get_metrics")
    call_operation = kwargs.get("call_operation")

    # Create factory instance
    factory = SNMPFactory(
        get_logger=get_logger,
        get_metrics=get_metrics,
        call_operation=call_operation
    )

    # DISPATCH Dictionary (DD-1 Pattern)
    _DISPATCH = {
        'connect': factory.connect,
        'get': factory.get,
        'set': factory.set,
        'walk': factory.walk,
        'disconnect': factory.disconnect,
    }

    handler = _DISPATCH.get(operation)

    if not handler:
        raise ValueError(
            f"Unknown SNMP operation: {operation}. "
            f"Valid operations: {list(_DISPATCH.keys())}"
        )

    return handler(**kwargs)


__all__ = [
    'execute_snmp_operation',
]
