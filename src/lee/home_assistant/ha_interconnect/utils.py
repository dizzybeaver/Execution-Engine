# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-06 - Extract utilities from ha_interconnect.py

"""utils.py - Logging and Metrics Utilities
Version: 2025-03-02_1
Purpose: Logging and metrics utilities for HA interconnect

This module provides:
- Logging wrappers with fallback
- Metrics recording wrappers
- Correlation ID generation

Copyright 2025 Joseph Hersey
Licensed under Apache License, Version 2.0
"""

import os

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id


def log_info(message: str, **context) -> None:
    """Log info message through LEE gateway with HA correlation ID."""
    try:
        execute_operation(GatewayInterface.LOGGING, "log_info",
                        message=message, **context)
    except (AttributeError, RuntimeError):
        # Gateway unavailable - fallback to print
        print(f"[HA_INFO] {message}")


def log_error(message: str, **context) -> None:
    """Log error message through LEE gateway with HA correlation ID."""
    try:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                        message=message, **context)
    except (AttributeError, RuntimeError):
        # Gateway unavailable - fallback to print
        print(f"[HA_ERROR] {message}")


def log_debug(message: str, **context) -> None:
    """Log debug message through LEE gateway with HA correlation ID."""
    try:
        execute_operation(GatewayInterface.LOGGING, "log_debug",
                        message=message, **context)
    except (AttributeError, RuntimeError):
        # Gateway unavailable - fallback to print (only if LEE_DEBUG)
        if os.environ.get("LEE_DEBUG", "false").lower() == "true":
            print(f"[HA_DEBUG] {message}")


def metrics_increment(metric_name: str, value: float = 1.0, **tags) -> None:
    """Increment metric through LEE gateway."""
    try:
        execute_operation(GatewayInterface.OBSERVABILITY, "increment",
                        metric_name=metric_name, value=value, **tags)
    except (AttributeError, ImportError, RuntimeError):
        # Metrics module unavailable or API changed
        log_debug(f"Metrics unavailable for increment {metric_name}")


def metrics_record(metric_name: str, value: float, unit: str = None, **tags) -> None:
    """Record metric through LEE gateway."""
    try:
        execute_operation(GatewayInterface.OBSERVABILITY, "record_metric",
                        name=metric_name, value=value, unit=unit, **tags)
    except (AttributeError, ImportError, RuntimeError):
        # Metrics module unavailable or API changed
        log_debug(f"Metrics unavailable for recording {metric_name}")


def generate_ha_correlation_id() -> str:
    """Generate correlation ID via LEE gateway or fallback."""
    try:
        return execute_operation(GatewayInterface.UTILITY, "generate_correlation_id")
    except (AttributeError, ImportError, RuntimeError):
        # Gateway utility unavailable, use fallback
        return generate_correlation_id("ha")


__all__ = [
    "log_info",
    "log_error",
    "log_debug",
    "metrics_increment",
    "metrics_record",
    "generate_ha_correlation_id",
]
