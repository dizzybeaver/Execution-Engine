# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-03-26 - Implement retry logic for device discovery

"""ha_discovery_retry.py - Device Discovery Retry Logic

Provides retry mechanism with exponential backoff for Home Assistant device
discovery operations to handle transient failures (network issues, HA restarts).

Retry Strategy:
- Maximum 3 retry attempts
- Exponential backoff: 1s, 2s, 4s
- Retriable errors: ConnectionError, TimeoutError, HTTP 5xx
- Non-retriable errors: Authentication, validation, HTTP 4xx (except 429)
"""

import random
import time
from typing import Any, Optional
from collections.abc import Callable

from lee.gateway import GatewayInterface, execute_operation

# Retriable exception types
RETRIABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
)

# Maximum retry attempts
MAX_RETRIES = 3

# Base backoff time in seconds
BASE_BACKOFF = 1.0


def is_retriable_error(error: Exception, response: Optional[dict] = None) -> bool:
    """Check if error is retriable.

    Args:
        error: Exception that occurred
        response: Optional response dict for HTTP errors

    Returns:
        True if error should be retried
    """
    # Check exception type
    if isinstance(error, RETRIABLE_EXCEPTIONS):
        return True

    # Check HTTP status codes in response
    if response and isinstance(response, dict):
        status_code = response.get("status_code") or response.get("code")
        if status_code:
            # Retry on server errors (5xx) and rate limiting (429)
            if 500 <= status_code < 600 or status_code == 429:
                return True

    return False


def retry_discovery_operation(
    operation: Callable,
    operation_name: str = "discovery",
    correlation_id: str = None,
    **kwargs
) -> dict[str, Any]:
    """Execute discovery operation with retry logic.

    Args:
        operation: Function to execute (should accept **kwargs)
        operation_name: Name of operation for logging
        correlation_id: Optional correlation ID for tracking
        **kwargs: Parameters to pass to operation

    Returns:
        Dict with success status and result

    Example:
        >>> result = retry_discovery_operation(
        ...     operation=ha_execute_operation,
        ...     operation_name="device_discovery",
        ...     interface=HAGatewayInterface.ALEXA,
        ...     operation_type="discovery",
        ...     event=event
        ... )
    """
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            # Execute operation
            result = operation(**kwargs)

            # Check if result indicates failure
            if isinstance(result, dict):
                if result.get("success") is False:
                    # Check if error is retriable
                    error_msg = result.get("error", "")
                    error = Exception(error_msg)

                    if is_retriable_error(error, result) and attempt < MAX_RETRIES:
                        last_error = error
                        # Add jitter to prevent thundering herd during HA recovery (10% +/-)
                        backoff = BASE_BACKOFF * (2 ** attempt)
                        backoff = backoff * random.uniform(0.9, 1.1)

                        execute_operation(
                            GatewayInterface.LOGGING,
                            "log_warning",
                            message=f"{operation_name} attempt {attempt + 1} failed, retrying in {backoff}s",
                            corr_id=correlation_id,
                            extra_context={
                                "operation": operation_name,
                                "attempt": attempt + 1,
                                "max_retries": MAX_RETRIES + 1,
                                "error": error_msg,
                                "backoff_seconds": backoff,
                            }
                        )

                        time.sleep(backoff)
                        continue

                    # Non-retriable error or last attempt failed
                    execute_operation(
                        GatewayInterface.LOGGING,
                        "log_error",
                        message=f"{operation_name} failed after {attempt + 1} attempts",
                        corr_id=correlation_id,
                        extra_context={
                            "operation": operation_name,
                            "attempts": attempt + 1,
                            "error": error_msg,
                        }
                    )

                    return result

            # Success or non-dict result
            if attempt > 0:
                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_info",
                    message=f"{operation_name} succeeded on attempt {attempt + 1}",
                    corr_id=correlation_id,
                    extra_context={
                        "operation": operation_name,
                        "attempt": attempt + 1,
                    }
                )

            return result

        except (ConnectionError, TimeoutError, OSError) as e:
            last_error = e

            # Check if exception is retriable
            if is_retriable_error(e, None) and attempt < MAX_RETRIES:
                # Add jitter to prevent thundering herd during HA recovery (10% +/-)
                backoff = BASE_BACKOFF * (2 ** attempt)
                backoff = backoff * random.uniform(0.9, 1.1)

                execute_operation(
                    GatewayInterface.LOGGING,
                    "log_warning",
                    message=f"{operation_name} raised {type(e).__name__}, retrying in {backoff}s",
                    corr_id=correlation_id,
                    extra_context={
                        "operation": operation_name,
                        "attempt": attempt + 1,
                        "exception_type": type(e).__name__,
                        "error": str(e),
                        "backoff_seconds": backoff,
                    }
                )

                time.sleep(backoff)
                continue

            # Non-retriable exception or last attempt failed
            execute_operation(
                GatewayInterface.LOGGING,
                "log_error",
                message=f"{operation_name} failed with {type(e).__name__} after {attempt + 1} attempts",
                corr_id=correlation_id,
                extra_context={
                    "operation": operation_name,
                    "attempts": attempt + 1,
                    "exception_type": type(e).__name__,
                    "error": str(e),
                }
            )

            return {
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}",
                "error_code": type(e).__name__,
                "attempts": attempt + 1,
            }

    # Should never reach here, but handle gracefully
    return {
        "success": False,
        "error": f"Retry exhausted: {last_error}",
        "error_code": "RETRY_EXHAUSTED",
        "attempts": MAX_RETRIES + 1,
    }


__all__ = [
    "retry_discovery_operation",
    "is_retriable_error",
    "MAX_RETRIES",
    "BASE_BACKOFF",
]
