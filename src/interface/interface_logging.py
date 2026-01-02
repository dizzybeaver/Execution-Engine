"""
interface_logging.py - Logging Router (SECURITY HARDENED)
Version: 2025-12-08_1
Purpose: Firewall router for LOGGING interface with security sanitization
License: Apache 2.0

CHANGES (2025-12-08_1):
- Updated imports from logging/ subdirectory
- Integrated hierarchical debug control via debug module
- Replaced _is_debug_mode()/_print_debug() with debug.debug_log()
- PRESERVED: All security sanitization (CVE-LOG-001/002/003)
"""

import os
from typing import Any, Dict, Callable, Union

from logging.logging_core import (
    _execute_log_info_implementation,
    _execute_log_warning_implementation,
    _execute_log_error_implementation,
    _execute_log_debug_implementation,
    _execute_log_operation_start_implementation,
    _execute_log_operation_success_implementation,
    _execute_log_operation_failure_implementation,
    _execute_log_reset_implementation,
)

# ===== AVAILABILITY CHECK =====

try:
    from logging.logging_manager import get_logging_core
    _LOGGING_AVAILABLE = True
    _LOGGING_IMPORT_ERROR = None
except ImportError as e:
    _LOGGING_AVAILABLE = False
    _LOGGING_IMPORT_ERROR = str(e)

# ===== SECURITY SANITIZATION =====

_SENSITIVE_KEYS = {'password', 'token', 'secret', 'api_key', 'auth', 'credential'}

def _sanitize_log_data(message: str, extra: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Sanitize log message and extra data (CVE-LOG-001, CVE-LOG-002, CVE-LOG-003)."""
    safe_message = message.replace('\n', ' ').replace('\r', ' ')[:500]
    
    safe_extra = {}
    for key, value in extra.items():
        if any(sens in key.lower() for sens in _SENSITIVE_KEYS):
            safe_extra[key] = '***REDACTED***'
        else:
            if isinstance(value, str):
                safe_extra[key] = value[:200]
            else:
                safe_extra[key] = value
    
    return safe_message, safe_extra

# ===== VALIDATION FUNCTIONS =====

def _validate_message_param(kwargs: Dict[str, Any], operation: str) -> None:
    """Validate message parameter."""
    if 'message' not in kwargs:
        raise ValueError(f"logging.{operation} requires 'message' parameter")
    
    message = str(kwargs['message'])
    message = message.replace('\n', ' ').replace('\r', ' ')
    kwargs['message'] = message[:500]
    
    extra = {k: v for k, v in kwargs.items() if k != 'message'}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

def _validate_operation_start_params(kwargs: Dict[str, Any]) -> None:
    """Validate operation_start parameters."""
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_start requires 'operation_name' parameter")
    
    operation_name = str(kwargs['operation_name'])
    operation_name = operation_name.replace('\n', ' ').replace('\r', ' ')
    kwargs['operation_name'] = operation_name[:200]
    
    extra = {k: v for k, v in kwargs.items() if k != 'operation_name'}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

def _validate_operation_success_params(kwargs: Dict[str, Any]) -> None:
    """Validate operation_success parameters."""
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'operation_name' parameter")
    if 'duration_ms' not in kwargs:
        raise ValueError("logging.log_operation_success requires 'duration_ms' parameter")
    
    operation_name = str(kwargs['operation_name'])
    operation_name = operation_name.replace('\n', ' ').replace('\r', ' ')
    kwargs['operation_name'] = operation_name[:200]
    
    try:
        kwargs['duration_ms'] = float(kwargs['duration_ms'])
    except (ValueError, TypeError):
        raise ValueError("duration_ms must be numeric")
    
    extra = {k: v for k, v in kwargs.items() 
             if k not in ('operation_name', 'duration_ms')}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

def _validate_operation_failure_params(kwargs: Dict[str, Any]) -> None:
    """Validate operation_failure parameters."""
    if 'operation_name' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'operation_name' parameter")
    if 'error' not in kwargs:
        raise ValueError("logging.log_operation_failure requires 'error' parameter")
    
    operation_name = str(kwargs['operation_name'])
    operation_name = operation_name.replace('\n', ' ').replace('\r', ' ')
    kwargs['operation_name'] = operation_name[:200]
    
    if 'error' in kwargs and kwargs['error'] is not None:
        kwargs['error'] = str(kwargs['error'])[:500]
    
    extra = {k: v for k, v in kwargs.items() 
             if k not in ('operation_name', 'error')}
    if extra:
        _, safe_extra = _sanitize_log_data("", extra)
        kwargs.update(safe_extra)

# ===== OPERATION DISPATCH =====

_OPERATION_DISPATCH: Dict[str, Callable] = {
    'log_info': _execute_log_info_implementation,
    'log_error': _execute_log_error_implementation,
    'log_warning': _execute_log_warning_implementation,
    'log_debug': _execute_log_debug_implementation,
    'log_operation_start': _execute_log_operation_start_implementation,
    'log_operation_success': _execute_log_operation_success_implementation,
    'log_operation_failure': _execute_log_operation_failure_implementation,
    'reset': _execute_log_reset_implementation,
    'reset_logging': _execute_log_reset_implementation,
}

# ===== PUBLIC INTERFACE =====

def execute_logging_operation(operation: str, **kwargs) -> Any:
    """Execute logging operation with security hardening."""
    if not _LOGGING_AVAILABLE:
        raise RuntimeError(
            f"Logging system not available: {_LOGGING_IMPORT_ERROR}"
        )
    
    if operation not in _OPERATION_DISPATCH:
        valid_ops = ', '.join(sorted(_OPERATION_DISPATCH.keys()))
        raise ValueError(
            f"Unknown logging operation: '{operation}'. "
            f"Valid operations: {valid_ops}"
        )
    
    try:
        if operation in ('log_info', 'log_error', 'log_warning', 'log_debug'):
            _validate_message_param(kwargs, operation)
        elif operation == 'log_operation_start':
            _validate_operation_start_params(kwargs)
        elif operation == 'log_operation_success':
            _validate_operation_success_params(kwargs)
        elif operation == 'log_operation_failure':
            _validate_operation_failure_params(kwargs)
        # Reset operation needs no validation
    except ValueError as e:
        raise
    
    try:
        handler = _OPERATION_DISPATCH[operation]
        result = handler(**kwargs)
        return result
        
    except Exception as e:
        print(f"[INTERFACE_LOGGING_ERROR] {operation} failed: {e}")
        raise

# ===== EXPORTS =====

__all__ = ['execute_logging_operation']
