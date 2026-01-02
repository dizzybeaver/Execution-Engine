"""
metrics/metrics_helper.py

Version: 2025-12-11_1
Purpose: Metrics helper utilities
Project: LEE
License: Apache 2.0
"""

from typing import Dict, Any, Optional, List


def safe_divide(numerator: float, denominator: float, default: float = 0.0, multiply_by: float = 1.0) -> float:
    """Safely divide with zero-check."""
    if denominator == 0:
        return default
    return (numerator / denominator) * multiply_by


def build_dimensions(base_dims: Dict[str, str], **extra_dims) -> Dict[str, str]:
    """Build dimensions dictionary from base and extras."""
    result = base_dims.copy()
    for key, value in extra_dims.items():
        if value is not None:
            result[key] = str(value)
    return result


def record_metric_with_duration(name: str, dimensions: Dict[str, str], duration_ms: Optional[float] = None) -> bool:
    """Record metric with optional duration."""
    from metrics.metrics_core import _MANAGER
    _MANAGER.record_metric(name, 1.0, dimensions)
    if duration_ms and duration_ms > 0:
        duration_name = name.replace('.count', '.duration_ms')
        _MANAGER.record_metric(duration_name, duration_ms, dimensions)
    return True


def calculate_percentiles(values: List[float]) -> Dict[str, float]:
    """Calculate percentiles from value list."""
    if not values:
        return {'p50': 0.0, 'p95': 0.0, 'p99': 0.0}
    sorted_values = sorted(values)
    n = len(sorted_values)
    return {
        'p50': sorted_values[int(n * 0.50)] if n > 0 else 0.0,
        'p95': sorted_values[int(n * 0.95)] if n > 0 else 0.0,
        'p99': sorted_values[int(n * 0.99)] if n > 0 else 0.0
    }


def format_metric_name(category: str, operation: str, metric_type: str) -> str:
    """Format metric name."""
    return f"{category}.{operation}.{metric_type}"


def parse_metric_key(key: str) -> Dict[str, Any]:
    """Parse metric key into components."""
    if '[' in key:
        name, dims_str = key.split('[', 1)
        dims_str = dims_str.rstrip(']')
        dimensions = {}
        for pair in dims_str.split(','):
            k, v = pair.split('=', 1)
            dimensions[k] = v
        return {'name': name, 'dimensions': dimensions}
    return {'name': key, 'dimensions': {}}
