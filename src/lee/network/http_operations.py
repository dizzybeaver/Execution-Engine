"""network/http_operations.py

Gateway HTTP operations with circuit breaker protection and SSRF validation.

Migrated from: http_client/http_client_operations.py
Enhanced with: CRLF protection, SSRF validation

Version: 2.0.0 (2026-03-07)
Security: SSRF protection added (CVSS 8.5 → <2.0)
License: Apache 2.0
"""

import os
from typing import Any, Optional

# Type aliases for better code documentation (must be defined before use)
CorrelationID = Optional[str]
HTTPResponse = dict[str, Any]
HTTPMethod = str | bytes
HTTPHeaders = Optional[dict[str, str]]
HTTPJSON = Optional[dict[str, Any]]
HTTPData = str | bytes | Optional[dict[str, Any]]
HTTPTimeout = Optional[float]
HTTPParams = Optional[dict[str, Any]]

# Gateway imports for cross-cutting concerns
from lee.circuit_breaker.circuit_breaker_config import (
    CircuitBreakerConfig,
    get_alexa_ha_api_config,
)
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# Configuration constants
from lee.lee_config.constants import (
    HTTP_BACKOFF_FACTOR,
    HTTP_DEFAULT_TIMEOUT,
    HTTP_LONG_TIMEOUT,
    HTTP_MAX_REDIRECTS,
    HTTP_MAX_RETRIES,
)

# Use new network factory for HTTP client
from lee.network.http_core import HttpClient

# SSRF protection
from lee.network.ssrf_protect import validate_url


def _build_error_response(
    error: Exception,
    method: str,
    url: str,
    correlation_id: CorrelationID,
) -> HTTPResponse:
    """Build standardized HTTP error response."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="_build_error_response ENTRY",
            error_type=type(error).__name__,
            error=str(error),
        )
    result = {
        "success": False,
        "error": str(error),
        "method": method,
        "url": url,
        "correlation_id": str(correlation_id),
    }
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="_build_error_response EXIT",
        )
    return result


_http_client: Optional[HttpClient] = None


def _get_http_client() -> HttpClient:
    """Get or create singleton HTTP client."""
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=None, scope="HTTP_OPERATIONS",
            message="_get_http_client ENTRY",
        )
    global _http_client  # pylint: disable=global-statement

    if _http_client is None:
        # For AWS Lambda: Read from environment variable
        # For local testing: .env file should set this via environment variable
        verify_ssl_env = os.getenv("HOME_ASSISTANT_VERIFY_SSL", "true").lower()
        verify_ssl = verify_ssl_env != "false"

        _http_client = HttpClient(
            timeout=HTTP_DEFAULT_TIMEOUT,
            verify_ssl=verify_ssl,
            max_retries=HTTP_MAX_RETRIES,
            backoff_factor=HTTP_BACKOFF_FACTOR,
            max_redirects=HTTP_MAX_REDIRECTS,
        )
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=None, scope="HTTP_OPERATIONS",
                message="_get_http_client - created new HttpClient",
                verify_ssl=verify_ssl,
            )

    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=None, scope="HTTP_OPERATIONS",
            message="_get_http_client EXIT",
        )
    return _http_client


def _validate_circuit_breaker_config(config) -> bool:
    """Validate circuit breaker configuration.

        config: CircuitBreakerConfig instance to validate

        True if valid, False otherwise

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=None, scope="HTTP_OPERATIONS",
            message="_validate_circuit_breaker_config ENTRY",
        )
    try:
        # Validate failure_threshold
        if getattr(config, "failure_threshold", None) is None:
            execute_operation(
                GatewayInterface.LOGGING, "log_warning",
                message="Circuit breaker config missing failure_threshold, "
                        "using defaults",
            )
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, "log",
                    corr_id=None, scope="HTTP_OPERATIONS",
                    message="_validate_circuit_breaker_config - missing failure_threshold",
                )
            return False

        if config.failure_threshold <= 0 or config.failure_threshold > 1000:
            execute_operation(
                GatewayInterface.LOGGING, "log_warning",
                message=f"Invalid failure_threshold: {config.failure_threshold}, "
                        f"must be 1-1000, using defaults",
            )
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, "log",
                    corr_id=None, scope="HTTP_OPERATIONS",
                    message="_validate_circuit_breaker_config - invalid failure_threshold",
                )
            return False

        # Validate timeout
        if getattr(config, "timeout", None) is None:
            execute_operation(
                GatewayInterface.LOGGING, "log_warning",
                message="Circuit breaker config missing timeout, using defaults",
            )
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, "log",
                    corr_id=None, scope="HTTP_OPERATIONS",
                    message="_validate_circuit_breaker_config - missing timeout",
                )
            return False

        if config.timeout <= 0 or config.timeout > 3600:
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, "log",
                    corr_id=None, scope="HTTP_OPERATIONS",
                    message="_validate_circuit_breaker_config - invalid timeout",
                )
            return False

        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=None, scope="HTTP_OPERATIONS",
                message="_validate_circuit_breaker_config EXIT - valid",
            )
        return True

    except (AttributeError, TypeError, ValueError) as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_warning",
            message=f"Config validation failed: {e}, using defaults",
        )
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=None, scope="HTTP_OPERATIONS",
                message="_validate_circuit_breaker_config EXIT - exception",
            )
        return False


