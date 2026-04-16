"""Singleton Wrapper Functions

Direct access to singleton operations (39 functions).
All functions execute via gateway internally.

Usage:
    from lee.gateway.wrappers import singleton

    # Get singleton instance
    instance = singleton.get(name='cache')

    # Set singleton value
    singleton.set(name='cache', value=my_cache_instance)

    # Check if singleton exists
    exists = singleton.has(name='cache')

    # Register singleton factory
    singleton.register(name='cache', factory=lambda: Cache())

    # Delete singleton
    singleton.delete(name='cache')
"""

from typing import Any, Optional
from collections.abc import Callable

from lee.gateway.gateway_core import GatewayInterface, execute_operation


def singleton_get(name: str, **kwargs: Any) -> Any:
    """Get singleton instance.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        Singleton instance or None if not found
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get', name=name, **kwargs)


def singleton_set(name: str, value: Any, **kwargs: Any) -> None:
    """Set singleton value.

    Args:
        name: Singleton name
        value: Value to set
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'set', name=name, value=value, **kwargs)


def singleton_register(name: str, factory: Callable[[], Any], **kwargs: Any) -> None:
    """Register singleton factory.

    Args:
        name: Singleton name
        factory: Factory function to create instance
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'register', name=name, factory=factory, **kwargs)


def singleton_has(name: str, **kwargs: Any) -> bool:
    """Check if singleton exists.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        True if singleton exists, False otherwise
    """
    return execute_operation(GatewayInterface.SINGLETON, 'has', name=name, **kwargs)


def singleton_exists(name: str, **kwargs: Any) -> bool:
    """Alias for has() - check if singleton exists.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        True if singleton exists, False otherwise
    """
    return execute_operation(GatewayInterface.SINGLETON, 'exists', name=name, **kwargs)


def singleton_delete(name: str, **kwargs: Any) -> bool:
    """Delete singleton.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        True if deleted, False if not found
    """
    return execute_operation(GatewayInterface.SINGLETON, 'delete', name=name, **kwargs)


def singleton_clear(**kwargs: Any) -> None:
    """Clear all singletons.

    Args:
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'clear', **kwargs)


def singleton_get_all(**kwargs: Any) -> dict[str, Any]:
    """Get all singletons.

    Args:
        **kwargs: Additional options

    Returns:
        Dictionary of all singleton instances
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_all', **kwargs)


def singleton_get_all_names(**kwargs: Any) -> list[str]:
    """Get all singleton names.

    Args:
        **kwargs: Additional options

    Returns:
        List of singleton names
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_all_names', **kwargs)


def singleton_get_stats(**kwargs: Any) -> dict[str, Any]:
    """Get singleton statistics.

    Args:
        **kwargs: Additional options

    Returns:
        Dictionary with singleton stats
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_stats', **kwargs)


def singleton_reset_stats(**kwargs: Any) -> None:
    """Reset singleton statistics.

    Args:
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'reset_stats', **kwargs)


def singleton_is_initialized(name: str, **kwargs: Any) -> bool:
    """Check if singleton is initialized.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        True if initialized, False otherwise
    """
    return execute_operation(GatewayInterface.SINGLETON, 'is_initialized', name=name, **kwargs)


def singleton_initialize(name: str, instance: Any, **kwargs: Any) -> None:
    """Initialize singleton with instance.

    Args:
        name: Singleton name
        instance: Instance to initialize with
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'initialize', name=name, instance=instance, **kwargs)


def singleton_get_or_create(name: str, factory: Callable[[], Any], **kwargs: Any) -> Any:
    """Get singleton or create if not exists.

    Args:
        name: Singleton name
        factory: Factory function to create instance
        **kwargs: Additional options

    Returns:
        Singleton instance
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_or_create', name=name, factory=factory, **kwargs)


def singleton_get_or_compute(name: str, compute_fn: Callable[[], Any], **kwargs: Any) -> Any:
    """Get singleton or compute if not exists.

    Args:
        name: Singleton name
        compute_fn: Function to compute instance
        **kwargs: Additional options

    Returns:
        Singleton instance
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_or_compute', name=name, compute_fn=compute_fn, **kwargs)


def singleton_register_factory(name: str, factory: Callable[[], Any], **kwargs: Any) -> None:
    """Register singleton factory.

    Args:
        name: Singleton name
        factory: Factory function
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'register_factory', name=name, factory=factory, **kwargs)


