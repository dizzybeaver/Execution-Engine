"""optimize_memory.py
Extracted from: singleton_memory.py
Function: optimize_memory
"""

import gc
import platform
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

if platform.system() != 'Windows':
    import resource


def optimize_memory() -> dict[str, Any]:
    """Optimize memory usage with multiple cleanup strategies - returns standardized response."""

    correlation_id = generate_correlation_id("sgl")

    try:
        optimization_results = []

        collected = gc.collect()
        optimization_results.append(f"gc_collected_{collected}_objects")

        for generation in range(3):
            gen_collected = gc.collect(generation)
            optimization_results.append(f"gen{generation}_collected_{gen_collected}_objects")

        if platform.system() == 'Windows':
            return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                    message="Memory optimization completed (Windows - limited functionality)",
                                    data={
                                        "strategies_applied": optimization_results,
                                        "compliant": True,
                                        "optimization_count": len(optimization_results),
                                    },
                                    correlation_id=correlation_id)

        rusage = resource.getrusage(resource.RUSAGE_SELF)
        current_memory = rusage.ru_maxrss / 1024

        if current_memory > 100:
            try:
                execute_operation(GatewayInterface.SINGLETON, "set",
                                name="_SINGLETON_MANAGER_reset", value=True)
                optimization_results.append("singleton_cache_cleared")
            except (KeyError, AttributeError, ValueError):
                # Optional dependency - continue if unavailable
                ...

        rusage_final = resource.getrusage(resource.RUSAGE_SELF)
        final_memory = rusage_final.ru_maxrss / 1024

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="Memory optimization completed",
                                data={
                                    "strategies_applied": optimization_results,
                                    "final_memory_mb": final_memory,
                                    "compliant": final_memory < 128,
                                    "optimization_count": len(optimization_results),
                                },
                                correlation_id=correlation_id)
    except (RuntimeError, ValueError, OSError, AttributeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"Memory optimization failed: {e!s}",
                         error_type=type(e).__name__)
        return {"success": False, "error": "Memory optimization failed"}
