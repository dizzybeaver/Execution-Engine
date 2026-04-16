# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface_architectural_scanners.py
Version: 2026-04-11_2
Purpose: Interface router for architectural violation scanners
License: Apache 2.0

This module provides the GATEWAY INTERFACE LAYER for architectural scanners.
All domain implementation is in architectural_scanners/ package.
"""

from typing import Any

from lee.home_assistant.interface.base_routers import BaseSimpleDispatchRouter
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.architectural_scanners')
def _import_architectural_scanners():
    from lee.architectural_scanners import (
        scan_completeness_compliance,
        scan_direct_wrapper_import,
        scan_relative_import,
        scan_security_bypass,
    )
    return {
        'scan_completeness_compliance': scan_completeness_compliance,
        'scan_direct_wrapper_import': scan_direct_wrapper_import,
        'scan_relative_import': scan_relative_import,
        'scan_security_bypass': scan_security_bypass,
    }


_scanner_funcs = _import_architectural_scanners()
_ARCHITECTURAL_SCANNERS_AVAILABLE = _import_architectural_scanners.__dict__.get(
    '_ARCHITECTURAL_SCANNERS_AVAILABLE',
    False
)

if _ARCHITECTURAL_SCANNERS_AVAILABLE:
    scan_completeness_compliance = _scanner_funcs['scan_completeness_compliance']
    scan_direct_wrapper_import = _scanner_funcs['scan_direct_wrapper_import']
    scan_relative_import = _scanner_funcs['scan_relative_import']
    scan_security_bypass = _scanner_funcs['scan_security_bypass']
else:
    def scan_direct_wrapper_import(**_kwargs):
        return {"success": False, "error": "architectural_scanners not available"}

    def scan_relative_import(**_kwargs):
        return {"success": False, "error": "architectural_scanners not available"}

    def scan_security_bypass(**_kwargs):
        return {"success": False, "error": "architectural_scanners not available"}

    def scan_completeness_compliance(**_kwargs):
        return {"success": False, "error": "architectural_scanners not available"}

# Dispatch dictionary for O(1) operation routing
_ARCHITECTURAL_SCANNERS_DISPATCH = {
    "scan_direct_wrapper_import": scan_direct_wrapper_import,
    "scan_relative_import": scan_relative_import,
    "scan_security_bypass": scan_security_bypass,
    "scan_completeness_compliance": scan_completeness_compliance,
}


class _ArchitecturalScannersRouter(BaseSimpleDispatchRouter):
    """Router for architectural scanners interface operations.

    This router manages all architectural scanner operations including:
    - Direct wrapper import scanning
    - Relative import detection
    - Security bypass identification
    - Completeness compliance validation
    """

    def __init__(self):
        """Initialize the architectural scanners router."""
        # Create a dummy module for the core module parameter
        class DummyModule:
            pass

        super().__init__(
            interface_name="ArchitecturalScanners",
            core_module=DummyModule(),
            dispatch_map=_ARCHITECTURAL_SCANNERS_DISPATCH
        )


_architectural_scanners_router = _ArchitecturalScannersRouter()


def execute_architectural_scanners_operation(operation: str, **kwargs) -> Any:
    """Execute architectural scanner operation via dispatch with SUGA-ISP debug support.

    Args:
        operation: The architectural scanner operation to execute
        **kwargs: Operation-specific parameters

    Returns:
        Operation result from architectural scanner implementation
    """
    return _architectural_scanners_router.execute(operation, **kwargs)


def list_architectural_scanners_operations() -> list[str]:
    """List all available architectural scanner operations."""
    return _architectural_scanners_router.dispatch_map.keys()


__all__ = [
    "execute_architectural_scanners_operation",
    "list_architectural_scanners_operations",
    "_ARCHITECTURAL_SCANNERS_AVAILABLE"
]
