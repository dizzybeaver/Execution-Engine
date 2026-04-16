"""singleton/functions/singleton_management/get_stats_implementation.py
Version: 2025.12.13.01
Description: Get singleton statistics function

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
from lee.singleton.singleton_manager import get_singleton_manager


def get_stats_implementation(correlation_id: str = None, **kwargs) -> dict[str, Any]:
    """Get singleton statistics.

    Args:
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Statistics dict
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("sng")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="get_stats_implementation called")

    return get_singleton_manager().get_stats(correlation_id=correlation_id)


__all__ = ["get_stats_implementation"]
