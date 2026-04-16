"""get_memory_stats.py
Extracted from: singleton_memory.py
Function: get_memory_stats
"""

import platform
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

if platform.system() != 'Windows':
    import resource


def get_memory_stats() -> dict[str, Any]:
    """Get current memory statistics - returns standardized response."""

    correlation_id = generate_correlation_id("sgl")

    try:
        if platform.system() == 'Windows':
            return {"success": False, "error": "Memory stats not available on Windows"}

        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="Memory statistics retrieved",
                                data={
                                    "rss_mb": memory_mb,
                                    "vms_mb": memory_mb,
                                    "percent": (memory_mb / 128) * 100,
                                    "available_mb": (128 - memory_mb),
                                    "compliant": memory_mb < 128,
                                },
                                correlation_id=correlation_id)
    except (RuntimeError, ValueError, OSError, AttributeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"Memory stats failed: {e!s}", error=e, error_type=type(e).__name__)
        return {"success": False, "error": "Failed to get memory statistics"}
