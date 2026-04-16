"""singleton/classes/SingletonCore.py
Version: 2025.12.13.01
Description: SingletonCore class - Manages singleton instances across the application

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

import sys
import time
from collections import deque
from collections.abc import Callable
from typing import Any, Optional

from lee.gateway import GatewayInterface, execute_operation
from lee.gateway.gateway_core import generate_correlation_id


class SingletonCore:
    """Manages singleton instances across the application.

    COMPLIANCE:
    - AP-08: NO threading locks (Lambda single-threaded)
    - DEC-04: Lambda single-threaded model
    - LESS-18: SINGLETON pattern via get_singleton_manager()
    - LESS-21: Rate limiting (1000 ops/sec)

    DISTINCTION FROM CACHE:
    - SINGLETON: Manages object instances (classes, managers, services)
    - CACHE: Manages data values with TTL and LRU eviction
    """

    def __init__(self):
        self._instances: dict[str, Any] = {}
        self._creation_times: dict[str, float] = {}
        self._access_counts: dict[str, int] = {}
        self._cached_memory_bytes: Optional[int] = None  # Cache for memory calculations

        # Rate limiting (1000 ops/sec for infrastructure)
        self._rate_limiter = deque(maxlen=1000)
        self._rate_limit_window_ms = 1000
        self._rate_limited_count = 0

    def _check_rate_limit(self) -> bool:
        """Check rate limit (1000 ops/sec)."""
        now = time.time() * 1000

        while self._rate_limiter and (now - self._rate_limiter[0]) > self._rate_limit_window_ms:
            self._rate_limiter.popleft()

        if len(self._rate_limiter) >= 1000:
            self._rate_limited_count += 1
            return False

        self._rate_limiter.append(now)
        return True

    def get(self, name: str, factory_func: Optional[Callable] = None,
            correlation_id: str = None, **kwargs) -> Any:
        """Get or create singleton instance.

        Args:
            name: Singleton name (must be non-empty string)
            factory_func: Optional factory function to create instance
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            Singleton instance or None if not exists and no factory provided

        Raises:
            ValueError: If name is empty or rate limited
            Exception: If factory function raises exception
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("sgl")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Rate limit exceeded in get()")
            raise ValueError("Rate limit exceeded (1000 ops/sec)")

        if not name or not isinstance(name, str):
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Invalid name",
                    name=name, name_type=type(name).__name__)
            raise ValueError("Singleton name must be a non-empty string")

        # Check if exists
        if name not in self._instances:
            if factory_func is None:
                execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Instance not found, no factory",
                        name=name)
                return None

            # Create instance
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Creating new instance",
                    name=name, has_factory=True)

            with execute_operation(GatewayInterface.DEBUG, "timing",
                     corr_id=correlation_id, scope="SINGLETON",
                     op_name=f"factory:{name}") as _:
                try:
                    instance = factory_func()
                    self._instances[name] = instance
                    self._cached_memory_bytes = None  # Invalidate cache
                    self._creation_times[name] = time.time()
                    self._access_counts[name] = 0

                    execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Instance created",
                            name=name, instance_type=type(instance).__name__)
                except (TypeError, ValueError, RuntimeError, ImportError) as e:
                    execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Factory failed",
                            name=name, error=str(e), error_type=type(e).__name__)
                    raise RuntimeError(f"Failed to create singleton '{name}': {e}") from e

        # Update access count and return
        if name in self._instances:
            self._access_counts[name] = self._access_counts.get(name, 0) + 1

            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Instance retrieved",
                    name=name, access_count=self._access_counts[name])

            return self._instances[name]
        return None

    def set(self, name: str, instance: Any, correlation_id: str = None, **kwargs):
        """Set singleton instance.

        Args:
            name: Singleton name (must be non-empty string)
            instance: Instance to store
            correlation_id: Optional correlation ID for debug tracking

        Raises:
            ValueError: If name is empty or rate limited

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("sgl")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Rate limit exceeded in set()")
            raise ValueError("Rate limit exceeded (1000 ops/sec)")

        if not name or not isinstance(name, str):
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Invalid name in set()",
                    name=name)
            raise ValueError("Singleton name must be a non-empty string")

        execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Setting instance",
                name=name, instance_type=type(instance).__name__)

        self._instances[name] = instance
        self._cached_memory_bytes = None  # Invalidate cache
        self._creation_times[name] = time.time()
        self._access_counts[name] = 0

        execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Instance set successfully", name=name)

    def has(self, name: str, correlation_id: str = None, **kwargs) -> bool:
        """Check if singleton exists.

        Args:
            name: Singleton name
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            True if singleton exists, False otherwise

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("sgl")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Rate limit exceeded in has()")
            return False

        exists = name in self._instances

        execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Existence check",
                name=name, exists=exists)

        return exists

    def delete(self, name: str, correlation_id: str = None, **kwargs) -> bool:
        """Delete singleton instance.

        Args:
            name: Singleton name
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            True if deleted, False if didn't exist or rate limited

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("sgl")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Rate limit exceeded in delete()")
            return False

        if name in self._instances:
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Deleting instance", name=name)

            del self._instances[name]
            self._cached_memory_bytes = None  # Invalidate cache
            self._creation_times.pop(name, None)
            self._access_counts.pop(name, None)

            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Instance deleted", name=name)
            return True

        execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Instance not found for deletion", name=name)
        return False

    def clear(self, correlation_id: str = None, **kwargs) -> int:
        """Clear all singleton instances.

        Args:
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            Count of singletons cleared

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("sgl")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Rate limit exceeded in clear()")
            return 0

        count = len(self._instances)

        execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Clearing all instances", count=count)

        self._instances.clear()
        self._cached_memory_bytes = None  # Invalidate cache
        self._creation_times.clear()
        self._access_counts.clear()

        execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "All instances cleared")

        return count

    def get_stats(self, correlation_id: str = None, **kwargs) -> dict[str, Any]:
        """Get singleton statistics.

        Args:
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            Dictionary containing singleton statistics
        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("sgl")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Rate limit exceeded in get_stats()")
            return {"error": "Rate limit exceeded"}

        try:
            total_memory = sum(
                sys.getsizeof(instance)
                for instance in self._instances.values()
            )
        except (TypeError, AttributeError, ValueError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "getsizeof failed, using zero",
                    error=str(e), error_type=type(e).__name__)
            total_memory = 0
        self._cached_memory_bytes = total_memory  # Cache the result

        execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Getting statistics",
                total_singletons=len(self._instances),
                total_memory_kb=total_memory / 1024)

        return {
            "total_singletons": len(self._instances),
            "singleton_names": list(self._instances.keys()),
            "singleton_types": {
                name: type(instance).__name__
                for name, instance in self._instances.items()
            },
            "creation_times": dict(self._creation_times),
            "access_counts": dict(self._access_counts),
            "estimated_memory_bytes": total_memory,
            "estimated_memory_kb": total_memory / 1024,
            "estimated_memory_mb": total_memory / (1024 * 1024),
            "memory_note": "Estimates are shallow size only (sys.getsizeof)",
            "rate_limited_count": self._rate_limited_count,
            "timestamp": time.time(),
        }

    def reset(self, correlation_id: str = None, **kwargs) -> bool:
        """Reset SINGLETON manager state (lifecycle management).

        Args:
            correlation_id: Optional correlation ID for debug tracking

        Returns:
            True if reset successful, False if rate limited

        """
        if correlation_id is None:
            correlation_id = generate_correlation_id("sgl")

        if not self._check_rate_limit():
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Rate limit exceeded in reset()")
            return False

        try:
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Resetting manager state")

            self._rate_limiter.clear()
            self._rate_limited_count = 0
            self._cached_memory_bytes = None  # Invalidate cache

            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Manager reset complete")
            return True
        except (RuntimeError, ValueError, AttributeError) as e:
            execute_operation(GatewayInterface.DEBUG, "log",
                 corr_id=correlation_id, scope="SINGLETON",
                 message= "Manager reset failed", error=str(e), error_type=type(e).__name__)
            return False

    # Legacy methods (backward compatibility)

    def reset_all(self, **kwargs) -> int:
        """Legacy name for clear."""
        return self.clear(**kwargs)

    def exists(self, name: str, **kwargs) -> bool:
        """Legacy name for has."""
        return self.has(name, **kwargs)


__all__ = ["SingletonCore"]