def _ensure_http_circuit_breaker() -> None:
    """Ensure HTTP client circuit breaker is registered with proper configuration.

    This pre-registers the 'http_client' circuit breaker with Alexa HA API config
    (5 failures, 60s timeout) to ensure it's created with the correct settings
    on first use.
    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=None, scope="HTTP_OPERATIONS",
            message="_ensure_http_circuit_breaker ENTRY",
        )

    try:
        # Get expected config
        expected_config = get_alexa_ha_api_config()

        # Validate configuration
        if not _validate_circuit_breaker_config(expected_config):
            execute_operation(
                GatewayInterface.LOGGING, "log_warning",
                message="HTTP client circuit breaker config validation failed, "
                        "using safe defaults",
            )
            # Use safe defaults
            expected_config = CircuitBreakerConfig(
                failure_threshold=5,
                timeout=HTTP_LONG_TIMEOUT,
            )

        # Pre-register circuit breaker with validated config
        execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            "get",
            name="http_client",
            config=expected_config,
        )

        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id="http_preregister", scope="HTTP",
            message="HTTP client circuit breaker pre-registered",
            failure_threshold=expected_config.failure_threshold,
            timeout=expected_config.timeout,
        )

        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=None, scope="HTTP_OPERATIONS",
                message="_ensure_http_circuit_breaker EXIT - success",
            )

    except (AttributeError, KeyError, RuntimeError, ConnectionError) as e:
        # If pre-registration fails, circuit breaker will be created
        # with defaults on first use (acceptable fallback)
        execute_operation(
            GatewayInterface.LOGGING, "log_warning",
            message=f"HTTP client circuit breaker pre-registration failed: {e}, "
                    f"will use defaults on first use",
        )
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=None, scope="HTTP_OPERATIONS",
                message="_ensure_http_circuit_breaker EXIT - exception",
            )


def _make_http_request(method: str, url: str, correlation_id: str = None,
                      **kwargs) -> dict[str, Any]:
    """Execute HTTP request via network factory with circuit breaker protection.

        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Request URL
        correlation_id: Optional correlation ID for tracking
        **kwargs: Additional request parameters

        Response dict with success, data, status_code, etc.

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="_make_http_request ENTRY",
            method=method,
            url=url[:100],
        )

    # Extract timeout for logging
    request_timeout = kwargs.get("timeout")
    if debug_enabled and request_timeout:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message=f"_make_http_request - timeout={request_timeout}s",
        )
    # Ensure circuit breaker is registered with proper config
    _ensure_http_circuit_breaker()

    try:
        validate_url(url)
    except ValueError as e:
        if correlation_id is None:
            correlation_id = generate_correlation_id("http")

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HTTP",
                         message="SSRF validation failed", url=str(url)[:100])

        return {
            "success": False,
            "error": str(e),
            "error_type": "SSRFValidationError",
            "url": url,
        }

    # SUGA-ISP compliance - route through gateway

    if correlation_id is None:
        correlation_id = generate_correlation_id("http")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="HTTP",
                     message=f"HTTP {method} request", url=url[:100])

    # Define the actual HTTP request function to be protected by circuit breaker
    def _execute_request():
        """Inner function that executes the actual HTTP request."""
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=correlation_id, scope="HTTP_OPERATIONS",
                message="_execute_request ENTRY",
            )
        client = _get_http_client()

        # Extract parameters
        headers = kwargs.get("headers")
        json_data = kwargs.get("json")
        data = kwargs.get("data")
        timeout = kwargs.get("timeout")
        params = kwargs.get("params")
        stream = kwargs.get("stream", False)

        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=correlation_id, scope="HTTP_OPERATIONS",
                message=f"_execute_request - timeout={timeout}, stream={stream}",
            )

        # Execute request with timing
        with execute_operation(GatewayInterface.DEBUG, "timing",
                              corr_id=correlation_id, scope="HTTP",
                              operation=f"{method} {url[:50]}"):
            response = client.request(
                method,
                url,
                headers=headers,
                json=json_data,
                data=data,
                timeout=timeout,
                params=params,
                stream=stream,
                allow_redirects=True,
            )

        # Use unified response-to-dict conversion
        result = response.to_dict(include_content=not stream)

        # Handle streaming responses
        if stream:
            result["data"] = None  # Streaming, caller uses iter_content

        execute_operation(GatewayInterface.DEBUG, "log",
                         corr_id=correlation_id, scope="HTTP",
                         message="Request completed", status=response.status,
                         success=response.ok)

        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=correlation_id, scope="HTTP_OPERATIONS",
                message="_execute_request EXIT",
            )
        return result

    # Execute request with circuit breaker protection
    try:
        result = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            "call",
            name="http_client",
            func=_execute_request,
        )
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=correlation_id, scope="HTTP_OPERATIONS",
                message="_make_http_request EXIT - success",
            )
        return result
    except (ConnectionError, TimeoutError, OSError) as e:
        # Enhanced error handling for network-related errors
        error_response = _build_error_response(
            error=e,
            method=method,
            url=url,
            correlation_id=correlation_id,
        )

        # Log with full context
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message=f"HTTP request failed: {e!s}",
            error=str(e),
            error_type=type(e).__name__,
            circuit_state=error_response.get("circuit_state", "unknown"),
            is_retriable=error_response.get("is_retriable", False),
        )

        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP",
            message="Request failed",
            error=str(e),
            error_type=type(e).__name__,
            circuit_state=error_response.get("circuit_state"),
            is_retriable=error_response.get("is_retriable"),
        )

        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=correlation_id, scope="HTTP_OPERATIONS",
                message="_make_http_request EXIT - network error",
            )
        return error_response
    except (AttributeError, KeyError, RuntimeError, ValueError, TypeError) as e:
        # Catch specific expected errors from HTTP operations
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message=f"HTTP request operation error: {e!s}",
            error=str(e),
            error_type=type(e).__name__,
        )
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=correlation_id, scope="HTTP_OPERATIONS",
                message="_make_http_request EXIT - operation error",
            )
        return _build_error_response(
            error=e,
            method=method,
            url=url,
            correlation_id=correlation_id,
        )


