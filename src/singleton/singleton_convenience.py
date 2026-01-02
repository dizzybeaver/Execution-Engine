"""
singleton_convenience.py
Version: 2025.10.14.01
Description: Singleton convenience wrappers using SUGA gateway pattern - PHASE 1 FIXED

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

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def get_named_singleton(name: str, factory_func: Optional[Any] = None) -> Optional[Any]:
    """
    Universal singleton accessor with SUGA gateway pattern.
    
    Args:
        name: Singleton instance name
        factory_func: Optional factory function to create singleton if it doesn't exist
        
    Returns:
        Singleton instance or None if not found and no factory provided
    """
    from gateway import execute_operation, GatewayInterface
    
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            'get',
            name=name,
            factory_func=factory_func
        )
    except Exception as e:
        logger.error(f"Failed to get singleton '{name}': {e}")
        return None


def get_cost_protection() -> Optional[Any]:
    """Get cost protection singleton."""
    return get_named_singleton('cost_protection')


def get_cache_manager() -> Optional[Any]:
    """Get cache manager singleton."""
    return get_named_singleton('cache_manager')


def get_security_validator() -> Optional[Any]:
    """Get security validator singleton."""
    return get_named_singleton('security_validator')


def get_unified_validator() -> Optional[Any]:
    """Get unified validator singleton."""
    return get_named_singleton('unified_validator')


def get_config_manager() -> Optional[Any]:
    """Get config manager singleton."""
    return get_named_singleton('config_manager')


def get_memory_manager() -> Optional[Any]:
    """Get memory manager singleton."""
    return get_named_singleton('memory_manager')


def get_lambda_cache() -> Optional[Any]:
    """Get lambda cache singleton."""
    return get_named_singleton('lambda_cache')


def get_response_cache() -> Optional[Any]:
    """Get response cache singleton."""
    return get_named_singleton('response_cache')


def get_circuit_breaker_manager() -> Optional[Any]:
    """Get circuit breaker manager singleton."""
    return get_named_singleton('circuit_breaker_manager')


def get_response_processor() -> Optional[Any]:
    """Get response processor singleton."""
    return get_named_singleton('response_processor')


def get_lambda_optimizer() -> Optional[Any]:
    """Get lambda optimizer singleton."""
    return get_named_singleton('lambda_optimizer')


def get_response_metrics_manager() -> Optional[Any]:
    """Get response metrics manager singleton."""
    return get_named_singleton('response_metrics_manager')


# ===== ADDITIONAL HELPER FUNCTIONS =====

def has_singleton(name: str) -> bool:
    """Check if a singleton exists."""
    from gateway import execute_operation, GatewayInterface
    
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            'has',
            name=name
        )
    except Exception as e:
        logger.error(f"Failed to check singleton '{name}': {e}")
        return False


def delete_singleton(name: str) -> bool:
    """Delete a specific singleton."""
    from gateway import execute_operation, GatewayInterface
    
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            'delete',
            name=name
        )
    except Exception as e:
        logger.error(f"Failed to delete singleton '{name}': {e}")
        return False


def clear_all_singletons() -> int:
    """Clear all singletons. Returns count cleared."""
    from gateway import execute_operation, GatewayInterface
    
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            'clear'
        )
    except Exception as e:
        logger.error(f"Failed to clear singletons: {e}")
        return 0


def get_singleton_stats() -> dict:
    """Get singleton statistics."""
    from gateway import execute_operation, GatewayInterface
    
    try:
        return execute_operation(
            GatewayInterface.SINGLETON,
            'get_stats'
        )
    except Exception as e:
        logger.error(f"Failed to get singleton stats: {e}")
        return {}


__all__ = [
    'get_named_singleton',
    'get_cost_protection',
    'get_cache_manager',
    'get_security_validator',
    'get_unified_validator',
    'get_config_manager',
    'get_memory_manager',
    'get_lambda_cache',
    'get_response_cache',
    'get_circuit_breaker_manager',
    'get_response_processor',
    'get_lambda_optimizer',
    'get_response_metrics_manager',
    'has_singleton',
    'delete_singleton',
    'clear_all_singletons',
    'get_singleton_stats',
]

# EOF
