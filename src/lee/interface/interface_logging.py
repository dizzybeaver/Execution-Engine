# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-11 - Refactor to use graceful_import decorator


"""interface_logging.py - Logging Router (SECURITY HARDENED)
Version: 2026-04-11_2
Purpose: Firewall router for LOGGING interface with security sanitization
License: Apache 2.0
"""

import random
import time
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.lee_security.sanitize import DataSanitizer
from lee.utils.graceful_import import graceful_import


@graceful_import('lee.lee_logging.logging_generic')
def _import_logging():
    from lee.lee_logging.logging_generic import (
        _execute_log_debug_implementation,
        _execute_log_error_implementation,
        _execute_log_info_implementation,
        _execute_log_operation_failure_implementation,
        _execute_log_operation_start_implementation,
        _execute_log_operation_success_implementation,
        _execute_log_reset_implementation,
        _execute_log_warning_implementation,
    )
    return {
        'execute_log_debug': _execute_log_debug_implementation,
        'execute_log_error': _execute_log_error_implementation,
        'execute_log_info': _execute_log_info_implementation,
        'execute_log_operation_failure':
            _execute_log_operation_failure_implementation,
        'execute_log_operation_start':
            _execute_log_operation_start_implementation,
        'execute_log_operation_success':
            _execute_log_operation_success_implementation,
        'execute_log_reset': _execute_log_reset_implementation,
        'execute_log_warning': _execute_log_warning_implementation,
    }


_logging_funcs = _import_logging()
_LOGGING_AVAILABLE = _import_logging.__dict__.get('_LOGGING_GENERIC_AVAILABLE', False)
_LOGGING_IMPORT_ERROR = _import_logging.__dict__.get('_LOGGING_GENERIC_IMPORT_ERROR',
                                                         None)

if _LOGGING_AVAILABLE:
    _execute_log_debug_implementation = _logging_funcs['execute_log_debug']
    _execute_log_error_implementation = _logging_funcs['execute_log_error']
    _execute_log_info_implementation = _logging_funcs['execute_log_info']
    _execute_log_operation_failure_implementation = \
        _logging_funcs['execute_log_operation_failure']
    _execute_log_operation_start_implementation = \
        _logging_funcs['execute_log_operation_start']
    _execute_log_operation_success_implementation = \
        _logging_funcs['execute_log_operation_success']
    _execute_log_reset_implementation = _logging_funcs['execute_log_reset']
    _execute_log_warning_implementation = _logging_funcs['execute_log_warning']
else:
    def _stub_unavailable(**_kwargs) -> dict[str, Any]:
        return {"success": False, "error": "Logging module unavailable"}

    _execute_log_debug_implementation = _stub_unavailable
    _execute_log_error_implementation = _stub_unavailable
    _execute_log_info_implementation = _stub_unavailable
    _execute_log_operation_failure_implementation = _stub_unavailable
    _execute_log_operation_start_implementation = _stub_unavailable
    _execute_log_operation_success_implementation = _stub_unavailable
    _execute_log_reset_implementation = _stub_unavailable
    _execute_log_warning_implementation = _stub_unavailable


