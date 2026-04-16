"""force_memory_cleanup.py
Extracted from: singleton_memory.py
Function: force_memory_cleanup
"""

import gc
import platform
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

if platform.system() != 'Windows':
    import resource


def force_memory_cleanup() -> dict[str, Any]:
    """Force aggressive memory cleanup - returns standardized response."""

    correlation_id = generate_correlation_id("sgl")

    try:
        if platform.system() == 'Windows':
            collected = gc.collect()
            return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                    message="Memory cleanup completed (Windows - GC only)",
                                    data={
                                        "gc_collected": collected,
                                        "compliant": True,
                                    },
                                    correlation_id=correlation_id)

        rusage_before = resource.getrusage(resource.RUSAGE_SELF)
        memory_before = rusage_before.ru_maxrss / 1024

        collected = gc.collect()

        rusage_after = resource.getrusage(resource.RUSAGE_SELF)
        memory_after = rusage_after.ru_maxrss / 1024

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="Memory cleanup completed",
                                data={
                                    "gc_collected": collected,
                                    "memory_before_mb": memory_before,
                                    "memory_after_mb": memory_after,
                                    "memory_freed_mb": max(0, memory_before - memory_after),
                                    "compliant": memory_after < 128,
                                },
                                correlation_id=correlation_id)
    except (RuntimeError, ValueError, OSError, AttributeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"Memory cleanup failed: {e!s}",
                         error_type=type(e).__name__)
        return {"success": False, "error": "Memory cleanup failed"}