def _build_enhanced_error_response(
    error: Exception,
    method: str,
    url: str,
    correlation_id: CorrelationID,
) -> dict[str, Any]:
    """Build enhanced error response with circuit state and context.

        error: The exception that occurred
        method: HTTP method
        url: Request URL
        correlation_id: Correlation ID for tracking

        Enhanced error response dict

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="_build_enhanced_error_response ENTRY",
            error_type=type(error).__name__,
        )
    # Get circuit state if available
    circuit_state = "unknown"
    failure_count = 0
    last_failure_time = None

    try:
        breaker = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            "get",
            name="http_client",
        )
        if breaker:
            circuit_state = breaker.state.name
            failure_count = breaker.failure_count
            last_failure_time = getattr(breaker, "last_failure_time", None)
            if debug_enabled:
                execute_operation(
                    GatewayInterface.DEBUG, "log",
                    corr_id=correlation_id, scope="HTTP_OPERATIONS",
                    message="_build_enhanced_error_response - got circuit state",
                    circuit_state=circuit_state,
                    failure_count=failure_count,
                )
    except (AttributeError, KeyError, RuntimeError) as e:
        # Circuit breaker unavailable or misconfigured - continue with unknown state
        execute_operation(
            GatewayInterface.LOGGING, "log_warning",
            message=f"Failed to get circuit breaker state: {e}",
            error=str(e),
        )

    # Determine if error is retriable
    is_retriable = isinstance(error, (TimeoutError, ConnectionError))

    # Build enhanced error response
    result = {
        "success": False,
        "error": str(error),
        "error_type": type(error).__name__,
        "circuit_state": circuit_state,
        "is_retriable": is_retriable,
        "request_context": {
            "method": method,
            "url": url[:100] if url else "",  # Truncate long URLs
            "correlation_id": correlation_id or "not_provided",
        },
        "circuit_context": {
            "failure_count": failure_count,
            "last_failure_time": last_failure_time,
        } if last_failure_time else None,
    }
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="_build_enhanced_error_response EXIT",
        )
    return result


def get_http_circuit_state() -> dict[str, Any]:
    """Get HTTP client circuit breaker state.

        Dict containing circuit state information:
        - state: Current circuit state (CLOSED, OPEN, HALF_OPEN)
        - failure_count: Number of failures recorded
        - last_failure_time: Timestamp of last failure (if any)
        - failure_threshold: Threshold for tripping circuit
        - timeout: Timeout in seconds before attempting recovery

    Example:
        >>> state = get_http_circuit_state()
        >>> print(state['state'])  # 'CLOSED'
        >>> print(state['failure_count'])  # 0

    """
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=None, scope="HTTP_OPERATIONS",
            message="get_http_circuit_state ENTRY",
        )

    try:
        breaker = execute_operation(
            GatewayInterface.CIRCUIT_BREAKER,
            "get",
            name="http_client",
        )

        result = {
            "success": True,
            "state": breaker.state.name,
            "failure_count": breaker.failure_count,
            "last_failure_time": getattr(breaker, "last_failure_time", None),
            "failure_threshold": breaker.failure_threshold,
            "timeout": breaker.timeout,
        }
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=None, scope="HTTP_OPERATIONS",
                message="get_http_circuit_state EXIT - success",
                state=result["state"],
            )
        return result

    except (AttributeError, KeyError, RuntimeError, ConnectionError) as e:
        result = {
            "success": False,
            "error": f"Failed to get circuit state: {e!s}",
            "state": "unknown",
            "failure_count": 0,
            "last_failure_time": None,
        }
        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=None, scope="HTTP_OPERATIONS",
                message="get_http_circuit_state EXIT - exception",
            )
        return result


def http_request_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for HTTP request.

        **kwargs: Request parameters including method, url, correlation_id

        HTTP response dict with success, data, status_code, etc.

    """
    method: str = kwargs.pop("method", "GET")
    url: str = kwargs.pop("url", "")
    correlation_id: CorrelationID = kwargs.pop("correlation_id", None)
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_request_implementation ENTRY",
            method=method,
            url=url[:100],
        )
    result = _make_http_request(method, url, correlation_id, **kwargs)
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_request_implementation EXIT",
            success=result.get("success", False),
        )
    return result


