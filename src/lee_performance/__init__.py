"""Performance observability package for LEE.

This package provides performance monitoring and profiling capabilities
with minimal cold start impact. Modules are lazy-loaded on first access.
"""

from .cold_start_tracker import (
    ColdStartMetrics,
    ColdStartTracker,
    ContainerPhase,
    get_cold_start_tracker,
)
from .resource_profiler import (
    AggregatedProfileStats,
    OperationProfile,
    ResourceProfiler,
    get_resource_profiler,
)

__all__ = [
    "ColdStartMetrics",
    "ColdStartTracker",
    "ContainerPhase",
    "OperationProfile",
    "ResourceProfiler",
    "AggregatedProfileStats",
    "get_cold_start_tracker",
    "get_resource_profiler",
]
