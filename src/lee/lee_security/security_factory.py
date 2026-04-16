# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Create generic factory for singleton method calls

"""security/security_factory.py

Version: 2026-04-11_1
Purpose: Generic factory for singleton security operations
License: Apache 2.0

Provides generic factory pattern to eliminate duplicate singleton convenience
functions across security module. Reduces code duplication from 200+ lines to
single factory function with configurable operations.

Factory Pattern Benefits:
- Eliminates 200+ lines of duplicate code
- Centralized correlation ID handling
- Consistent debug logging
- Easy to add new operations
- Single point of maintenance

Usage Example:
    # Before (25 lines per function):
    def validate_token_implementation(
        token: str, correlation_id: str = None, **kwargs
    ) -> bool:
        GatewayInterface, execute_operation = _get_gateway()
        if correlation_id is None:
            correlation_id = generate_correlation_id("sec")
        execute_operation(GatewayInterface.DEBUG, "log", ...)
        return get_security_manager().execute_security_operation(...)

    # After (1 line using factory):
    validate_token_implementation = create_security_function_factory(
        SecurityOperation.VALIDATE_TOKEN,
        "validate_token_implementation"
    )
"""

from typing import Any, Callable, Optional


# Lazy imports to avoid circular dependency
_gateway_imported = False
_GatewayInterface = None
_execute_operation = None
_generate_correlation_id = None


def _get_gateway():
    """Lazy import gateway functions to avoid circular dependency.

    Returns:
        Tuple of (GatewayInterface, execute_operation, generate_correlation_id)
    """
    global _gateway_imported
    global _GatewayInterface, _execute_operation, _generate_correlation_id

    if not _gateway_imported:
        try:
            from lee.gateway import GatewayInterface, execute_operation  # pylint: disable=import-outside-toplevel
            from lee.gateway.gateway_core import generate_correlation_id  # pylint: disable=import-outside-toplevel
            _GatewayInterface = GatewayInterface
            _execute_operation = execute_operation
            _generate_correlation_id = generate_correlation_id
            _gateway_imported = True
        except ImportError:
            _GatewayInterface = None
            _execute_operation = None
            _generate_correlation_id = None

    return _GatewayInterface, _execute_operation, _generate_correlation_id


def _ensure_correlation_id(correlation_id: Optional[str] = None,
                           prefix: str = "sec") -> str:
    """Ensure correlation_id exists, generating one if needed.

    Args:
        correlation_id: Optional correlation ID
        prefix: Prefix for generated correlation ID

    Returns:
        correlation_id (generated if None)
    """
    if correlation_id is not None:
        return correlation_id

    _GatewayInterface, _execute_operation, generate_correlation_id = _get_gateway()
    if generate_correlation_id is not None:
        return generate_correlation_id(prefix)

    import time
    import random
    return f"{prefix}_{int(time.time() * 1000)}_{random.randbytes(4).hex()}"


def _log_operation(operation_name: str, correlation_id: str,
                   log_params: dict[str, Any] = None) -> None:
    """Log security operation if gateway available.

    Args:
        operation_name: Name of operation being logged
        correlation_id: Correlation ID for tracking
        log_params: Additional log parameters
    """
    _GatewayInterface, execute_operation, _generate_correlation_id = _get_gateway()

    if _GatewayInterface and execute_operation:
        params = {
            "corr_id": correlation_id,
            "scope": "SECURITY",
            "message": f"{operation_name} called",
        }
        if log_params:
            params.update(log_params)
        execute_operation(_GatewayInterface.DEBUG, "log", **params)


