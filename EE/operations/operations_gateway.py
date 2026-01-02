"""
Operations Domain Gateway - UG-ISP Compliant

Routes operations to appropriate interfaces within the Operations domain:
- cache: Caching operations with LRU eviction
- circuit_breaker: Fault tolerance and circuit breaker pattern
- fileio: File I/O operations
- serialization: Data serialization (JSON, pickle, etc.)
- template: Template operations and rendering
- object_pool: Generic object pooling for resource management
- threading: Thread pool management and concurrent execution

UG-ISP Compliance:
- Extends DomainGateway base class
- Uses execute_domain_operation(interface, operation, **kwargs)
- Cross-domain calls via call_operation callback
"""

from __future__ import annotations
from typing import Any, Dict, Callable

# EE 2.1: NO sys.path manipulation
from EE.universal_gateway.domain_gateway import DomainGateway

# Import interface routers
from EE.operations.cache.cache_interface import execute_cache_operation
from EE.operations.circuit_breaker.circuit_breaker_interface import execute_circuit_breaker_operation
from EE.operations.fileio.fileio_interface import execute_fileio_operation
from EE.operations.serialization.serialization_interface import execute_serialization_operation
from EE.operations.template.template_interface import execute_template_operation
from EE.operations.object_pool.object_pool_interface import execute_object_pool_operation
from EE.operations.threading_ops.threading_interface import execute_threading_operation