def http_get_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for HTTP GET.

        **kwargs: Request parameters including url, correlation_id

        HTTP response dict with success, data, status_code, etc.

    """
    url: str = kwargs.pop("url", "")
    correlation_id: CorrelationID = kwargs.pop("correlation_id", None)
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_get_implementation ENTRY",
            url=url[:100],
        )
    result = _make_http_request("GET", url, correlation_id, **kwargs)
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_get_implementation EXIT",
            success=result.get("success", False),
        )
    return result


def http_post_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for HTTP POST.

        **kwargs: Request parameters including url, correlation_id

        HTTP response dict with success, data, status_code, etc.

    """
    url: str = kwargs.pop("url", "")
    correlation_id: CorrelationID = kwargs.pop("correlation_id", None)
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_post_implementation ENTRY",
            url=url[:100],
        )
    result = _make_http_request("POST", url, correlation_id, **kwargs)
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_post_implementation EXIT",
            success=result.get("success", False),
        )
    return result


def http_put_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for HTTP PUT.

        **kwargs: Request parameters including url, correlation_id

        HTTP response dict with success, data, status_code, etc.

    """
    url: str = kwargs.pop("url", "")
    correlation_id: CorrelationID = kwargs.pop("correlation_id", None)
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_put_implementation ENTRY",
            url=url[:100],
        )
    result = _make_http_request("PUT", url, correlation_id, **kwargs)
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_put_implementation EXIT",
            success=result.get("success", False),
        )
    return result


def http_delete_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for HTTP DELETE.

    Args:
        **kwargs: Request parameters including url, correlation_id

    Returns:
        HTTP response dict with success, data, status_code, etc.
    """
    url: str = kwargs.pop("url", "")
    correlation_id: CorrelationID = kwargs.pop("correlation_id", None)
    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_delete_implementation ENTRY",
            url=url[:100],
        )
    result = _make_http_request("DELETE", url, correlation_id, **kwargs)
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_delete_implementation EXIT",
            success=result.get("success", False),
        )
    return result


