"""utility/utility_sanitize.py
Version: 2025-12-13_1
Purpose: Sanitization operations for utility interface
License: Apache 2.0
"""

import logging
from typing import TYPE_CHECKING, Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id
from lee.lee_config.constants import STRING_MAX_LENGTH

if TYPE_CHECKING:
    from lee.lee_utility.utility_core import SharedUtilityCore


logger = logging.getLogger(__name__)


class UtilitySanitizeOperations:
    """Sanitization operations for data cleaning and error extraction."""

    def __init__(self, manager: "SharedUtilityCore") -> None:
        """Initialize with reference to SharedUtilityCore manager."""
        self._manager = manager

    def sanitize_data(self, data: dict[str, Any], correlation_id: str = None) -> dict[str, Any]:
        """Sanitize response data by removing sensitive fields."""
        # SUGA-ISP compliant correlation ID generation
        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        sensitive_keys = ["password", "secret", "token", "api_key", "private_key"]

        if not isinstance(data, dict):
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="UTILITY",
                               message="Sanitize skipped: not a dict",
                               data_type=type(data).__name__)
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return data

        sanitized = {}
        redacted_count = 0

        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
                redacted_count += 1
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_data(value, correlation_id)
            else:
                sanitized[key] = value

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                           corr_id=correlation_id, scope="UTILITY",
                           message="Data sanitized",
                           redacted_count=redacted_count, total_keys=len(data))
        except ImportError:
            # Optional dependency - continue if unavailable
            ...

        return sanitized

    def safe_string_conversion(self, data: Any, max_length: int = STRING_MAX_LENGTH,
                              correlation_id: str = None) -> str:
        """Safely convert data to string with length limits."""
        # SUGA-ISP compliant correlation ID generation
        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        try:
            result = str(data)
            if len(result) > max_length:
                truncated = result[:max_length] + "... [TRUNCATED]"
                try:
                    execute_operation(GatewayInterface.DEBUG, "log",
                                   corr_id=correlation_id, scope="UTILITY",
                                   message="String conversion truncated",
                                   original_length=len(result), max_length=max_length)
                except ImportError:
                    # Optional dependency - continue if unavailable
                    ...
                return truncated

            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="UTILITY",
                               message="String conversion successful",
                               result_length=len(result))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return result
        except (ValueError, TypeError, AttributeError) as e:
            try:
                execute_operation(GatewayInterface.DEBUG, "log",
                               corr_id=correlation_id, scope="UTILITY",
                               message="String conversion failed", error=str(e))
            except ImportError:
                # Optional dependency - continue if unavailable
                ...
            return "[conversion_error]"

    def extract_error_details(self, error: Exception, correlation_id: str = None) -> dict[str, Any]:
        """Extract detailed error information with stack trace."""
        # SUGA-ISP compliant correlation ID generation
        if correlation_id is None:
            correlation_id = generate_correlation_id("util")

        try:
            details = {
                "type": type(error).__name__,
                "message": str(error),
                "args": getattr(error, "args", []),
            }

            try:
                execute_operation(GatewayInterface.DEBUG, "log_debug",
                               corr_id=correlation_id, scope="UTILITY",
                               message="Error details extracted",
                               error_type=details["type"])
            except (ImportError, AttributeError):
                # Optional dependency - continue if unavailable
                ...

            return details
        except (ValueError, TypeError, KeyError) as e:
            try:
                execute_operation(GatewayInterface.DEBUG, "log_debug",
                               corr_id=correlation_id, scope="UTILITY",
                               message="Error detail extraction failed",
                               error=str(e))
            except (ImportError, AttributeError):
                # Optional dependency - continue if unavailable
                ...
            return {
                "type": "DataError",
                "message": f"Failed to extract error details: {e}",
            }
        except (AttributeError, RuntimeError, OSError) as e:
            try:
                execute_operation(GatewayInterface.DEBUG, "log_debug",
                               corr_id=correlation_id, scope="UTILITY",
                               message="Error detail extraction failed",
                               error=str(e))
            except (ImportError, AttributeError):
                # Optional dependency - continue if unavailable
                ...
            return {
                "type": "UnknownError",
                "message": "Failed to extract error details",
            }


__all__ = [
    "UtilitySanitizeOperations",
]
