"""
Threading Factory - Operations Domain

Thread pool management and concurrent execution implementation.

UG-ISP Compliant:
- Factory contains actual implementation
- Receives logger, metrics, call_operation via DI
- NO imports outside operations domain (except stdlib)
- All cross-domain calls via call_operation callback
"""

from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from typing import Any, Dict, Optional, Callable, List, TypeVar, Iterable
import logging
import threading
import time


T = TypeVar('T')
R = TypeVar('R')


# =============================================================================
# Thread Pool Manager
# =============================================================================

class ThreadingFactory:
    """Thread pool management factory.

    Provides thread pool operations for concurrent execution.

    UG-ISP Compliance:
    - Factory contains actual implementation
    - Cross-domain calls via call_operation callback
    - Singleton pattern for thread pool management
    """

    _instance: Optional["ThreadingFactory"] = None
    _lock = threading.Lock()

    def __init__(
        self,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ):
        """Initialize threading factory.

        Args:
            logger: Logger instance
            metrics: Metrics instance
            call_operation: Callback for cross-domain operations
        """
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = metrics
        self.call_operation = call_operation

        # Thread pool executor
        self._executor: Optional[ThreadPoolExecutor] = None
        self._max_workers: int = 4
        self._lock = threading.RLock()

        # Statistics
        self._stats = {
            "submitted": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }

    @classmethod
    def get_instance(
        cls,
        logger: Optional[Any] = None,
        metrics: Optional[Any] = None,
        call_operation: Optional[Callable] = None
    ) -> "ThreadingFactory":
        """Get singleton instance of threading factory.

        Returns:
            Global ThreadingFactory instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(logger, metrics, call_operation)
        return cls._instance

    def _get_executor(self) -> ThreadPoolExecutor:
        """Get or create thread pool executor."""
        with self._lock:
            if self._executor is None or self._executor._shutdown:
                self._executor = ThreadPoolExecutor(max_workers=self._max_workers)
                self.logger.info(f"Thread pool created with {self._max_workers} workers")
            return self._executor

    def submit(
        self,
        func: Callable[..., R],
        *args,
        max_workers: Optional[int] = None,
        **kwargs
    ) -> Optional[Future]:
        """Submit task to thread pool.

        Args:
            func: Function to execute
            *args: Function arguments
            max_workers: Optional max workers for this pool
            **kwargs: Additional parameters

        Returns:
            Future object or None if error
        """
        try:
            # Update max workers if specified
            if max_workers is not None:
                with self._lock:
                    if self._max_workers != max_workers:
                        self._max_workers = max_workers
                        # Recreate executor if it was shut down
                        if self._executor and self._executor._shutdown:
                            self._executor = None

            executor = self._get_executor()
            future = executor.submit(func, *args, **kwargs)

            with self._lock:
                self._stats["submitted"] += 1

            self.logger.debug(f"Task submitted: {func.__name__}")
            return future

        except Exception as e:
            self.logger.error(f"Error submitting task: {e}")
            with self._lock:
                self._stats["failed"] += 1
            return None

    def map(
        self,
        func: Callable[[T], R],
        iterable: Iterable[T],
        timeout: Optional[float] = None,
        max_workers: Optional[int] = None,
        **kwargs
    ) -> List[R]:
        """Map function over iterable using thread pool.

        Args:
            func: Function to apply to each item
            iterable: Iterable of items
            timeout: Optional timeout for each task
            max_workers: Optional max workers for this pool
            **kwargs: Additional parameters

        Returns:
            List of results
        """
        try:
            # Update max workers if specified
            if max_workers is not None:
                with self._lock:
                    if self._max_workers != max_workers:
                        self._max_workers = max_workers
                        if self._executor and self._executor._shutdown:
                            self._executor = None

            executor = self._get_executor()

            results = []
            futures = []
            for item in iterable:
                future = executor.submit(func, item)
                futures.append(future)
                with self._lock:
                    self._stats["submitted"] += 1

            # Wait for all futures to complete
            for future in as_completed(futures, timeout=timeout):
                try:
                    result = future.result()
                    results.append(result)
                    with self._lock:
                        self._stats["completed"] += 1
                except Exception as e:
                    self.logger.error(f"Error in map task: {e}")
                    with self._lock:
                        self._stats["failed"] += 1

            return results

        except Exception as e:
            self.logger.error(f"Error in map: {e}")
            return []

    def shutdown(self, wait: bool = True, **kwargs) -> bool:
        """Shutdown thread pool.

        Args:
            wait: Wait for pending tasks to complete
            **kwargs: Additional parameters

        Returns:
            True if shutdown successful
        """
        try:
            with self._lock:
                if self._executor is not None and not self._executor._shutdown:
                    self._executor.shutdown(wait=wait)
                    self.logger.info("Thread pool shutdown")
            return True
        except Exception as e:
            self.logger.error(f"Error shutting down thread pool: {e}")
            return False

    def get_stats(self, **kwargs) -> Dict[str, Any]:
        """Get thread pool statistics.

        Args:
            **kwargs: Additional parameters

        Returns:
            Thread pool statistics
        """
        with self._lock:
            is_active = (
                self._executor is not None
                and not self._executor._shutdown
            )

            return {
                "max_workers": self._max_workers,
                "active": is_active,
                "submitted": self._stats["submitted"],
                "completed": self._stats["completed"],
                "failed": self._stats["failed"],
                "cancelled": self._stats["cancelled"],
                "pending": self._stats["submitted"] - self._stats["completed"] - self._stats["failed"],
            }


__all__ = [
    "ThreadingFactory",
]
