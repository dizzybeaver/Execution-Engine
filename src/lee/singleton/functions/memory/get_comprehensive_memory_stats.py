"""get_comprehensive_memory_stats.py
Extracted from: singleton_memory.py
Function: get_comprehensive_memory_stats
"""

import gc
import platform
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

if platform.system() != 'Windows':
    import resource


def get_comprehensive_memory_stats() -> dict[str, Any]:
    """Get comprehensive memory statistics - returns standardized response."""

    correlation_id = generate_correlation_id("sgl")

    try:
        if platform.system() == 'Windows':
            return {"success": False, "error": "Comprehensive memory stats not available on Windows"}

        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024

        gc_stats = gc.get_stats()
        gc_counts = gc.get_count()
        object_count = len(gc.get_objects())

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="Comprehensive memory statistics retrieved",
                                data={
                                    "memory": {
                                        "rss_mb": memory_mb,
                                        "available_mb": 128 - memory_mb,
                                        "percent_used": (memory_mb / 128) * 100,
                                        "compliant": memory_mb < 128,
                                    },
                                    "gc": {
                                        "collections": gc_counts,
                                        "stats": gc_stats,
                                        "tracked_objects": object_count,
                                    },
                                    "system": {
                                        "lambda_limit_mb": 128,
                                        "pressure_level": "high" if memory_mb > 100 else "normal",
                                    },
                                },
                                correlation_id=correlation_id)
    except (RuntimeError, ValueError, OSError, AttributeError):
        return {"success": False, "error": "Failed to get comprehensive memory statistics"}
