"""interface/interface_common.py
Version: 2026-04-03_1
Purpose: Common utilities and helpers for interface routers
License: Apache 2.0

This module provides shared functionality for all interface routers,
including import protection helpers to reduce boilerplate code.
"""



from typing import Optional
def validate_module_available(
    interface_name: str,
    available_flag: bool,
    import_error: Optional[str],
) -> None:
    """Validate that a module is available, raise error if not.

    This centralizes the availability check logic used across all
    interface routers, reducing boilerplate in execute_*_operation().

    Args:
        interface_name: Name of the interface (e.g., 'cache', 'config')
        available_flag: Boolean flag indicating if module is available
        import_error: Error message from import failure

    Raises:
        InterfaceUnavailableError: If module is not available
    """
    # pylint: disable=import-outside-toplevel
    from lee.interface.interface_errors import InterfaceUnavailableError

    if not available_flag:
        raise InterfaceUnavailableError(interface_name, import_error)


__all__ = [
    'validate_module_available',
]