def singleton_register_instance(name: str, instance: Any, **kwargs: Any) -> None:
    """Register singleton instance.

    Args:
        name: Singleton name
        instance: Instance to register
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'register_instance', name=name, instance=instance, **kwargs)


def singleton_register_lazy(name: str, factory: Callable[[], Any], **kwargs: Any) -> None:
    """Register lazy singleton (created on first access).

    Args:
        name: Singleton name
        factory: Factory function
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'register_lazy', name=name, factory=factory, **kwargs)


def singleton_get_metadata(name: str, **kwargs: Any) -> dict[str, Any]:
    """Get singleton metadata.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        Metadata dictionary
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_metadata', name=name, **kwargs)


def singleton_set_metadata(name: str, metadata: dict[str, Any], **kwargs: Any) -> None:
    """Set singleton metadata.

    Args:
        name: Singleton name
        metadata: Metadata dictionary
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'set_metadata', name=name, metadata=metadata, **kwargs)


def singleton_get_or_create_metadata(name: str, **kwargs: Any) -> dict[str, Any]:
    """Get or create singleton metadata.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        Metadata dictionary
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_or_create_metadata', name=name, **kwargs)


def singleton_validate_all(**kwargs: Any) -> tuple[bool, list[str]]:
    """Validate all singletons.

    Args:
        **kwargs: Additional options

    Returns:
        Tuple of (is_valid, error_messages)
    """
    return execute_operation(GatewayInterface.SINGLETON, 'validate_all', **kwargs)


def singleton_validate_instance(name: str, **kwargs: Any) -> tuple[bool, Optional[str]]:
    """Validate singleton instance.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        Tuple of (is_valid, error_message)
    """
    return execute_operation(GatewayInterface.SINGLETON, 'validate_instance', name=name, **kwargs)


def singleton_get_factory(name: str, **kwargs: Any) -> Optional[Callable[[], Any]]:
    """Get singleton factory.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        Factory function or None
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_factory', name=name, **kwargs)


def singleton_set_factory(name: str, factory: Callable[[], Any], **kwargs: Any) -> None:
    """Set singleton factory.

    Args:
        name: Singleton name
        factory: Factory function
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'set_factory', name=name, factory=factory, **kwargs)


def singleton_get_instance(name: str, **kwargs: Any) -> Any:
    """Get singleton instance (alias for get).

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        Singleton instance or None
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_instance', name=name, **kwargs)


def singleton_set_instance(name: str, instance: Any, **kwargs: Any) -> None:
    """Set singleton instance (alias for set).

    Args:
        name: Singleton name
        instance: Instance to set
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'set_instance', name=name, instance=instance, **kwargs)


def singleton_clear_instance(name: str, **kwargs: Any) -> None:
    """Clear singleton instance.

    Args:
        name: Singleton name
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'clear_instance', name=name, **kwargs)


def singleton_get_dependencies(name: str, **kwargs: Any) -> list[str]:
    """Get singleton dependencies.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        List of dependency names
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_dependencies', name=name, **kwargs)


def singleton_set_dependencies(name: str, dependencies: list[str], **kwargs: Any) -> None:
    """Set singleton dependencies.

    Args:
        name: Singleton name
        dependencies: List of dependency names
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'set_dependencies', name=name, dependencies=dependencies, **kwargs)


def singleton_add_dependency(name: str, dependency: str, **kwargs: Any) -> None:
    """Add singleton dependency.

    Args:
        name: Singleton name
        dependency: Dependency name to add
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'add_dependency', name=name, dependency=dependency, **kwargs)


def singleton_remove_dependency(name: str, dependency: str, **kwargs: Any) -> None:
    """Remove singleton dependency.

    Args:
        name: Singleton name
        dependency: Dependency name to remove
        **kwargs: Additional options
    """
    execute_operation(GatewayInterface.SINGLETON, 'remove_dependency', name=name, dependency=dependency, **kwargs)


def singleton_get_dependency_graph(**kwargs: Any) -> dict[str, list[str]]:
    """Get singleton dependency graph.

    Args:
        **kwargs: Additional options

    Returns:
        Dictionary mapping names to dependencies
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_dependency_graph', **kwargs)


