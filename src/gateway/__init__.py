"""
gateway/__init__.py - Gateway Package Initialization
Version: 2025-12-14_1
Purpose: Central gateway entry point for all LEE operations
License: Apache 2.0

This module provides the single gateway entry point for all LEE operations
following the SUGA (Single Universal Gateway Architecture) pattern.
"""

from gateway.gateway_enums import GatewayInterface

from gateway.gateway_core import (
    execute_operation,
    get_gateway_stats,
    reset_gateway_state,
    create_error_response,
    create_success_response,
)

# Import all wrapper functions
from gateway.wrappers.gateway_wrappers_cache import *
from gateway.wrappers.gateway_wrappers_logging import *
from gateway.wrappers.gateway_wrappers_security import *
from gateway.wrappers.gateway_wrappers_metrics import *
from gateway.wrappers.gateway_wrappers_config import *
from gateway.wrappers.gateway_wrappers_singleton import *
from gateway.wrappers.gateway_wrappers_initialization import *
from gateway.wrappers.gateway_wrappers_http_client import *
from gateway.wrappers.gateway_wrappers_websocket import *
from gateway.wrappers.gateway_wrappers_circuit_breaker import *
from gateway.wrappers.gateway_wrappers_utility import *
from gateway.wrappers.gateway_wrappers_debug import *
from gateway.wrappers.gateway_wrappers_diagnosis import *
from gateway.wrappers.gateway_wrappers_test import *
from gateway.wrappers.gateway_wrappers_zaph import *

__all__ = [
    # Core gateway functions
    'GatewayInterface',
    'execute_operation',
    'get_gateway_stats',
    'reset_gateway_state',
    'create_error_response',
    'create_success_response',
    
    # CACHE interface (6 functions)
    'cache_get',
    'cache_set',
    'cache_exists',
    'cache_delete',
    'cache_clear',
    'cache_stats',
    
    # LOGGING interface (7 functions)
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_operation_start',
    'log_operation_success',
    'log_operation_failure',
    
    # SECURITY interface (16 functions)
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
    
    # METRICS interface (18 functions)
    'record_metric',
    'increment_counter',
    'get_metrics_stats',
    'record_operation_metric',
    'record_error_metric',
    'record_cache_metric',
    'record_api_metric',
    'record_response_metric',
    'record_http_metric',
    'record_circuit_breaker_metric',
    'get_response_metrics',
    'get_http_metrics',
    'get_circuit_breaker_metrics',
    'record_dispatcher_timing',
    'get_dispatcher_stats',
    'get_operation_metrics',
    'get_performance_report',
    'reset_metrics',
    
    # CONFIG interface (21 functions)
    'config_initialize',
    'config_get_parameter',
    'config_set_parameter',
    'config_get_category',
    'config_get_state',
    'config_reload',
    'config_switch_preset',
    'config_load_environment',
    'config_load_file',
    'config_validate_all',
    'config_reset',
    'initialize_config',
    'get_config',
    'set_config',
    'get_config_category',
    'get_config_state',
    'reload_config',
    'switch_config_preset',
    'load_config_from_environment',
    'load_config_from_file',
    'validate_all_config',
    
    # SINGLETON interface (16 functions)
    'singleton_get',
    'singleton_set',
    'singleton_register',
    'singleton_has',
    'singleton_delete',
    'singleton_clear',
    'singleton_stats',
    'singleton_get_stats',
    'singleton_reset',
    'get_memory_stats',
    'get_comprehensive_memory_stats',
    'check_lambda_memory_compliance',
    'force_memory_cleanup',
    'optimize_memory',
    'force_comprehensive_memory_cleanup',
    'emergency_memory_preserve',
    
    # INITIALIZATION interface (5 functions)
    'initialize_system',
    'get_initialization_status',
    'initialization_get_stats',
    'set_initialization_flag',
    'get_initialization_flag',
    
    # HTTP_CLIENT interface (8 functions)
    'http_request',
    'http_get',
    'http_post',
    'http_put',
    'http_delete',
    'http_reset',
    'http_get_state',
    'http_reset_state',
    
    # WEBSOCKET interface (7 functions)
    'websocket_connect',
    'websocket_send',
    'websocket_receive',
    'websocket_close',
    'websocket_request',
    'websocket_get_stats',
    'websocket_reset',
    
    # CIRCUIT_BREAKER interface (8 functions)
    'is_circuit_breaker_open',
    'get_circuit_breaker_state',
    'get_circuit_breaker',
    'execute_with_circuit_breaker',
    'get_all_circuit_breaker_states',
    'reset_all_circuit_breakers',
    'get_circuit_breaker_stats',
    'reset_circuit_breaker_manager',
    
    # UTILITY interface (9 functions)
    'format_response',
    'parse_json',
    'safe_get',
    'generate_uuid',
    'get_timestamp',
    'utility_get_stats',
    'utility_reset',
    'render_template',
    'config_get',
    
    # DEBUG interface (7 functions)
    'debug_log',
    'debug_timing',
    'generate_trace_id',
    'set_trace_context',
    'get_trace_context',
    'clear_trace_context',
    
    # DIAGNOSIS interface (21 functions)
    'test_module_import',
    'test_import_sequence',
    'format_diagnostic_response',
    'diagnose_import_failure',
    'diagnose_system_health',
    'diagnose_component_performance',
    'diagnose_memory_usage',
    'diagnose_initialization_performance',
    'diagnose_utility_performance',
    'diagnose_singleton_performance',
    'validate_system_architecture',
    'validate_imports',
    'validate_gateway_routing',
    'run_diagnostic_suite',
    'check_component_health',
    'check_gateway_health',
    'generate_health_report',
    'check_initialization_health',
    'check_utility_health',
    'check_singleton_health',
    'check_system_health',
    
    # TEST interface (16 functions)
    'run_test_suite',
    'run_single_test',
    'run_component_tests',
    'test_component_operation',
    'test_invalid_operation',
    'test_missing_parameters',
    'test_graceful_degradation',
    'run_error_scenario_tests',
    'test_operation_performance',
    'test_component_performance',
    'benchmark_operation',
    'run_performance_tests',
    'test_lambda_mode',
    'test_emergency_mode',
    'test_failsafe_mode',
    'test_diagnostic_mode',
    
    # ZAPH interface (18 functions)
    'zaph_track_operation',
    'zaph_execute',
    'zaph_register',
    'zaph_get',
    'zaph_is_hot',
    'zaph_should_protect',
    'zaph_heat_level',
    'zaph_stats',
    'zaph_hot_operations',
    'zaph_cached_operations',
    'zaph_configure',
    'zaph_config',
    'zaph_prewarm',
    'zaph_prewarm_common',
    'zaph_clear',
    'zaph_reset_counts',
    'zaph_reset_stats',
    'zaph_optimize',
]

__version__ = '2025-12-14_1'

# EOF