def http_reset_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for HTTP client reset.

    Args:
        **kwargs: Optional correlation_id

    Returns:
        Response dict indicating success/failure
    """

    correlation_id: CorrelationID = kwargs.pop(
        "correlation_id",
        generate_correlation_id("http"),
    )

    execute_operation(
        GatewayInterface.DEBUG, "log",
        corr_id=correlation_id, scope="HTTP_OPERATIONS",
        message="http_reset_implementation ENTRY - HTTP client reset requested",
    )

    try:
        global _http_client  # pylint: disable=global-statement
        if _http_client is not None:
            _http_client.close()
            _http_client = None

        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="http_reset_implementation - HTTP client reset successful",
        )

        return {
            "success": True,
            "message": "HTTP client reset successful",
        }
    except (ConnectionError, OSError) as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message=f"HTTP client reset failed: {e!s}",
            error=str(e),
        )
        return {
            "message": f"HTTP client reset failed: {e!s}",
        }
    except (AttributeError, RuntimeError, ValueError) as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message=f"HTTP client reset operation error: {e!s}",
            error=str(e),
            error_type=type(e).__name__,
        )
        return {
            "message": f"HTTP client reset failed: {e!s}",
        }


def get_state_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for get state.

    Args:
        **kwargs: Optional correlation_id

    Returns:
        HTTP client state information
    """

    correlation_id: CorrelationID = kwargs.pop(
        "correlation_id",
        generate_correlation_id("http"),
    )

    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    execute_operation(
        GatewayInterface.DEBUG, "log",
        corr_id=correlation_id, scope="HTTP_OPERATIONS",
        message="get_state_implementation ENTRY - Getting HTTP client state",
    )

    result = {
        "success": True,
        "data": {
            "client_exists": _http_client is not None,
            # For AWS Lambda: Read from environment variable
            # For local testing: .env file should set this via environment variable
            "verify_ssl": os.getenv("HOME_ASSISTANT_VERIFY_SSL", "true").lower() != "false",
        },
    }
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="get_state_implementation EXIT",
            client_exists=result["data"]["client_exists"],
        )
    return result


def reset_state_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for reset state.

    Args:
        **kwargs: Optional correlation_id

    Returns:
        Response dict indicating success/failure
    """
    return http_reset_implementation(**kwargs)


def get_http_circuit_state_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for getting HTTP circuit breaker state.

    Args:
        **kwargs: Optional correlation_id

    Returns:
        Circuit breaker state information

        >>> result = get_http_circuit_state_implementation()
        >>> print(result['state'])  # 'CLOSED'
        >>> print(result['failure_count'])  # 0

    """
    correlation_id: CorrelationID = kwargs.pop(
        "correlation_id",
        generate_correlation_id("http"),
    )

    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="get_http_circuit_state_implementation ENTRY",
        )

    result = get_http_circuit_state()

    # Log circuit state query
    execute_operation(
        GatewayInterface.DEBUG, "log",
        corr_id=correlation_id, scope="HTTP_OPERATIONS",
        message="get_http_circuit_state_implementation - HTTP circuit state queried",
        circuit_state=result.get("state", "unknown"),
        failure_count=result.get("failure_count", 0),
    )

    if debug_enabled:
        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="get_http_circuit_state_implementation EXIT",
        )
    return result


