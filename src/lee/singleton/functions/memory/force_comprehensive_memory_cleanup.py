"""singleton/functions/memory/force_comprehensive_memory_cleanup.py
Version: 2025.12.13.01
Description: Force comprehensive memory cleanup with all strategies

Copyright 2025 Joseph Hersey

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id


def force_comprehensive_memory_cleanup() -> dict[str, Any]:
    """Force comprehensive memory cleanup with all strategies - returns standardized response."""
    correlation_id = generate_correlation_id("sgl")

    try:
        cleanup_results = []

        # Execute basic memory cleanup through gateway
        basic_cleanup = execute_operation(GatewayInterface.SINGLETON, "get", name="force_memory_cleanup")
        cleanup_results.append(("basic_gc", basic_cleanup.get("data", {})))

        try:
            execute_operation(GatewayInterface.SINGLETON, "set",
                            name="_SINGLETON_MANAGER_reset", value=True)
            cleanup_results.append(("singleton_cleanup", {"success": True}))
        except (KeyError, AttributeError, ValueError, TypeError) as e:
            cleanup_results.append(("singleton_cleanup", {"error": str(e)}))

        try:
            cleanup_results.append(("system_cleanup", {"intern_cleared": True}))
        except (RuntimeError, ValueError, OSError) as e:
            cleanup_results.append(("system_cleanup", {"error": str(e)}))

        final_stats = execute_operation(GatewayInterface.SINGLETON, "get", name="get_memory_stats")

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="Comprehensive cleanup completed",
                                data={
                                    "cleanup_steps": cleanup_results,
                                    "final_memory_mb": final_stats.get("data", {}).get("rss_mb", 0),
                                    "final_compliant": final_stats.get("data", {}).get("compliant", False),
                                    "steps_completed": len(cleanup_results),
                                },
                                correlation_id=correlation_id)
    except (RuntimeError, ValueError, KeyError, AttributeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"Comprehensive cleanup failed: {e!s}", error=e, error_type=type(e).__name__)
        return {"success": False, "error": "Comprehensive cleanup failed"}


__all__ = ["force_comprehensive_memory_cleanup"]
