"""
lambda_diagnostic.py
Version: 2025-12-14_1
Purpose: Diagnostic mode handler (wrapper for DIAGNOSIS interface)
License: Apache 2.0
"""

from typing import Dict, Any
from gateway import test_import_sequence


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Diagnostic mode handler - tests module imports sequentially."""
    
    # Define critical modules to test in order (updated for new structure)
    modules = [
        # Gateway core
        'gateway.gateway_core',
        'gateway.gateway_enums',
        
        # Gateway wrappers
        'gateway.wrappers.gateway_wrappers_cache',
        'gateway.wrappers.gateway_wrappers_logging',
        'gateway.wrappers.gateway_wrappers_security',
        'gateway.wrappers.gateway_wrappers_metrics',
        'gateway.wrappers.gateway_wrappers_config',
        'gateway.wrappers.gateway_wrappers_singleton',
        'gateway.wrappers.gateway_wrappers_initialization',
        'gateway.wrappers.gateway_wrappers_http_client',
        'gateway.wrappers.gateway_wrappers_websocket',
        'gateway.wrappers.gateway_wrappers_circuit_breaker',
        'gateway.wrappers.gateway_wrappers_utility',
        'gateway.wrappers.gateway_wrappers_debug',
        'gateway.wrappers.gateway_wrappers_diagnosis',
        'gateway.wrappers.gateway_wrappers_test',
        'gateway.wrappers.gateway_wrappers_zaph',
        
        # Gateway main
        'gateway',
        
        # Interfaces
        'interface.interface_cache',
        'interface.interface_logging',
        'interface.interface_security',
        'interface.interface_metrics',
        'interface.interface_config',
        'interface.interface_singleton',
        'interface.interface_initialization',
        'interface.interface_http',
        'interface.interface_websocket',
        'interface.interface_circuit_breaker',
        'interface.interface_utility',
        'interface.interface_debug',
        'interface.interface_diagnosis',
        'interface.interface_test',
        'interface.interface_zaph',
        
        # Core implementations
        'cache.cache_core',
        'logging.logging_core',
        'security.security_core',
        'metrics.metrics_core',
        'config.config_core',
        'singleton.singleton_core',
        'zaph.zaph_core',
    ]
    
    # Use DIAGNOSIS interface via gateway
    return test_import_sequence(modules)

# EOF