def _sanitize_log_data(
    message: str,
    extra: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Sanitize log message and extra data (CVE-LOG-001/002/003)."""
    return DataSanitizer.sanitize_log_data(message, extra)


def _validate_message_param(
    kwargs: dict[str, Any],
    operation: str,
) -> None:
    """Validate message parameter."""
    if "message" not in kwargs:
        raise ValueError(
            f"logging.{operation} requires 'message' parameter"
        )

    message = str(kwargs["message"])
    safe_message, safe_extra = DataSanitizer.sanitize_log_data(
        message, {k: v for k, v in kwargs.items() if k != "message"}
    )
    kwargs["message"] = safe_message
    kwargs.update(safe_extra)


def _validate_operation_start_params(kwargs: dict[str, Any]) -> None:
    """Validate operation_start parameters."""
    if "operation_name" not in kwargs:
        raise ValueError(
            "logging.log_operation_start requires "
            "'operation_name' parameter"
        )

    operation_name = str(kwargs["operation_name"])
    _, safe_extra = DataSanitizer.sanitize_log_data(
        operation_name, {k: v for k, v in kwargs.items()
                         if k != "operation_name"}
    )
    kwargs["operation_name"] = operation_name[:200]
    kwargs.update(safe_extra)


def _validate_operation_success_params(kwargs: dict[str, Any]) -> None:
    """Validate operation_success parameters."""
    if "operation_name" not in kwargs:
        raise ValueError(
            "logging.log_operation_success requires "
            "'operation_name' parameter"
        )
    if "duration_ms" not in kwargs:
        raise ValueError(
            "logging.log_operation_success requires "
            "'duration_ms' parameter"
        )

    operation_name = str(kwargs["operation_name"])
    _, safe_extra = DataSanitizer.sanitize_log_data(
        operation_name, {k: v for k, v in kwargs.items()
                         if k not in ("operation_name", "duration_ms")}
    )
    kwargs["operation_name"] = operation_name[:200]
    kwargs.update(safe_extra)

    try:
        kwargs["duration_ms"] = float(kwargs["duration_ms"])
    except (ValueError, TypeError) as exc:
        raise ValueError("duration_ms must be numeric") from exc


def _validate_operation_failure_params(kwargs: dict[str, Any]) -> None:
    """Validate operation_failure parameters."""
    if "operation_name" not in kwargs:
        raise ValueError(
            "logging.log_operation_failure requires "
            "'operation_name' parameter"
        )
    if "error" not in kwargs:
        raise ValueError(
            "logging.log_operation_failure requires 'error' parameter"
        )

    operation_name = str(kwargs["operation_name"])
    error_msg = str(kwargs["error"])[:500] if kwargs.get("error") else ""

    _, safe_extra = DataSanitizer.sanitize_log_data(
        operation_name, {k: v for k, v in kwargs.items()
                         if k not in ("operation_name", "error")}
    )

    kwargs["operation_name"] = operation_name[:200]
    kwargs["error"] = error_msg
    kwargs.update(safe_extra)


# Static Dispatch Dictionary (DDS) with metadata
_OPERATION_DISPATCH: dict[str, dict[str, Any]] = {
    "log_info": {
        "func": _execute_log_info_implementation,
        "category": "write",
        "description": "Log info-level message",
    },
    "log_warning": {
        "func": _execute_log_warning_implementation,
        "category": "write",
        "description": "Log warning-level message",
    },
    "log_error": {
        "func": _execute_log_error_implementation,
        "category": "write",
        "description": "Log error-level message",
    },
    "log_debug": {
        "func": _execute_log_debug_implementation,
        "category": "write",
        "description": "Log debug-level message",
    },
    "log_operation_start": {
        "func": _execute_log_operation_start_implementation,
        "category": "write",
        "description": "Log operation start event",
    },
    "log_operation_success": {
        "func": _execute_log_operation_success_implementation,
        "category": "write",
        "description": "Log operation success with timing",
    },
    "log_operation_failure": {
        "func": _execute_log_operation_failure_implementation,
        "category": "write",
        "description": "Log operation failure with error",
    },
    "reset": {
        "func": _execute_log_reset_implementation,
        "category": "admin",
        "description": "Reset logging system",
    },
    "reset_logging": {
        "func": _execute_log_reset_implementation,
        "category": "admin",
        "description": "Alias for reset",
    },
}


def execute_logging_operation(operation: str, **kwargs) -> Any:
    """Execute logging operation with security hardening."""
    if not _LOGGING_AVAILABLE:
        raise RuntimeError(
            f"Logging interface unavailable: {_LOGGING_IMPORT_ERROR}",
        )

    # Generate correlation ID if not provided
    if "correlation_id" not in kwargs:
        prefix = execute_operation(
            GatewayInterface.UTILITY,
            'get_module_prefix',
            module_name='int'
        )
        # Correlation ID - non-security-critical, use fast random
        kwargs["correlation_id"] = (
            f"{prefix}{int(time.time() * 1000)}_"
            f"{random.randbytes(4).hex()}"
        )

    if operation not in _OPERATION_DISPATCH:
        valid_ops = ", ".join(_OPERATION_DISPATCH.keys())
        raise ValueError(
            f"Unknown logging operation: '{operation}'. "
            f"Valid: {valid_ops}",
        )

    # Validate parameters
    # Dictionary dispatch for O(1) operation lookup
    LOG_VALIDATORS = {
        "log_info": _validate_message_param,
        "log_error": _validate_message_param,
        "log_warning": _validate_message_param,
        "log_debug": _validate_message_param,
        "log_operation_start": _validate_operation_start_params,
        "log_operation_success": _validate_operation_success_params,
        "log_operation_failure": _validate_operation_failure_params,
    }

    validator = LOG_VALIDATORS.get(operation)
    if validator:
        validator(kwargs, operation)

    dispatch_entry = _OPERATION_DISPATCH[operation]
    handler = dispatch_entry["func"]
    return handler(**kwargs)


__all__ = ["execute_logging_operation"]
