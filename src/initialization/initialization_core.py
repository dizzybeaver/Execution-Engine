"""
initialization/initialization_core.py
Version: 2025-12-13_1
Purpose: Gateway implementation functions for initialization interface
License: Apache 2.0
"""

from typing import Dict, Any

from initialization.initialization_manager import (
    InitializationOperation,
    get_initialization_manager
)


def execute_initialization_operation(operation: InitializationOperation, 
                                     correlation_id: str = None, **kwargs):
    """
    Universal initialization operation executor with error handling.
    
    Args:
        operation: InitializationOperation enum value
        correlation_id: Optional correlation ID for debug tracking
        **kwargs: Operation-specific parameters
        
    Returns:
        Operation result from InitializationCore
        
    Raises:
        ValueError: If operation is unknown
        Exception: If operation execution fails
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "INIT",
             "execute_initialization_operation called",
             operation=operation.value if isinstance(operation, InitializationOperation) else str(operation))
    
    try:
        manager = get_initialization_manager()
        
        if operation == InitializationOperation.INITIALIZE:
            return manager.initialize(correlation_id=correlation_id, **kwargs)
        elif operation == InitializationOperation.GET_CONFIG:
            return manager.get_config(correlation_id=correlation_id)
        elif operation == InitializationOperation.IS_INITIALIZED:
            return manager.is_initialized(correlation_id=correlation_id)
        elif operation == InitializationOperation.RESET:
            return manager.reset(correlation_id=correlation_id)
        elif operation == InitializationOperation.GET_STATUS:
            return manager.get_status(correlation_id=correlation_id)
        elif operation == InitializationOperation.GET_STATS:
            return manager.get_stats(correlation_id=correlation_id)
        elif operation == InitializationOperation.SET_FLAG:
            return manager.set_flag(correlation_id=correlation_id, **kwargs)
        elif operation == InitializationOperation.GET_FLAG:
            return manager.get_flag(correlation_id=correlation_id, **kwargs)
        else:
            raise ValueError(f"Unknown initialization operation: {operation}")
    except Exception as e:
        debug_log(correlation_id, "INIT",
                 f"Operation failed: {str(e)}",
                 operation=operation.value if isinstance(operation, InitializationOperation) else str(operation))
        raise Exception(f"Initialization operation '{operation.value}' failed: {e}") from e


def initialize_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Execute initialization operation.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
        **kwargs: Configuration parameters
    
    Returns:
        Initialization status dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "INIT", "initialize_implementation called",
             kwargs_count=len(kwargs))
    
    return get_initialization_manager().initialize(correlation_id=correlation_id, **kwargs)


def get_config_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Execute get config operation.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Configuration dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "INIT", "get_config_implementation called")
    
    return get_initialization_manager().get_config(correlation_id=correlation_id)


def is_initialized_implementation(correlation_id: str = None, **kwargs) -> bool:
    """
    Execute is initialized check.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        True if initialized, False otherwise
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "INIT", "is_initialized_implementation called")
    
    return get_initialization_manager().is_initialized(correlation_id=correlation_id)


def reset_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Execute reset operation.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Reset status dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "INIT", "reset_implementation called")
    
    return get_initialization_manager().reset(correlation_id=correlation_id)


def get_status_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Execute get status operation.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Status dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "INIT", "get_status_implementation called")
    
    return get_initialization_manager().get_status(correlation_id=correlation_id)


def get_stats_implementation(correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Execute get stats operation.
    
    Args:
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Statistics dict
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    debug_log(correlation_id, "INIT", "get_stats_implementation called")
    
    return get_initialization_manager().get_stats(correlation_id=correlation_id)


def set_flag_implementation(flag_name: str, value: Any, 
                            correlation_id: str = None, **kwargs) -> Dict[str, Any]:
    """
    Execute set flag operation.
    
    Args:
        flag_name: Flag name
        value: Flag value
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Set flag result dict
    
    Raises:
        ValueError: If flag_name or value missing
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not flag_name:
        raise ValueError("Parameter 'flag_name' is required for set_flag operation")
    
    debug_log(correlation_id, "INIT", "set_flag_implementation called",
             flag_name=flag_name, has_value=value is not None)
    
    return get_initialization_manager().set_flag(
        flag_name=flag_name,
        value=value,
        correlation_id=correlation_id
    )


def get_flag_implementation(flag_name: str, default: Any = None,
                            correlation_id: str = None, **kwargs) -> Any:
    """
    Execute get flag operation.
    
    Args:
        flag_name: Flag name
        default: Default value if flag doesn't exist
        correlation_id: Optional correlation ID for debug tracking
    
    Returns:
        Flag value or default
    
    Raises:
        ValueError: If flag_name missing
    """
    # ADDED: Debug integration
    from gateway import debug_log, generate_correlation_id
    
    if correlation_id is None:
        correlation_id = generate_correlation_id()
    
    if not flag_name:
        raise ValueError("Parameter 'flag_name' is required for get_flag operation")
    
    debug_log(correlation_id, "INIT", "get_flag_implementation called",
             flag_name=flag_name)
    
    return get_initialization_manager().get_flag(
        flag_name=flag_name,
        default=default,
        correlation_id=correlation_id
    )


__all__ = [
    'execute_initialization_operation',
    'initialize_implementation',
    'get_config_implementation',
    'is_initialized_implementation',
    'reset_implementation',
    'get_status_implementation',
    'get_stats_implementation',
    'set_flag_implementation',
    'get_flag_implementation',
]