class OperationsGateway(DomainGateway):
    """Operations Domain Gateway - EE 2.1 Compliant.

    Provides operational EE capabilities through the following interfaces:
    - cache: Caching operations (get, set, delete, clear, stats)
    - circuit_breaker: Fault tolerance (execute, get_state, reset, get_stats)
    - fileio: File I/O (read, write, append, delete, exists)
    - serialization: Data serialization (to_json, from_json, to_pickle, from_pickle)
    - template: Template operations (render, compile)
    - object_pool: Object pooling (acquire, release, create, delete, stats)
    - threading: Threading (submit, map, shutdown, get_stats)

    All operations follow UG-ISP patterns:
    - execute_domain_operation(interface, operation, **kwargs)
    - Cross-domain calls via call_operation callback
    - No direct imports outside operations domain

    Example:
        gateway = OperationsGateway(
            domain_name="operations",
            get_logger=logger_factory,
            get_metrics=metrics_factory,
            get_config=config_factory,
            call_operation=callback
        )

        # Cache a value
        gateway.execute_domain_operation(
            "cache", "set", key="user:123", value={"name": "Alice"}
        )

        # Acquire from pool
        conn = gateway.execute_domain_operation(
            "object_pool", "acquire", pool_name="connections"
        )
    """

    # FIXED: Removed @dataclass(frozen=True) decorator - incompatible with custom __init__
    # FIXED: Removed dataclass field declarations (logger, metrics, call_operation)

    def __init__(
        self,
        domain_name: str,
        get_logger: Callable,
        get_metrics: Callable,
        get_config: Callable,
        call_operation: Callable,
    ):
        """Initialize operations domain gateway (EE 2.1).

        Args:
            domain_name: Domain name (must be "operations")
            get_logger: Factory function to create loggers
            get_metrics: Factory function to create metrics collectors
            get_config: Factory function to get configuration values
            call_operation: Function to call operations in other domains
        """
        # Call parent constructor with uniform signature (EE 2.1)
        super().__init__(
            domain_name=domain_name,
            get_logger=get_logger,
            get_metrics=get_metrics,
            get_config=get_config,
            call_operation=call_operation
        )

    # FIXED: Removed legacy execute() method - use execute_domain_operation() instead

    def execute_domain_operation(
        self,
        interface: str,
        operation: str,
        **kwargs
    ) -> Any:
        """Execute domain operation using UG-ISP pattern.

        Args:
            interface: Interface name (cache, circuit_breaker, fileio, etc.)
            operation: Operation name (get, set, acquire, etc.)
            **kwargs: Operation parameters

        Returns:
            Operation result

        Raises:
            GatewayError: If interface or operation is invalid
        """
        # EE 2.1: Inject factory functions instead of instances
        kwargs.setdefault("get_logger", self._get_logger)
        kwargs.setdefault("get_metrics", self._get_metrics)
        kwargs.setdefault("call_operation", self._call_operation)

        # Route to appropriate interface
        try:
            if interface == "cache":
                return execute_cache_operation(operation, **kwargs)
            elif interface == "circuit_breaker":
                return execute_circuit_breaker_operation(operation, **kwargs)
            elif interface == "fileio":
                return execute_fileio_operation(operation, **kwargs)
            elif interface == "serialization":
                return execute_serialization_operation(operation, **kwargs)
            elif interface == "template":
                return execute_template_operation(operation, **kwargs)
            elif interface == "object_pool":
                return execute_object_pool_operation(operation, **kwargs)
            elif interface == "threading":
                return execute_threading_operation(operation, **kwargs)
            else:
                raise GatewayError(
                    f"Unknown operations interface: {interface}. "
                    f"Valid interfaces: cache, circuit_breaker, fileio, serialization, "
                    f"template, object_pool, threading"
                )
        except ValueError as e:
            raise GatewayError(
                f"Operation failed: {e}"
            ) from e

    def list_all(self) -> Dict[str, Any]:
        """List all operations domain operations.

        Returns:
            Dictionary with all operations organized by interface
        """
        return {
            "domain": "operations",
            "interfaces": {
                "cache": {
                    "description": "Caching operations with LRU eviction",
                    "operations": [
                        {"operation": "get", "description": "Get value from cache"},
                        {"operation": "set", "description": "Set value in cache"},
                        {"operation": "delete", "description": "Delete from cache"},
                        {"operation": "clear", "description": "Clear cache"},
                        {"operation": "stats", "description": "Get cache statistics"},
                        {"operation": "exists", "description": "Check if key exists"},
                    ]
                },
                "circuit_breaker": {
                    "description": "Fault tolerance and circuit breaker pattern",
                    "operations": [
                        {"operation": "execute", "description": "Execute through circuit breaker"},
                        {"operation": "get_state", "description": "Get circuit breaker state"},
                        {"operation": "reset", "description": "Reset circuit breaker"},
                        {"operation": "get_stats", "description": "Get circuit breaker stats"},
                    ]
                },
                "fileio": {
                    "description": "File I/O operations",
                    "operations": [
                        {"operation": "read", "description": "Read file"},
                        {"operation": "write", "description": "Write file"},
                        {"operation": "append", "description": "Append to file"},
                        {"operation": "delete", "description": "Delete file"},
                        {"operation": "exists", "description": "Check if file exists"},
                    ]
                },
                "serialization": {
                    "description": "Data serialization",
                    "operations": [
                        {"operation": "to_json", "description": "Serialize to JSON"},
                        {"operation": "from_json", "description": "Deserialize from JSON"},
                        {"operation": "to_pickle", "description": "Serialize to pickle"},
                        {"operation": "from_pickle", "description": "Deserialize from pickle"},
                    ]
                },
                "template": {
                    "description": "Template operations",
                    "operations": [
                        {"operation": "render", "description": "Render template"},
                        {"operation": "compile", "description": "Compile template"},
                        {"operation": "render_string", "description": "Render string template"},
                    ]
                },
                "object_pool": {
                    "description": "Generic object pooling",
                    "operations": [
                        {"operation": "create_pool", "description": "Create object pool"},
                        {"operation": "acquire", "description": "Acquire from pool"},
                        {"operation": "release", "description": "Release to pool"},
                        {"operation": "delete_pool", "description": "Delete pool"},
                        {"operation": "get_stats", "description": "Get pool statistics"},
                        {"operation": "list_pools", "description": "List all pools"},
                        {"operation": "clear_pool", "description": "Clear pool"},
                        {"operation": "resize_pool", "description": "Resize pool"},
                        {"operation": "warm_pool", "description": "Warm pool with objects"},
                    ]
                },
                "threading": {
                    "description": "Thread pool management",
                    "operations": [
                        {"operation": "submit", "description": "Submit task to thread pool"},
                        {"operation": "map", "description": "Map function over iterable"},
                        {"operation": "shutdown", "description": "Shutdown thread pool"},
                        {"operation": "get_stats", "description": "Get thread pool stats"},
                    ]
                },
            }
        }


__all__ = [
    "OperationsGateway",
]
