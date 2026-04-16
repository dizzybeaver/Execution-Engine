"""singleton/functions/memory/emergency_memory_preserve.py
Version: 2025.12.13.01
Description: Emergency memory preservation mode function

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

import gc
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id


def emergency_memory_preserve() -> dict[str, Any]:
    """Emergency memory preservation mode - returns standardized response."""
    correlation_id = generate_correlation_id("sgl")

    try:
        initial_stats = execute_operation(GatewayInterface.SINGLETON, "get", name="get_memory_stats")
        initial_data = initial_stats.get("data", {})

        if initial_data.get("compliant", False):
            return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                    message="Memory within limits, emergency mode not required",
                                    data={
                                        "emergency_mode": False,
                                        "reason": "memory_within_limits",
                                        "current_mb": initial_data.get("rss_mb", 0),
                                    },
                                    correlation_id=correlation_id)

        emergency_steps = []

        gc_result = gc.collect()
        emergency_steps.append(f"gc_collected_{gc_result}_objects")

        try:
            singleton_manager = execute_operation(GatewayInterface.SINGLETON, "get",
                                                name="_SINGLETON_MANAGER")
            instances = getattr(singleton_manager, "_instances", None) if singleton_manager else None
            if singleton_manager and instances is not None:
                singleton_count = len(instances)
                execute_operation(GatewayInterface.SINGLETON, "set",
                                name="_SINGLETON_MANAGER_reset", value=True)
                emergency_steps.append(f"cleared_{singleton_count}_singletons")
        except (KeyError, AttributeError, ValueError, TypeError):
            emergency_steps.append("singleton_clear_failed")

        final_gc = gc.collect()
        emergency_steps.append(f"final_gc_collected_{final_gc}_objects")

        final_stats = execute_operation(GatewayInterface.SINGLETON, "get", name="get_memory_stats")
        final_data = final_stats.get("data", {})

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="Emergency memory preservation completed",
                                data={
                                    "emergency_mode": True,
                                    "emergency_steps": emergency_steps,
                                    "memory_before_mb": initial_data.get("rss_mb", 0),
                                    "memory_after_mb": final_data.get("rss_mb", 0),
                                    "memory_freed_mb": initial_data.get("rss_mb", 0) - final_data.get("rss_mb", 0),
                                    "now_compliant": final_data.get("compliant", False),
                                },
                                correlation_id=correlation_id)
    except (RuntimeError, ValueError, KeyError, AttributeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"Emergency memory preservation failed: {e!s}", error=e, error_type=type(e).__name__)
        return {"success": False, "error": "Emergency memory preservation failed"}


__all__ = ["emergency_memory_preserve"]
