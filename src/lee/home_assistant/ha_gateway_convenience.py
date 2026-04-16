# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-01 - Extracted convenience functions from ha_gateway.py

"""ha_gateway_convenience.py - Convenience Functions for HA Gateway
Version: 2026-04-01
Purpose: Utility functions for logging, validation, metrics, and correlation IDs

This module contains general-purpose convenience functions that are used
across all HA interfaces. These are the basic building blocks for HA operations.

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Core imports
from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

# ===== LOGGING FUNCTIONS =====

def ha_log_error(message: str, **context) -> None:
    """Log error through LEE gateway (SUGA-ISP compliant)."""
    try:
        corr_id = generate_correlation_id("ha")
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=message, corr_id=corr_id, **context)
    except ImportError:
        print(f"[HA_ERROR] {message}")


def ha_log_info(message: str, **context) -> None:
    """Log info through LEE gateway (SUGA-ISP compliant)."""
    try:
        # Only generate corr_id if not provided in context
        if 'corr_id' not in context:
            context['corr_id'] = generate_correlation_id("ha")
        execute_operation(GatewayInterface.LOGGING, "log_info",
                         message=message, **context)
    except ImportError:
        print(f"[HA_INFO] {message}")


def ha_log_warning(message: str, **context) -> None:
    """Log warning through LEE gateway (SUGA-ISP compliant)."""
    try:
        # Only generate corr_id if not provided in context
        if 'corr_id' not in context:
            context['corr_id'] = generate_correlation_id("ha")
        execute_operation(GatewayInterface.LOGGING, "log_warning",
                         message=message, **context)
    except ImportError:
        print(f"[HA_WARNING] {message}")


# ===== VALIDATION FUNCTIONS =====

def ha_validate_string(value: str, min_length: int = 0, max_length: int = 1000, name: str = "value") -> None:
    """Validate string through LEE gateway (SUGA-ISP compliant)."""
    try:
        execute_operation(GatewayInterface.SECURITY, "validate_string",
                         value=value, min_length=min_length, max_length=max_length, name=name)
    except ImportError as exc:
        # Fallback validation
        if not isinstance(value, str):
            raise TypeError(f"'{name}' must be str") from exc
        if len(value) < min_length:
            raise ValueError(f"'{name}' too short") from exc
        if len(value) > max_length:
            raise ValueError(f"'{name}' too long") from exc


# ===== METRICS FUNCTIONS =====

def ha_metrics_put(metric_name: str, value: float, unit: str = None, **tags) -> None:
    """Put metric through LEE gateway (SUGA-ISP compliant)."""
    try:
        execute_operation(GatewayInterface.OBSERVABILITY, "record_metric",
                         name=metric_name, value=value, unit=unit, **tags)
    except ImportError:
        # Optional dependency - continue if unavailable
        pass


# ===== UTILITY FUNCTIONS =====

def ha_generate_correlation_id() -> str:
    """Generate correlation ID through LEE gateway (SUGA-ISP compliant)."""
    try:
        return execute_operation(GatewayInterface.UTILITY, "generate_correlation_id")
    except ImportError:
        return generate_correlation_id("ha")
