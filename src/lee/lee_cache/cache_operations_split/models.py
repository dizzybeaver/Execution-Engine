"""cache_operations_split/models.py

Gateway imports and utilities for cache operations.
"""

from __future__ import annotations


# Import gateway functions (avoid circular import with lazy import)

# Import the LUGSIntegratedCache class from cache_generic

# Import debug logging helper

# Lazy imports for gateway operations to avoid circular dependency
_gateway_imported = False
_GatewayInterface = None
_execute_operation = None

def _get_gateway():
    """Lazy import gateway functions to avoid circular dependency."""
    # pylint: disable=global-statement,import-outside-toplevel
    # Lazy import pattern requires global state and delayed imports
    global _gateway_imported, _GatewayInterface, _execute_operation
    if not _gateway_imported:
        try:
            from lee.gateway import GatewayInterface, execute_operation
            _GatewayInterface = GatewayInterface
            _execute_operation = execute_operation
            _gateway_imported = True
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
    return _GatewayInterface, _execute_operation



# Lazy imports for optional cache optimization modules
_cache_observability_imported = False
_get_cache_observability = None


def _get_cache_observability_instance():
    """Lazy import cache observability to avoid circular dependency."""
    # pylint: disable=global-statement,import-outside-toplevel
    # Lazy import pattern requires global state and delayed imports
    global _cache_observability_imported, _get_cache_observability
    if not _cache_observability_imported:
        try:
            from lee.lee_cache.cache_observability import get_cache_observability
            _get_cache_observability = get_cache_observability
            _cache_observability_imported = True
        except ImportError:
            # Optional dependency - continue if unavailable
            ...
    return _get_cache_observability
