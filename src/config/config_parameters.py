"""
config/config_parameters.py
Version: 2025-12-09_1
Purpose: Configuration parameter operations with SSM-first priority
License: Apache 2.0
"""

import os
from typing import Dict, Any, Optional
from config.config_core import get_config_manager


def initialize_config() -> Dict[str, Any]:
    """Initialize configuration system."""
    import gateway
    
    manager = get_config_manager()
    
    try:
        with gateway.debug_timing("CONFIG", "CONFIG", "initialize"):
            # Check USE_PARAMETER_STORE flag
            use_ssm = os.getenv('USE_PARAMETER_STORE', 'false').lower() == 'true'
            manager._use_parameter_store = use_ssm
            
            gateway.debug_log("CONFIG", "CONFIG", "Initializing config",
                            use_ssm=use_ssm,
                            prefix=manager._parameter_prefix)
            
            # Load environment config
            from config.config_loader import load_from_environment
            env_config = load_from_environment()
            manager._config.update(env_config)
            
            manager._initialized = True
            
            return {
                'success': True,
                'use_parameter_store': use_ssm,
                'parameter_count': len(manager._config)
            }
            
    except Exception as e:
        gateway.log_error(f"Config initialization failed: {e}")
        return {'success': False, 'error': str(e)}


def get_parameter(key: str, default: Any = None) -> Any:
    """
    Get configuration parameter with SSM-first priority.
    
    Priority:
    1. SSM Parameter Store (if USE_PARAMETER_STORE=true)
    2. Environment variable
    3. Default value
    """
    import gateway
    
    manager = get_config_manager()
    
    if manager._check_rate_limit():
        gateway.log_warning(f"Config get_parameter rate limited: {key}")
        return default
    
    gateway.debug_log("CONFIG", "CONFIG", "Getting parameter", key=key)
    
    # Check cache first
    if key in manager._config:
        value = manager._config[key]
        if value is not None and not isinstance(value, object) or value != object():
            gateway.debug_log("CONFIG", "CONFIG", "Cache hit", key=key)
            return value
    
    # SSM Parameter Store (if enabled)
    if manager._use_parameter_store:
        try:
            ssm_key = f"{manager._parameter_prefix}/{key}"
            gateway.debug_log("CONFIG", "CONFIG", "Checking SSM", ssm_key=ssm_key)
            
            value = _get_ssm_parameter(ssm_key)
            if value is not None:
                manager._config[key] = value
                gateway.debug_log("CONFIG", "CONFIG", "SSM hit", key=key)
                return value
                
        except Exception as e:
            gateway.log_warning(f"SSM get failed for {key}: {e}")
    
    # Environment variable fallback
    env_value = os.getenv(key)
    if env_value is not None:
        manager._config[key] = env_value
        gateway.debug_log("CONFIG", "CONFIG", "Environment hit", key=key)
        return env_value
    
    # Default value
    gateway.debug_log("CONFIG", "CONFIG", "Using default", key=key, default=default)
    return default


def set_parameter(key: str, value: Any) -> bool:
    """Set configuration parameter."""
    import gateway
    
    manager = get_config_manager()
    
    if manager._check_rate_limit():
        gateway.log_warning(f"Config set_parameter rate limited: {key}")
        return False
    
    try:
        with gateway.debug_timing("CONFIG", "CONFIG", "set_parameter"):
            gateway.debug_log("CONFIG", "CONFIG", "Setting parameter", 
                            key=key, value_type=type(value).__name__)
            
            manager._config[key] = value
            return True
            
    except Exception as e:
        gateway.log_error(f"Config set_parameter failed for {key}: {e}")
        return False


def get_category_config(category: str) -> Dict[str, Any]:
    """Get configuration for a category."""
    import gateway
    
    manager = get_config_manager()
    
    gateway.debug_log("CONFIG", "CONFIG", "Getting category config", category=category)
    
    # Filter config keys by category prefix
    category_config = {}
    prefix = f"{category}."
    
    for key, value in manager._config.items():
        if key.startswith(prefix):
            # Remove category prefix from key
            short_key = key[len(prefix):]
            category_config[short_key] = value
    
    gateway.debug_log("CONFIG", "CONFIG", "Category config retrieved",
                     category=category, key_count=len(category_config))
    
    return category_config


def get_state() -> Dict[str, Any]:
    """Get configuration state."""
    import gateway
    
    manager = get_config_manager()
    
    return {
        'initialized': manager._initialized,
        'use_parameter_store': manager._use_parameter_store,
        'parameter_prefix': manager._parameter_prefix,
        'config_keys': list(manager._config.keys()),
        'rate_limited_count': manager._rate_limited_count
    }


def _get_ssm_parameter(key: str) -> Optional[Any]:
    """Get parameter from SSM Parameter Store."""
    try:
        import boto3
        ssm_client = boto3.client('ssm')
        
        response = ssm_client.get_parameter(
            Name=key,
            WithDecryption=True
        )
        
        return response['Parameter']['Value']
        
    except Exception:
        return None


__all__ = [
    'initialize_config',
    'get_parameter',
    'set_parameter',
    'get_category_config',
    'get_state'
]