def singleton_validate_dependencies(**kwargs: Any) -> tuple[bool, list[str]]:
    """Validate singleton dependencies.

    Args:
        **kwargs: Additional options

    Returns:
        Tuple of (is_valid, error_messages)
    """
    return execute_operation(GatewayInterface.SINGLETON, 'validate_dependencies', **kwargs)


def singleton_get_or_create_dependency(name: str, dependency: str, factory: Callable[[], Any], **kwargs: Any) -> Any:
    """Get or create singleton dependency.

    Args:
        name: Singleton name
        dependency: Dependency name
        factory: Factory function
        **kwargs: Additional options

    Returns:
        Dependency instance
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_or_create_dependency', name=name, dependency=dependency, factory=factory, **kwargs)


def singleton_lock(name: str, **kwargs: Any) -> bool:
    """Lock singleton.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        True if locked, False if already locked
    """
    return execute_operation(GatewayInterface.SINGLETON, 'lock', name=name, **kwargs)


def singleton_unlock(name: str, **kwargs: Any) -> bool:
    """Unlock singleton.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        True if unlocked, False if not locked
    """
    return execute_operation(GatewayInterface.SINGLETON, 'unlock', name=name, **kwargs)


def singleton_is_locked(name: str, **kwargs: Any) -> bool:
    """Check if singleton is locked.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        True if locked, False otherwise
    """
    return execute_operation(GatewayInterface.SINGLETON, 'is_locked', name=name, **kwargs)


def singleton_wait_for_lock(name: str, timeout: float = 5.0, **kwargs: Any) -> bool:
    """Wait for singleton lock.

    Args:
        name: Singleton name
        timeout: Maximum time to wait in seconds
        **kwargs: Additional options

    Returns:
        True if lock acquired, False if timeout
    """
    return execute_operation(GatewayInterface.SINGLETON, 'wait_for_lock', name=name, timeout=timeout, **kwargs)


def singleton_get_lock_info(name: str, **kwargs: Any) -> dict[str, Any]:
    """Get singleton lock information.

    Args:
        name: Singleton name
        **kwargs: Additional options

    Returns:
        Lock information dictionary
    """
    return execute_operation(GatewayInterface.SINGLETON, 'get_lock_info', name=name, **kwargs)


def singleton_release_all_locks(**kwargs: Any) -> int:
    """Release all singleton locks.

    Args:
        **kwargs: Additional options

    Returns:
        Number of locks released
    """
    return execute_operation(GatewayInterface.SINGLETON, 'release_all_locks', **kwargs)


# Convenience aliases without singleton_ prefix
get = singleton_get
set_value = singleton_set  # Avoid shadowing built-in 'set'
has = singleton_has
delete = singleton_delete
clear = singleton_clear


__all__ = [
    'singleton_get',
    'singleton_set',
    'singleton_register',
    'singleton_has',
    'singleton_delete',
    'singleton_exists',
    'singleton_clear',
    'singleton_get_all',
    'singleton_get_all_names',
    'singleton_get_stats',
    'singleton_reset_stats',
    'singleton_is_initialized',
    'singleton_initialize',
    'singleton_get_or_create',
    'singleton_get_or_compute',
    'singleton_register_factory',
    'singleton_register_instance',
    'singleton_register_lazy',
    'singleton_get_metadata',
    'singleton_set_metadata',
    'singleton_get_or_create_metadata',
    'singleton_validate_all',
    'singleton_validate_instance',
    'singleton_get_factory',
    'singleton_set_factory',
    'singleton_get_instance',
    'singleton_set_instance',
    'singleton_clear_instance',
    'singleton_get_dependencies',
    'singleton_set_dependencies',
    'singleton_add_dependency',
    'singleton_remove_dependency',
    'singleton_get_dependency_graph',
    'singleton_validate_dependencies',
    'singleton_get_or_create_dependency',
    'singleton_lock',
    'singleton_unlock',
    'singleton_is_locked',
    'singleton_wait_for_lock',
    'singleton_get_lock_info',
    'singleton_release_all_locks',
    # Convenience aliases
    'get',
    'set_value',
    'has',
    'delete',
    'clear',
]