def configure_retry_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for configure retry.

    Args:
        **kwargs: Optional max_retries, backoff_factor, correlation_id

    Returns:
        Response dict indicating success/failure

    Example:
        >>> result = configure_retry_implementation(max_retries=3, backoff_factor=1.0)
        >>> print(result['success'])  # True
    """

    correlation_id: CorrelationID = kwargs.pop(
        "correlation_id",
        generate_correlation_id("http"),
    )

    max_retries = kwargs.pop("max_retries", None)
    backoff_factor = kwargs.pop("backoff_factor", None)

    execute_operation(
        GatewayInterface.DEBUG, "log",
        corr_id=correlation_id, scope="HTTP_OPERATIONS",
        message="configure_retry_implementation ENTRY - Configuring HTTP retry policy",
        max_retries=max_retries,
        backoff_factor=backoff_factor,
    )

    try:
        client = _get_http_client()
        client.configure_retry(
            max_retries=max_retries,
            backoff_factor=backoff_factor,
        )

        execute_operation(
            GatewayInterface.DEBUG, "log",
            corr_id=correlation_id, scope="HTTP_OPERATIONS",
            message="configure_retry_implementation - HTTP retry policy configured successfully",
        )

        return {
            "success": True,
            "message": "HTTP retry policy configured successfully",
            "config": {
                "max_retries": client.max_retries,
                "backoff_factor": client.backoff_factor,
            },
        }

    except (AttributeError, ValueError, TypeError) as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message=f"Failed to configure HTTP retry policy: {e!s}",
            error=str(e),
        )

        return {
            "success": False,
            "message": f"Failed to configure HTTP retry policy: {e!s}",
        }
    except (OSError, MemoryError) as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message=f"Unexpected error in configure retry: {e!s}",
            error=str(e),
            error_type=type(e).__name__,
        )

        return {
            "success": False,
            "message": f"Failed to configure HTTP retry policy: {e!s}",
        }


def get_statistics_implementation(**kwargs) -> HTTPResponse:
    """Gateway implementation for getting HTTP client statistics.

    Args:
        **kwargs: Optional correlation_id

    Returns:
        HTTP client statistics

    Example:
        >>> result = get_statistics_implementation()
        >>> print(result['data']['requests_total'])  # 1234
        >>> print(result['data']['requests_successful'])  # 1200
    """

    correlation_id: CorrelationID = kwargs.pop(
        "correlation_id",
        generate_correlation_id("http"),
    )

    debug_enabled = os.environ.get("LEE_DEBUG", "false").lower() == "true"
    execute_operation(
        GatewayInterface.DEBUG, "log",
        corr_id=correlation_id, scope="HTTP_OPERATIONS",
        message="get_statistics_implementation ENTRY - Getting HTTP client statistics",
    )

    try:
        client = _get_http_client()
        stats = client.get_statistics()

        if debug_enabled:
            execute_operation(
                GatewayInterface.DEBUG, "log",
                corr_id=correlation_id, scope="HTTP_OPERATIONS",
                message="get_statistics_implementation EXIT - success",
            )

        return {
            "success": True,
            "data": stats,
        }

    except (AttributeError, KeyError) as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message=f"Failed to get HTTP client statistics: {e!s}",
            error=str(e),
        )

        return {
            "success": False,
            "message": f"Failed to get HTTP client statistics: {e!s}",
            "data": {},
        }
    except (OSError, MemoryError) as e:
        execute_operation(
            GatewayInterface.LOGGING, "log_error",
            message=f"Unexpected error in get statistics: {e!s}",
            error=str(e),
            error_type=type(e).__name__,
        )

        return {
            "success": False,
            "message": f"Failed to get HTTP client statistics: {e!s}",
            "data": {},
        }


__all__ = [
    "_build_error_response",
    "_validate_circuit_breaker_config",
    "configure_retry_implementation",
    "get_http_circuit_state",
    "get_http_circuit_state_implementation",
    "get_state_implementation",
    "get_statistics_implementation",
    "http_delete_implementation",
    "http_get_implementation",
    "http_post_implementation",
    "http_put_implementation",
    "http_request_implementation",
    "http_reset_implementation",
    "reset_state_implementation",
]
