"""
SDK Common Module - EE SDK Domain Gateway Base

This module provides SDK-specific error handling and common utilities
for the EE SDK domain gateway.

Architecture Layer: SDK Domain - Base Layer

Based on Gateway reference implementation patterns.

Integration:
    - Uses EE gateway infrastructure (GatewayError from gateway_common)
    - Provides SDK-specific error classes
    - Maintains error chaining and context preservation
    - Supports both local and remote SDK operations
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import datetime

class SDKGatewayError(Exception):
    """Base error for SDK gateway failures in EE.

    This error class extends GatewayError with SDK-specific error handling
    for SDK domain operations including initialization, execution,
    configuration validation, and lifecycle management.

    Attributes:
        sdk_type: Type of SDK (e.g., "local", "remote")
        sdk_name: Name/identifier of the SDK instance
        operation: SDK operation type (e.g., "initialize", "execute", "shutdown")
        method: SDK method being called (if applicable)

    Example:
        >>> try:
        ...     sdk_gateway.execute("sdk.call", {"method": "process_data"})
        ... except SDKGatewayError as e:
        ...     print(f"SDK Error: {e.error_code}")
        ...     print(f"Type: {e.sdk_type}, Method: {e.method}")
        ...     print(f"Context: {e.context}")
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        source: Optional[str] = None,
        sdk_type: Optional[str] = None,
        sdk_name: Optional[str] = None,
        operation: Optional[str] = None,
        method: Optional[str] = None,
    ) -> None:
        """Initialize an SDKGatewayError.

        Args:
            message: Human-readable error description
            error_code: Optional error code for categorization
            context: Optional dictionary with error context
            source: Optional source component name
            sdk_type: Type of SDK (e.g., "local", "remote")
            sdk_name: Name/identifier of the SDK instance
            operation: SDK operation type (e.g., "initialize", "execute")
            method: SDK method being called (if applicable)
        """
        self.sdk_type = sdk_type
        self.sdk_name = sdk_name
        self.operation = operation
        self.method = method

        # Add SDK-specific context
        sdk_context = {
            "sdk_type": sdk_type,
            "sdk_name": sdk_name,
            "operation": operation,
            "method": method,
        }
        # Filter out None values
        sdk_context = {k: v for k, v in sdk_context.items() if v is not None}

        if context:
            sdk_context.update(context)

        # Default to SDK Gateway if not specified
        sdk_source = source or "SDKGateway"

        # Default error code
        sdk_error_code = error_code or "SDK_GATEWAY_ERROR"

        super().__init__(
            message=message,
            error_code=sdk_error_code,
            context=sdk_context,
            source=sdk_source,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation.

        Returns:
            Dictionary with all error information including SDK-specific fields
        """
        base_dict = super().to_dict()
        base_dict.update({
            "sdk_type": self.sdk_type,
            "sdk_name": self.sdk_name,
            "operation": self.operation,
            "method": self.method,
        })
        return base_dict


class SDKInitializationError(SDKGatewayError):
    """Raised when SDK initialization fails.

    Example:
        >>> raise SDKInitializationError(
        ...     sdk_type="local",
        ...     sdk_name="data_processor",
        ...     reason="Missing required configuration"
        ... )
    """

    def __init__(
        self,
        message: str,
        sdk_type: Optional[str] = None,
        sdk_name: Optional[str] = None,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an SDKInitializationError.

        Args:
            message: Human-readable error description
            sdk_type: Type of SDK being initialized
            sdk_name: Name of SDK being initialized
            reason: Reason for initialization failure
            context: Optional additional context
        """
        self.reason = reason

        error_context = {"reason": reason} if reason else {}
        if context:
            error_context.update(context)

        super().__init__(
            message=message or f"SDK initialization failed: {reason}",
            error_code="SDK_INITIALIZATION_ERROR",
            context=error_context,
            sdk_type=sdk_type,
            sdk_name=sdk_name,
            operation="initialize",
        )


class SDKExecutionError(SDKGatewayError):
    """Raised when SDK method execution fails.

    Example:
        >>> raise SDKExecutionError(
        ...     sdk_type="local",
        ...     method="process_data",
        ...     params={"input": "data"},
        ...     reason="Invalid input format"
        ... )
    """

    def __init__(
        self,
        message: str,
        sdk_type: Optional[str] = None,
        sdk_name: Optional[str] = None,
        method: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an SDKExecutionError.

        Args:
            message: Human-readable error description
            sdk_type: Type of SDK
            sdk_name: Name of SDK instance
            method: Method being executed
            params: Parameters passed to method
            reason: Reason for execution failure
            context: Optional additional context
        """
        self.reason = reason
        self.params = params

        error_context = {
            "reason": reason,
            "params": params,
        }
        # Filter out None values
        error_context = {k: v for k, v in error_context.items() if v is not None}

        if context:
            error_context.update(context)

        super().__init__(
            message=message or f"SDK execution failed for method '{method}': {reason}",
            error_code="SDK_EXECUTION_ERROR",
            context=error_context,
            sdk_type=sdk_type,
            sdk_name=sdk_name,
            operation="execute",
            method=method,
        )


class SDKConfigurationError(SDKGatewayError):
    """Raised when SDK configuration is invalid.

    Example:
        >>> raise SDKConfigurationError(
        ...     sdk_type="remote",
        ...     config={"host": "invalid"},
        ...     validation_errors=["host must be valid URL"]
        ... )
    """

    def __init__(
        self,
        message: str,
        sdk_type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        validation_errors: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an SDKConfigurationError.

        Args:
            message: Human-readable error description
            sdk_type: Type of SDK
            config: Configuration that failed validation
            validation_errors: List of validation error messages
            context: Optional additional context
        """
        self.config = config
        self.validation_errors = validation_errors or []

        error_context = {
            "config": config,
            "validation_errors": self.validation_errors,
        }
        # Filter out None values
        error_context = {k: v for k, v in error_context.items() if v is not None}

        if context:
            error_context.update(context)

        super().__init__(
            message=message or "SDK configuration validation failed",
            error_code="SDK_CONFIGURATION_ERROR",
            context=error_context,
            sdk_type=sdk_type,
            operation="validate_config",
        )


class SDKNotFoundError(SDKGatewayError):
    """Raised when requested SDK instance is not found.

    Example:
        >>> raise SDKNotFoundError(
        ...     sdk_name="nonexistent_sdk",
        ...     available_sdks=["processor", "analyzer"]
        ... )
    """

    def __init__(
        self,
        sdk_name: str,
        available_sdks: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an SDKNotFoundError.

        Args:
            sdk_name: Name of SDK that was not found
            available_sdks: List of available SDK names (if known)
            context: Optional additional context
        """
        self.sdk_name = sdk_name
        self.available_sdks = available_sdks or []

        error_context = {
            "sdk_name": sdk_name,
            "available_sdks": self.available_sdks,
        }
        if context:
            error_context.update(context)

        super().__init__(
            message=f"SDK not found: {sdk_name}",
            error_code="SDK_NOT_FOUND",
            context=error_context,
            operation="get_sdk",
            sdk_name=sdk_name,
        )


class SDKMethodNotFoundError(SDKGatewayError):
    """Raised when requested SDK method is not found.

    Example:
        >>> raise SDKMethodNotFoundError(
    ...     sdk_name="processor",
    ...     method="nonexistent_method",
    ...     available_methods=["process", "analyze", "validate"]
    ... )
    """

    def __init__(
        self,
        sdk_name: str,
        method: str,
        available_methods: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an SDKMethodNotFoundError.

        Args:
            sdk_name: Name of SDK instance
            method: Method name that was not found
            available_methods: List of available method names (if known)
            context: Optional additional context
        """
        self.method = method
        self.available_methods = available_methods or []

        error_context = {
            "sdk_name": sdk_name,
            "method": method,
            "available_methods": self.available_methods,
        }
        if context:
            error_context.update(context)

        super().__init__(
            message=f"SDK method not found: {sdk_name}.{method}",
            error_code="SDK_METHOD_NOT_FOUND",
            context=error_context,
            sdk_name=sdk_name,
            operation="execute",
            method=method,
        )


class SDKTimeoutError(SDKGatewayError):
    """Raised when SDK operation times out.

    Example:
        >>> raise SDKTimeoutError(
        ...     sdk_name="processor",
        ...     method="process_large_dataset",
        ...     timeout_seconds=30
        ... )
    """

    def __init__(
        self,
        message: str,
        sdk_name: Optional[str] = None,
        method: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize an SDKTimeoutError.

        Args:
            message: Human-readable error description
            sdk_name: Name of SDK instance
            method: Method that timed out
            timeout_seconds: Timeout duration in seconds
            context: Optional additional context
        """
        self.timeout_seconds = timeout_seconds

        error_context = {"timeout_seconds": timeout_seconds} if timeout_seconds else {}
        if context:
            error_context.update(context)

        super().__init__(
            message=message or f"SDK operation timed out after {timeout_seconds}s",
            error_code="SDK_TIMEOUT_ERROR",
            context=error_context,
            sdk_name=sdk_name,
            operation="execute",
            method=method,
        )


__all__ = [
    'SDKGatewayError',
    'SDKInitializationError',
    'SDKExecutionError',
    'SDKConfigurationError',
    'SDKNotFoundError',
    'SDKMethodNotFoundError',
    'SDKTimeoutError',
]
