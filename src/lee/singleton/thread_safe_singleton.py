# LEE Project Code File
# ASCII ONLY - No emojis, no unicode, no special characters
# Modified: 2026-04-03 - Thread-safe singleton base class

"""Thread-Safe Singleton Base Class

Provides a reusable, thread-safe singleton pattern implementation using
double-checked locking for optimal performance.

Usage:
    from lee.singleton.thread_safe_singleton import ThreadSafeSingleton

    class MySingleton(ThreadSafeSingleton):
        def __init__(self):
            if self._initialized:
                return
            self._initialized = True
            # Your initialization here

    instance = MySingleton.get_instance()

Thread Safety:
    - Double-checked locking pattern
    - Thread-safe initialization
    - Fast path after initialization (no locking)
"""

import threading
from typing import Generic, TypeVar, Optional
from collections.abc import Callable

T = TypeVar('T')


class ThreadSafeSingleton(Generic[T]):
    """Thread-safe singleton base class using double-checked locking.

    This class provides a reusable singleton pattern that ensures:
    - Only one instance exists
    - Thread-safe initialization
    - Fast access after initialization (no locking overhead)

    Attributes:
        _instance: Class-level storage for the singleton instance
        _lock: Class-level lock for thread-safe initialization
        _initialized: Instance-level flag to prevent re-initialization

    Example:
        class MySingleton(ThreadSafeSingleton):
            def __init__(self):
                if self._initialized:
                    return
                self._initialized = True
                self.value = 42

        instance = MySingleton.get_instance()
        print(instance.value)  # 42
    """

    _instance: Optional[T] = None
    _lock: threading.RLock = threading.RLock()

    def __new__(cls: type[T]) -> T:
        """Create or return the singleton instance.

        Uses double-checked locking for thread safety with minimal overhead.

        Returns:
            The singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the singleton (only called once).

        Subclasses should check self._initialized before performing
        initialization to prevent re-initialization.

        Example:
            def __init__(self):
                if self._initialized:
                    return
                self._initialized = True
                self.value = 42
        """

    @classmethod
    def get_instance(cls: type[T]) -> T:
        """Get the singleton instance.

        This is the preferred way to access the singleton.

        Returns:
            The singleton instance

        Example:
            instance = MySingleton.get_instance()
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the singleton has been initialized.

        Returns:
            True if the singleton instance exists
        """
        return cls._instance is not None

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing).

        WARNING: This should only be used in tests. Resetting the singleton
        in production code can lead to unexpected behavior.

        Example:
            MySingleton.reset_instance()
            instance = MySingleton.get_instance()  # Fresh instance
        """
        with cls._lock:
            cls._instance = None


class SingletonFactory(Generic[T]):
    """Factory for creating singleton instances with custom initialization.

    Useful when you need to create singletons with different configurations
    or when the singleton requires parameters.

    Example:
        factory = SingletonFactory(lambda: MyService(config={'key': 'value'}))
        instance = factory.get_instance()
    """

    def __init__(self, factory_func: Callable[[], T]):
        """Initialize the singleton factory.

        Args:
            factory_func: Function that creates the singleton instance
        """
        self._factory_func = factory_func
        self._instance: Optional[T] = None
        self._lock = threading.Lock()

    def get_instance(self) -> T:
        """Get or create the singleton instance.

        Returns:
            The singleton instance
        """
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._factory_func()
        return self._instance

    def is_initialized(self) -> bool:
        """Check if the singleton has been initialized.

        Returns:
            True if the singleton instance exists
        """
        return self._instance is not None

    def reset_instance(self) -> None:
        """Reset the singleton instance (for testing)."""
        with self._lock:
            self._instance = None


def singleton(cls: type[T]) -> type[T]:
    """Decorator to make a class a singleton.

    Simple decorator alternative to inheriting from ThreadSafeSingleton.

    Example:
        @singleton
        class MySingleton:
            def __init__(self):
                self.value = 42

        instance1 = MySingleton()
        instance2 = MySingleton()
        assert instance1 is instance2  # True
    """
    instance = None
    lock = threading.Lock()

    def get_instance(*args, **kwargs) -> T:
        nonlocal instance
        if instance is None:
            with lock:
                if instance is None:
                    instance = cls(*args, **kwargs)
        return instance

    return get_instance


__all__ = [
    'ThreadSafeSingleton',
    'SingletonFactory',
    'singleton',
]
