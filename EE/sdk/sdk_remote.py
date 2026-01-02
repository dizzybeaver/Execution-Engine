"""
Remote SDK - EE Remote SDK Implementation

This module provides the Remote SDK implementation for the EE SDK domain gateway.
Remote SDKs execute operations on remote services via HTTP/REST APIs.

Architecture Layer: SDK Domain - Implementation Layer

Based on Gateway reference implementation patterns.

Integration:
    - Uses SDKGatewayError from sdk_common
    - Implements remote execution via HTTP requests
    - Supports lifecycle management (initialize, shutdown)
    - Provides method registration and execution via API calls

Usage:
    >>> from EE.sdk import create_remote_sdk
    >>>
    >>> # Create remote SDK
    >>> sdk = create_remote_sdk({
    ...     "name": "remote_processor",
    ...     "base_url": "https://api.example.com",
    ...     "methods": {
    ...         "process": "/api/process",
    ...         "validate": "/api/validate"
    ...     },
    ...     "timeout": 30,
    ...     "auth_token": "your-token"
    ... })
    >>>
    >>> # Initialize and call
    >>> sdk.initialize()
    >>> result = sdk.call("process", {"data": "input"})
    >>> sdk.shutdown()
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Callable
import threading
import json

from EE.sdk.sdk_common import (
    SDKGatewayError,
    SDKInitializationError,
    SDKExecutionError,
    SDKMethodNotFoundError,
    SDKTimeoutError,
)


class RemoteSDK:
    """Remote SDK implementation for HTTP-based remote execution.

    The RemoteSDK class provides a way to execute operations on remote services
    via HTTP/REST APIs. It supports authentication, timeout handling, and
    error handling.

    Attributes:
        config: Configuration dictionary
        base_url: Base URL for API endpoints
        methods: Dictionary of method names to API endpoints
        timeout: Default timeout in seconds
        auth_token: Optional authentication token
        headers: Default HTTP headers
        initialized: Whether SDK has been initialized
        session: Optional requests session for connection pooling
        _lock: Threading lock for thread-safe operations

    Example:
        >>> sdk = RemoteSDK({
        ...     "base_url": "https://api.example.com",
        ...     "methods": {
        ...         "process": "/api/process",
        ...         "validate": "/api/validate"
        ...     },
        ...     "timeout": 30,
        ...     "auth_token": "token123"
        ... })
        >>>
        >>> sdk.initialize()
        >>> result = sdk.call("process", {"data": "test"})
        >>> sdk.shutdown()
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize Remote SDK.

        Args:
            config: Configuration dictionary with keys:
                - base_url: Base URL for API endpoints (required)
                - methods: Dict of method name to API endpoint (required)
                - timeout: Default timeout in seconds (default: 30)
                - auth_token: Optional authentication token
                - headers: Optional dict of default HTTP headers
                - verify_ssl: Verify SSL certificates (default: True)

        Example:
            >>> config = {
            ...     "base_url": "https://api.example.com",
            ...     "methods": {
            ...         "process": "/api/process",
            ...         "analyze": "/api/analyze"
            ...     },
            ...     "timeout": 60,
            ...     "auth_token": "your-token",
            ...     "headers": {"X-Custom": "value"}
            ... }
            >>> sdk = RemoteSDK(config)
        """
        self.config = config
        self.base_url: str = config.get("base_url", "")
        self.methods: Dict[str, str] = config.get("methods", {})
        self.timeout: float = config.get("timeout", 30.0)
        self.auth_token: Optional[str] = config.get("auth_token")
        self.headers: Dict[str, str] = config.get("headers", {})
        self.verify_ssl: bool = config.get("verify_ssl", True)

        self.initialized: bool = False
        self.session: Optional[Any] = None  # requests.Session
        self._lock = threading.Lock()

    def initialize(self) -> None:
        """Initialize the Remote SDK.

        Creates requests session for connection pooling.

        Raises:
            SDKInitializationError: If initialization fails

        Example:
            >>> sdk = RemoteSDK(config)
            >>> sdk.initialize()
        """
        with self._lock:
            if self.initialized:
                return  # Already initialized

            try:
                # Import requests
                try:
                    import requests
                except ImportError as e:
                    raise SDKInitializationError(
                        message="requests library is required for RemoteSDK",
                        sdk_type="remote",
                        reason="Install requests: pip install requests",
                    ) from e

                # Create session
                self.session = requests.Session()

                # Add auth token if provided
                if self.auth_token:
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.auth_token}"
                    })

                # Add custom headers
                if self.headers:
                    self.session.headers.update(self.headers)

                # Validate base URL
                if not self.base_url:
                    raise SDKInitializationError(
                        message="base_url is required",
                        sdk_type="remote",
                        reason="Configuration must include base_url",
                    )

                # Validate methods
                if not self.methods:
                    raise SDKInitializationError(
                        message="No methods configured",
                        sdk_type="remote",
                        reason="Configuration must include methods dict",
                    )

                self.initialized = True

            except SDKInitializationError:
                raise
            except Exception as e:
                raise SDKInitializationError(
                    message=f"Failed to initialize Remote SDK",
                    sdk_type="remote",
                    reason=str(e),
                ) from e

    def call(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        http_method: str = "POST",
    ) -> Any:
        """Call a method on the Remote SDK.

        Args:
            method: Method name to call
            params: Parameters to send as JSON body (default: {})
            timeout: Timeout in seconds (default: uses SDK default)
            http_method: HTTP method to use (default: "POST")

        Returns:
            Parsed JSON response from API

        Raises:
            SDKMethodNotFoundError: If method not found
            SDKExecutionError: If HTTP request fails
            SDKTimeoutError: If request times out
            SDKGatewayError: If SDK not initialized

        Example:
            >>> result = sdk.call(
            ...     method="process",
            ...     params={"data": "input"},
            ...     timeout=60,
            ...     http_method="POST"
            ... )
        """
        if not self.initialized:
            raise SDKGatewayError(
                message="SDK not initialized. Call initialize() first.",
                error_code="SDK_NOT_INITIALIZED",
                sdk_type="remote",
                operation="call",
                method=method,
            )

        if method not in self.methods:
            raise SDKMethodNotFoundError(
                sdk_name=self.config.get("name", "remote"),
                method=method,
                available_methods=list(self.methods.keys()),
            )

        # Build full URL
        endpoint = self.methods[method]
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        params = params or {}

        # Use method-specific timeout or default
        req_timeout = timeout or self.timeout

        try:
            # Import requests
            import requests

            # Execute HTTP request
            response = self.session.request(
                method=http_method,
                url=url,
                json=params,
                timeout=req_timeout,
                verify=self.verify_ssl,
            )

            # Check for HTTP errors
            response.raise_for_status()

            # Parse JSON response
            try:
                return response.json()
            except ValueError as e:
                # Return text if not JSON
                return response.text

        except requests.exceptions.Timeout as e:
            raise SDKTimeoutError(
                message=f"Remote method '{method}' timed out after {req_timeout}s",
                sdk_name=self.config.get("name", "remote"),
                method=method,
                timeout_seconds=req_timeout,
            ) from e

        except requests.exceptions.HTTPError as e:
            raise SDKExecutionError(
                message=f"HTTP error calling method '{method}': {e.response.status_code}",
                sdk_type="remote",
                sdk_name=self.config.get("name", "remote"),
                method=method,
                params=params,
                reason=f"HTTP {e.response.status_code}: {e.response.text}",
            ) from e

        except requests.exceptions.RequestException as e:
            raise SDKExecutionError(
                message=f"Request failed for method '{method}'",
                sdk_type="remote",
                sdk_name=self.config.get("name", "remote"),
                method=method,
                params=params,
                reason=str(e),
            ) from e

        except Exception as e:
            raise SDKExecutionError(
                message=f"Unexpected error calling method '{method}'",
                sdk_type="remote",
                sdk_name=self.config.get("name", "remote"),
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

    def register_method(self, name: str, endpoint: str) -> None:
        """Register a new method.

        Args:
            name: Method name
            endpoint: API endpoint path (e.g., "/api/new_method")

        Raises:
            SDKGatewayError: If method already exists

        Example:
            >>> sdk.register_method("new_method", "/api/new_method")
        """
        if name in self.methods:
            raise SDKGatewayError(
                message=f"Method '{name}' already registered",
                error_code="SDK_METHOD_EXISTS",
                sdk_type="remote",
                operation="register_method",
                method=name,
            )

        self.methods[name] = endpoint

    def unregister_method(self, name: str) -> None:
        """Unregister a method.

        Args:
            name: Method name to remove

        Example:
            >>> sdk.unregister_method("old_method")
        """
        if name in self.methods:
            del self.methods[name]

    def set_auth_token(self, token: str) -> None:
        """Set or update authentication token.

        Args:
            token: New authentication token

        Example:
            >>> sdk.set_auth_token("new-token-123")
        """
        self.auth_token = token
        if self.session:
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })

    def set_header(self, key: str, value: str) -> None:
        """Set or update a default HTTP header.

        Args:
            key: Header name
            value: Header value

        Example:
            >>> sdk.set_header("X-Custom-Header", "custom-value")
        """
        self.headers[key] = value
        if self.session:
            self.session.headers.update({key: value})

    def shutdown(self) -> None:
        """Shutdown the Remote SDK.

        Closes requests session and cleans up resources.

        Example:
            >>> sdk.shutdown()
        """
        with self._lock:
            if not self.initialized:
                return  # Already shut down

            try:
                # Close session
                if self.session:
                    self.session.close()
                    self.session = None

                self.initialized = False

            except Exception as e:
                raise SDKGatewayError(
                    message=f"Failed to shutdown Remote SDK",
                    error_code="SDK_SHUTDOWN_ERROR",
                    context={"error": str(e)},
                    sdk_type="remote",
                    operation="shutdown",
                ) from e

    def get_status(self) -> Dict[str, Any]:
        """Get SDK status information.

        Returns:
            Dictionary with status information

        Example:
            >>> status = sdk.get_status()
            >>> print(f"Initialized: {status['initialized']}")
            >>> print(f"Base URL: {status['base_url']}")
        """
        return {
            "type": "remote",
            "initialized": self.initialized,
            "base_url": self.base_url,
            "method_count": len(self.methods),
            "methods": self.list_methods(),
            "timeout": self.timeout,
            "has_auth": self.auth_token is not None,
            "headers": list(self.headers.keys()),
        }


def create_remote_sdk(config: Dict[str, Any]) -> RemoteSDK:
    """Factory function to create a Remote SDK.

    This provides a clean interface for creating Remote SDK instances.

    Args:
        config: Configuration dictionary with keys:
            - base_url: Base URL for API endpoints (required)
            - methods: Dict of method name to API endpoint (required)
            - timeout: Default timeout in seconds (default: 30)
            - auth_token: Optional authentication token
            - headers: Optional dict of default HTTP headers
            - verify_ssl: Verify SSL certificates (default: True)

    Returns:
        Configured RemoteSDK instance

    Raises:
        SDKConfigurationError: If configuration is invalid

    Example:
        >>> sdk = create_remote_sdk({
        ...     "base_url": "https://api.example.com",
        ...     "methods": {
        ...         "process": "/api/process",
        ...         "analyze": "/api/analyze"
        ...     },
        ...     "timeout": 60,
        ...     "auth_token": "your-token"
        ... })
        >>>
        >>> sdk.initialize()
        >>> result = sdk.call("process", {"data": "test"})
    """
    # Validate required fields
    if "base_url" not in config:
        from EE.sdk.sdk_common import SDKConfigurationError
        raise SDKConfigurationError(
            message="Missing required configuration key: 'base_url'",
            sdk_type="remote",
            config=config,
            validation_errors=["base_url key is required"],
        )

    if "methods" not in config:
        from EE.sdk.sdk_common import SDKConfigurationError
        raise SDKConfigurationError(
            message="Missing required configuration key: 'methods'",
            sdk_type="remote",
            config=config,
            validation_errors=["methods key is required"],
        )

    base_url = config.get("base_url")
    if not isinstance(base_url, str) or not base_url:
        from EE.sdk.sdk_common import SDKConfigurationError
        raise SDKConfigurationError(
            message="'base_url' must be a non-empty string",
            sdk_type="remote",
            config=config,
            validation_errors=["base_url must be a valid URL string"],
        )

    methods = config.get("methods")
    if not isinstance(methods, dict):
        from EE.sdk.sdk_common import SDKConfigurationError
        raise SDKConfigurationError(
            message="'methods' must be a dictionary",
            sdk_type="remote",
            config=config,
            validation_errors=["methods must be a dict"],
        )

    # Validate timeout
    timeout = config.get("timeout", 30)
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        from EE.sdk.sdk_common import SDKConfigurationError
        raise SDKConfigurationError(
            message="'timeout' must be a positive number",
            sdk_type="remote",
            config=config,
            validation_errors=["timeout must be > 0"],
        )

    return RemoteSDK(config)


__all__ = [
    'RemoteSDK',
    'create_remote_sdk',
]
