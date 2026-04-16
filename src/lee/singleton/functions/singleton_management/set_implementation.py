"""singleton/functions/singleton_management/set_implementation.py
Version: 2025.12.13.01
Description: Set singleton implementation function

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


def set_implementation(name: str, instance: Any,
                      correlation_id: str = None, **kwargs):
    """Set singleton instance.

    Args:
        name: Singleton name
        instance: Instance to store
        correlation_id: Optional correlation ID for debug tracking

    """
    if correlation_id is None:
        correlation_id = generate_correlation_id("sgl")

    if not name:
        raise ValueError("Parameter 'name' is required for set operation")
    if instance is None and "instance" not in kwargs:
        raise ValueError("Parameter 'instance' is required for set operation")

    execute_operation(GatewayInterface.DEBUG, "log",
                     corr_id=correlation_id, scope="SINGLETON",
                     message="set_implementation called",
                     name=name, instance_type=type(instance).__name__)

    return get_singleton_manager().set(
        name=name,
        instance=instance,
        correlation_id=correlation_id,
    )


__all__ = ["set_implementation"]
