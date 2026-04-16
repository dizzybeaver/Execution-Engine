"""singleton/functions/singleton_management/clear_implementation.py
Version: 2025.12.13.01
Description: Clear all singleton implementations function

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

from lee.gateway.gateway_core import generate_correlation_id
from lee.singleton.singleton_manager import get_singleton_manager


def clear_implementation(correlation_id: str = None, **kwargs) -> int:
    """Clear all singleton instances.

    Args:
        correlation_id: Optional correlation ID for debug tracking

    Returns:
        Number of instances cleared
    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("sng")

    manager = get_singleton_manager()
    return manager.clear(correlation_id=correlation_id, **kwargs)


__all__ = ["clear_implementation"]
