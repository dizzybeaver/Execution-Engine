"""
gateway_wrappers.py - Gateway Convenience Wrapper Functions (Main Module)
Version: 2025.11.20.01
Description: Main module that imports and re-exports all interface wrappers

STRUCTURE:
- gateway_wrappers_cache.py - CACHE interface (6 functions)
- gateway_wrappers_logging.py - LOGGING interface (7 functions)
- gateway_wrappers_security.py - SECURITY interface (16 functions)
- gateway_wrappers_metrics.py - METRICS interface (8 functions)
- gateway_wrappers_config.py - CONFIG interface (20 functions)
- gateway_wrappers_singleton.py - SINGLETON interface (13 functions) ← UPDATED 2025.11.20.01
- gateway_wrappers_initialization.py - INITIALIZATION interface (4 functions)
- gateway_wrappers_http_client.py - HTTP_CLIENT interface (8 functions)
- gateway_wrappers_websocket.py - WEBSOCKET interface (5 functions)
- gateway_wrappers_circuit_breaker.py - CIRCUIT_BREAKER interface (6 functions)
- gateway_wrappers_utility.py - UTILITY interface (5 functions)
- gateway_wrappers_debug.py - DEBUG interface (13 functions)

Copyright 2025 Joseph Hersey
Licensed under the Apache License, Version 2.0
"""

# Import all interface-specific wrappers
from gateway_wrappers_cache import *
from gateway_wrappers_logging import *
from gateway_wrappers_security import *
from gateway_wrappers_metrics import *
from gateway_wrappers_config import *
from gateway_wrappers_singleton import *
from gateway_wrappers_initialization import *
from gateway_wrappers_http_client import *
from gateway_wrappers_websocket import *
from gateway_wrappers_circuit_breaker import *
from gateway_wrappers_utility import *
from gateway_wrappers_debug import *

# Re-export everything
__all__ = [
    # CACHE wrappers (6)
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    
    # LOGGING wrappers (7)
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
    
    # SECURITY wrappers (16)
    'validate_request',
    'validate_token',
    'encrypt_data',
    'decrypt_data',
    'generate_correlation_id',
    'validate_string',
    'validate_email',
    'validate_url',
    'hash_data',
    'verify_hash',
    'sanitize_input',
    'sanitize_for_log',
    'validate_cache_key',
    'validate_ttl',
    'validate_module_name',
    'validate_number_range',
    
    # METRICS wrappers (8)
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    'get_performance_report',
    
    # CONFIG wrappers (20)
    'initialize_config',
    'get_cache_config',
    'get_metrics_config',
    'get_config',
    'set_config',
    'get_config_category',
    'reload_config',
    'switch_config_preset',
    'get_config_state',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    'config_initialize',
    'config_get_parameter',
    'config_set_parameter',
    'config_delete_parameter',
    'config_validate_parameter',
    'config_validate_all',
    'config_get_state',
    'config_reset',
    
    # SINGLETON wrappers (13) ← UPDATED 2025.11.20.01: Added singleton_register
    'singleton_get',
    'singleton_set',
    'singleton_register',  # ADDED: Missing function causing import errors
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    'get_memory_stats',
    'get_comprehensive_memory_stats',
    'check_lambda_memory_compliance',
    'force_memory_cleanup',
    'optimize_memory',
    'force_comprehensive_memory_cleanup',
    'emergency_memory_preserve',
    
    # INITIALIZATION wrappers (4)
    'initialize_system',
    'get_initialization_status',
    'set_initialization_flag',
    'get_initialization_flag',
    
    # HTTP_CLIENT wrappers (8)
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'http_reset',
    'http_get_state',
    'http_reset_state',
    
    # WEBSOCKET wrappers (5)
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    
    # CIRCUIT_BREAKER wrappers (6)
    'is_circuit_breaker_open',
    'get_circuit_breaker_state',
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    
    # UTILITY wrappers (5)
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    
    # DEBUG wrappers (13)
    'check_component_health',
    'check_gateway_health',
    'diagnose_system_health',
    'run_debug_tests',
    'validate_system_architecture',
    'check_config_health',
    'diagnose_config_performance',
    'validate_config_configuration',
    'benchmark_config_operations',
    'check_http_client_health',
    'diagnose_http_client_performance',
    'validate_http_client_configuration',
    'benchmark_http_client_operations',
]

# EOF
