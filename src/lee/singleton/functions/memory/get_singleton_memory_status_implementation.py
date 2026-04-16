"""singleton/functions/memory/get_singleton_memory_status_implementation.py
Version: 2025.12.13.01
Description: Get singleton memory status implementation function

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

import platform
from typing import Any

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id

if platform.system() != 'Windows':
    import resource


def _get_singleton_memory_status_implementation() -> dict[str, Any]:
    """Get singleton memory status implementation - returns standardized response."""
    correlation_id = generate_correlation_id("sgl")

    try:
        if platform.system() == 'Windows':
            try:
                singleton_manager = execute_operation(GatewayInterface.SINGLETON, "get",
                                                    name="_SINGLETON_MANAGER")
                instances = getattr(singleton_manager, "_instances", None) if singleton_manager else None
                singleton_count = len(instances) if instances is not None else 0
            except (KeyError, AttributeError, ValueError, TypeError):
                singleton_count = 0

            return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                    message="Singleton memory status retrieved (Windows - limited info)",
                                    data={
                                        "singleton_count": singleton_count,
                                        "memory_pressure": "normal",
                                    },
                                    correlation_id=correlation_id)

        rusage = resource.getrusage(resource.RUSAGE_SELF)
        memory_mb = rusage.ru_maxrss / 1024

        try:
            singleton_manager = execute_operation(GatewayInterface.SINGLETON, "get",
                                                name="_SINGLETON_MANAGER")
            instances = getattr(singleton_manager, "_instances", None) if singleton_manager else None
            singleton_count = len(instances) if instances is not None else 0
        except (KeyError, AttributeError, ValueError, TypeError):
            singleton_count = 0

        return execute_operation(GatewayInterface.UTILITY, "create_success_response",
                                message="Singleton memory status retrieved",
                                data={
                                    "total_process_memory_mb": memory_mb,
                                    "singleton_count": singleton_count,
                                    "lambda_128mb_compliant": memory_mb < 128,
                                    "memory_pressure": "high" if memory_mb > 100 else "normal",
                                },
                                correlation_id=correlation_id)
    except (RuntimeError, ValueError, OSError, AttributeError) as e:
        execute_operation(GatewayInterface.LOGGING, "log_error",
                         message=f"Singleton memory status failed: {e!s}", error_type=type(e).__name__)
        return {"success": False, "error": "Failed to get singleton memory status"}


__all__ = ["_get_singleton_memory_status_implementation"]
