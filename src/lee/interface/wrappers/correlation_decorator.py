"""Correlation ID Decorator

Automatically adds correlation IDs to wrapper function calls for observability.

DEPRECATED: Import from lee.interface.wrappers.base_wrapper instead.
This module is maintained for backward compatibility only.

Migration guide:
- OLD: from lee.interface.wrappers.correlation_decorator import generate_correlation_id
- NEW: from lee.interface.wrappers.base_wrapper import generate_correlation_id
"""

# Re-export from base_wrapper for backward compatibility
from lee.interface.wrappers.base_wrapper import (
    generate_correlation_id,
    with_correlation_id,
)

__all__ = ["generate_correlation_id", "with_correlation_id"]
