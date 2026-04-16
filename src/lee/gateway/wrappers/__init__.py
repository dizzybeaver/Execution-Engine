"""LEE Gateway Wrapper Functions - User-Facing API

Provides categorized access to all 181+ wrapper functions organized by functional area.

Usage:
    from lee.gateway.wrappers import cache, logging, security, metrics

    cache.get(key='device:light:office', default=None)
    logging.log_info(message='System started')
    metrics.increment_counter(name='api.calls')

Note: The 'test' wrapper is not auto-imported to avoid circular import issues.
Import it explicitly when needed: from lee.gateway.wrappers import test
"""

# Import all category namespaces as modules
# NOTE: 'test' module excluded to avoid circular import during package initialization
# Import test module explicitly when needed: from lee.gateway.wrappers import test
from lee.gateway.wrappers import (
    batch,
    cache,
    circuit_breaker,
    config,
    database,
    debug,
    http,
    initialization,
    lazy_import,
    logging,
    metrics,
    monitoring,
    security,
    singleton,
    utility,
    validation,
    websocket,
)


def __getattr__(name: str):
    """Lazy import for test module to avoid circular import."""
    if name == 'test':
        try:
            import importlib
            return importlib.import_module('.test', 'lee.gateway.wrappers')
        except ModuleNotFoundError:
            # test.py is excluded from deployment packages
            # Only available in development environment
            raise AttributeError(
                "test module not available in production deployment. "
                "Use from lee.gateway import execute_operation, GatewayInterface; "
                "execute_operation(GatewayInterface.TEST, 'operation_name', ...) instead."
            )
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


__all__ = [
    'cache',
    'config',
    'logging',
    'security',
    'singleton',
    'batch',
    'validation',
    'http',
    'database',
    'initialization',
    'metrics',
    'utility',
    'monitoring',
    'debug',
    'websocket',
    'circuit_breaker',
    'lazy_import',
    'test',  # Available for explicit import but not auto-imported
]
