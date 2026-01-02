"""
Local SDK - EE Local SDK Implementation

This module provides the Local SDK implementation for the EE SDK domain gateway.
Local SDKs execute operations within the current process using configurable handlers.

Architecture Layer: SDK Domain - Implementation Layer

Based on Gateway reference implementation patterns.

Integration:
    - Uses SDKGatewayError from sdk_common
    - Implements local execution via Python callables
    - Supports lifecycle management (initialize, shutdown)
    - Provides method registration and execution

Usage:
    >>> from EE.sdk import create_local_sdk
    >>>
    >>> # Define handler functions
    >>> def process_handler(params):
    ...     data = params.get("data")
    ...     # Process data locally
    ...     return {"result": processed_data}
    >>>
    >>> # Create local SDK
    >>> sdk = create_local_sdk({
    ...     "name": "processor",
    ...     "methods": {
    ...         "process": process_handler,
    ...         "validate": validate_handler
    ...     },
    ...     "timeout": 30
    ... })
    >>>
    >>> # Initialize and call
    >>> sdk.initialize()
    >>> result = sdk.call("process", {"data": "input"})
    >>> sdk.shutdown()
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Callable
import concurrent.futures
import threading

from EE.sdk.sdk_common import (
    SDKGatewayError,
    SDKInitializationError,
    SDKExecutionError,
    SDKMethodNotFoundError,
    SDKTimeoutError,
)


class LocalSDK:
    """Local SDK implementation for in-process execution.

    The LocalSDK class provides a way to execute Python callables as SDK methods.
    It supports timeout handling, method registration, and lifecycle management.

    Attributes:
        config: Configuration dictionary
        methods: Dictionary of registered method names to callables
        initialized: Whether SDK has been initialized
        executor: Thread pool executor for timeout handling
        _lock: Threading lock for thread-safe operations

    Example:
        >>> sdk = LocalSDK({
        ...     "methods": {
        ...         "process": my_handler,
        ...         "validate": validator
        ...     },
        ...     "timeout": 30
        ... })
        >>>
        >>> sdk.initialize()
        >>> result = sdk.call("process", {"data": "test"})
        >>> sdk.shutdown()
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize Local SDK.

        Args:
            config: Configuration dictionary with keys:
                - methods: Dict of method name to callable
                - timeout: Default timeout in seconds (default: 30)
                - max_workers: Max thread pool workers (default: 4)

        Example:
            >>> config = {
            ...     "methods": {
            ...         "process": process_func,
            ...         "analyze": analyze_func
            ...     },
            ...     "timeout": 60,
            ...     "max_workers": 8
            ... }
            >>> sdk = LocalSDK(config)
        """
        self.config = config
        self.methods: Dict[str, Callable] = config.get("methods", {})
        self.timeout: float = config.get("timeout", 30.0)
        self.max_workers: int = config.get("max_workers", 4)

        self.initialized: bool = False
        self.executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self._lock = threading.Lock()

    def initialize(self) -> None:
        """Initialize the Local SDK.

        Creates thread pool executor for timeout handling.

        Raises:
            SDKInitializationError: If initialization fails

        Example:
            >>> sdk = LocalSDK(config)
            >>> sdk.initialize()
        """
        with self._lock:
            if self.initialized:
                return  # Already initialized

            try:
                # Create thread pool executor
                self.executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=self.max_workers,
                    thread_name_prefix="local_sdk_",
                )

                # Validate methods
                for method_name, method in self.methods.items():
                    if not callable(method):
                        raise SDKInitializationError(
                            message=f"Method '{method_name}' is not callable",
                            sdk_type="local",
                            reason="Method must be a callable function",
                        )

                self.initialized = True

            except SDKInitializationError:
                raise
            except Exception as e:
                raise SDKInitializationError(
                    message=f"Failed to initialize Local SDK",
                    sdk_type="local",
                    reason=str(e),
                ) from e

    def call(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Call a method on the Local SDK.

        Args:
            method: Method name to call
            params: Parameters to pass to method (default: {})
            timeout: Timeout in seconds (default: uses SDK default)

        Returns:
            Method execution result

        Raises:
            SDKMethodNotFoundError: If method not found
            SDKExecutionError: If method execution fails
            SDKTimeoutError: If method times out
            SDKGatewayError: If SDK not initialized

        Example:
            >>> result = sdk.call(
            ...     method="process",
            ...     params={"data": "input"},
            ...     timeout=60
            ... )
        """
        if not self.initialized:
            raise SDKGatewayError(
                message="SDK not initialized. Call initialize() first.",
                error_code="SDK_NOT_INITIALIZED",
                sdk_type="local",
                operation="call",
                method=method,
            )

        if method not in self.methods:
            raise SDKMethodNotFoundError(
                sdk_name=self.config.get("name", "local"),
                method=method,
                available_methods=list(self.methods.keys()),
            )

        # Get method handler
        handler = self.methods[method]
        params = params or {}

        # Use method-specific timeout or default
        exec_timeout = timeout or self.timeout

        try:
            # Execute with timeout handling
            future = self.executor.submit(handler, params)

            try:
                result = future.result(timeout=exec_timeout)
                return result

            except concurrent.futures.TimeoutError:
                future.cancel()
                raise SDKTimeoutError(
                    message=f"Method '{method}' timed out after {exec_timeout}s",
                    sdk_name=self.config.get("name", "local"),
                    method=method,
                    timeout_seconds=exec_timeout,
                )

        except SDKTimeoutError:
            raise
        except Exception as e:
            raise SDKExecutionError(
                message=f"Method '{method}' execution failed",
                sdk_type="local",
                sdk_name=self.config.get("name", "local"),
                method=method,
                params=params,
                reason=str(e),
            ) from e

    def has_method(self, method: str) -> bool:
        """Check if method exists.

        Args:
            method: Method name to check

        Returns:
            True if method exists, False otherwise

        Example:
            >>> if sdk.has_method("process"):
            ...     result = sdk.call("process", {...})
        """
        return method in self.methods

    def list_methods(self) -> list[str]:
        """List all available methods.

        Returns:
            List of method names

        Example:
            >>> methods = sdk.list_methods()
            >>> print(f"Available methods: {methods}")
        """
        return list(self.methods.keys())

    def register_method(self, name: str, handler: Callable) -> None:
        """Register a new method.

        Args:
            name: Method name
            handler: Callable handler function

        Raises:
            SDKGatewayError: If method already exists

        Example:
            >>> def new_handler(params):
            ...     return {"result": "processed"}
            >>>
            >>> sdk.register_method("new_method", new_handler)
        """
        if name in self.methods:
            raise SDKGatewayError(
                message=f"Method '{name}' already registered",
                error_code="SDK_METHOD_EXISTS",
                sdk_type="local",
                operation="register_method",
                method=name,
            )

        if not callable(handler):
            raise SDKGatewayError(
                message=f"Handler for '{name}' is not callable",
                error_code="SDK_INVALID_HANDLER",
                sdk_type="local",
                operation="register_method",
                method=name,
            )

        self.methods[name] = handler

    def unregister_method(self, name: str) -> None:
        """Unregister a method.

        Args:
            name: Method name to remove

        Example:
            >>> sdk.unregister_method("old_method")
        """
        if name in self.methods:
            del self.methods[name]

    def shutdown(self) -> None:
        """Shutdown the Local SDK.

        Closes thread pool executor and cleans up resources.

        Example:
            >>> sdk.shutdown()
        """
        with self._lock:
            if not self.initialized:
                return  # Already shut down

            try:
                # Shutdown executor
                if self.executor:
                    self.executor.shutdown(wait=True)
                    self.executor = None

                self.initialized = False

            except Exception as e:
                raise SDKGatewayError(
                    message=f"Failed to shutdown Local SDK",
                    error_code="SDK_SHUTDOWN_ERROR",
                    context={"error": str(e)},
                    sdk_type="local",
                    operation="shutdown",
                ) from e

    def get_status(self) -> Dict[str, Any]:
        """Get SDK status information.

        Returns:
            Dictionary with status information

        Example:
            >>> status = sdk.get_status()
            >>> print(f"Initialized: {status['initialized']}")
            >>> print(f"Methods: {status['method_count']}")
        """
        return {
            "type": "local",
            "initialized": self.initialized,
            "method_count": len(self.methods),
            "methods": self.list_methods(),
            "timeout": self.timeout,
            "max_workers": self.max_workers,
        }


