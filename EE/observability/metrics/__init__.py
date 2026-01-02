"""
Metrics Interface - Observability Domain

Performance metrics and CloudWatch metrics.
"""

from EE.observability.metrics.metrics_interface import execute_metrics_operation
from EE.observability.metrics.metrics_factory import MetricsFactory

__all__ = [
    'execute_metrics_operation',
    'MetricsFactory',
]