def create_security_function_factory(
    operation: Any,
    function_name: str,
    log_params_factory: Optional[Callable] = None,
    custom_impl: Optional[Callable] = None,
) -> Callable:
    """Generic factory for creating security implementation functions.

    Eliminates duplicate singleton convenience functions by providing a
    standardized pattern for all security operations.

    Args:
        operation: SecurityOperation enum value for this operation
        function_name: Name of function (for logging and debug tracking)
        log_params_factory: Optional callable that creates log parameters from kwargs
            Signature: (kwargs) -> dict[str, Any]
            If None, uses default empty params
        custom_impl: Optional custom implementation instead of manager call
            Signature: (correlation_id, **kwargs) -> result
            If provided, bypasses manager.execute_security_operation()

    Returns:
        Implementation function with standard correlation_id handling

    Example:
        # Simple operation (passes through to manager)
        validate_token_implementation = create_security_function_factory(
            SecurityOperation.VALIDATE_TOKEN,
            "validate_token_implementation"
        )

        # Operation with custom log parameters
        validate_string_implementation = create_security_function_factory(
            SecurityOperation.VALIDATE_STRING,
            "validate_string_implementation",
            log_params_factory=lambda kw: {
                "value_length": len(kw.get("value", "")),
                "min_length": kw.get("min_length", 0),
                "max_length": kw.get("max_length", 1000)
            }
        )

        # Operation with custom implementation
        compare_tokens_implementation = create_security_function_factory(
            None,  # No operation enum for custom impl
            "compare_tokens_implementation",
            custom_impl=lambda corr_id, **kw: _compare_tokens(
                kw["token1"],
                kw["token2"]
            )
        )

    Factory Function Behavior:
    1. Ensures correlation_id exists (generates if None)
    2. Logs operation call with parameters
    3. Executes operation (via manager or custom_impl)
    4. Returns result

    All factory-generated functions are backward compatible with existing code.
    """
    def impl(correlation_id: str = None, **kwargs) -> Any:
        # Step 1: Ensure correlation_id
        correlation_id = _ensure_correlation_id(correlation_id)

        # Step 2: Log operation
        log_params = {}
        if log_params_factory is not None:
            try:
                log_params = log_params_factory(kwargs)
            except (KeyError, TypeError, AttributeError):
                pass  # Use empty params if factory fails
        _log_operation(function_name, correlation_id, log_params)

        # Step 3: Execute operation
        if custom_impl is not None:
            # Use custom implementation
            return custom_impl(correlation_id, **kwargs)
        else:
            # Use manager.execute_security_operation
            from lee.lee_security.security_manager import get_security_manager  # pylint: disable=import-outside-toplevel
            manager = get_security_manager()

            # Extract operation-specific parameters from kwargs
            # Manager expects: (operation, correlation_id, *args, **kwargs)
            # We need to separate args from kwargs based on operation type
            args = []
            if operation.value in ("validate_token", "validate_email", "validate_url",
                                  "validate_cache_key", "validate_module_name"):
                # Single parameter operations
                param_key = {
                    "validate_token": "token",
                    "validate_email": "email",
                    "validate_url": "url",
                    "validate_cache_key": "key",
                    "validate_module_name": "module_name"
                }.get(operation.value)
                if param_key and param_key in kwargs:
                    args.append(kwargs[param_key])

            elif operation.value == "validate_string":
                # Three parameter operation
                args.extend([
                    kwargs.get("value"),
                    kwargs.get("min_length", 0),
                    kwargs.get("max_length", 1000)
                ])

            elif operation.value == "validate_number_range":
                # Four parameter operation
                args.extend([
                    kwargs.get("value"),
                    kwargs.get("min_val"),
                    kwargs.get("max_val"),
                    kwargs.get("name", "value")
                ])

            elif operation.value in ("hash", "verify_hash"):
                # Hash operations
                args.append(kwargs.get("data"))
                if operation.value == "verify_hash":
                    args.append(kwargs.get("hash_value"))

            elif operation.value == "validate_ttl":
                # TTL operation
                args.append(kwargs.get("ttl"))

            elif operation.value == "sanitize":
                # Sanitize operation
                args.extend([
                    kwargs.get("data"),
                    kwargs.get("level", "medium")
                ])

            # Call manager with operation, correlation_id, and args
            return manager.execute_security_operation(
                operation, correlation_id, *args, **kwargs
            )

    impl.__name__ = function_name
    impl.__doc__ = (
        f"""Execute {
            operation.value if hasattr(operation, 'value') else function_name
        } operation.

    Generated by create_security_function_factory() - eliminates duplicate code.
    """
    )
    return impl


__all__ = [
    "create_security_function_factory",
]
