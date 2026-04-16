"""debug/__init__.py
Version: 2025-03-03_2
Purpose: DEBUG interface package exports
License: Apache 2.0
"""

from lee.lee_debug.call_stack_tracker import (
    CallFrame,
    CallStack,
    CallStackTracker,
    get_call_stack_tracker,
)
from lee.lee_debug.debug_config import DebugConfig, get_debug_config

# NEW: Export debug enhancement singletons
from lee.lee_debug.gateway_profiler import GatewayProfiler, get_gateway_profiler
from lee.lee_debug.hot_path_detector import (
    HotPathDetector,
    HotPathStats,
    get_hot_path_detector,
)

__all__ = [
    # Existing
    "DebugConfig",
    "get_debug_config",

    # NEW: Gateway Profiler
    "GatewayProfiler",
    "get_gateway_profiler",

    # NEW: Call Stack Tracker
    "CallFrame",
    "CallStack",
    "CallStackTracker",
    "get_call_stack_tracker",

    # NEW: Hot Path Detector
    "HotPathStats",
    "HotPathDetector",
    "get_hot_path_detector",
]