def create_local_sdk(config: Dict[str, Any]) -> LocalSDK:
    """Factory function to create a Local SDK.

    This provides a clean interface for creating Local SDK instances.

    Args:
        config: Configuration dictionary with keys:
            - methods: Dict of method name to callable (required)
            - timeout: Default timeout in seconds (default: 30)
            - max_workers: Max thread pool workers (default: 4)

    Returns:
        Configured LocalSDK instance

    Raises:
        SDKConfigurationError: If configuration is invalid

    Example:
        >>> def process_handler(params):
        ...     return {"result": "processed"}
        >>>
        >>> sdk = create_local_sdk({
        ...     "methods": {
        ...         "process": process_handler
        ...     },
        ...     "timeout": 60
        ... })
        >>>
        >>> sdk.initialize()
        >>> result = sdk.call("process", {"data": "test"})
    """
    # Validate required fields
    if "methods" not in config:
        from EE.sdk.sdk_common import SDKConfigurationError
        raise SDKConfigurationError(
            message="Missing required configuration key: 'methods'",
            sdk_type="local",
            config=config,
            validation_errors=["methods key is required"],
        )

    methods = config.get("methods")
    if not isinstance(methods, dict):
        from EE.sdk.sdk_common import SDKConfigurationError
        raise SDKConfigurationError(
            message="'methods' must be a dictionary",
            sdk_type="local",
            config=config,
            validation_errors=["methods must be a dict"],
        )

    # Validate timeout
    timeout = config.get("timeout", 30)
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        from EE.sdk.sdk_common import SDKConfigurationError
        raise SDKConfigurationError(
            message="'timeout' must be a positive number",
            sdk_type="local",
            config=config,
            validation_errors=["timeout must be > 0"],
        )

    # Validate max_workers
    max_workers = config.get("max_workers", 4)
    if not isinstance(max_workers, int) or max_workers <= 0:
        from EE.sdk.sdk_common import SDKConfigurationError
        raise SDKConfigurationError(
            message="'max_workers' must be a positive integer",
            sdk_type="local",
            config=config,
            validation_errors=["max_workers must be > 0"],
        )

    return LocalSDK(config)


__all__ = [
    'LocalSDK',
    'create_local_sdk',
]
