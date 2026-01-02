"""
user_config.py
Version: 2025-12-14_1
Purpose: User-customizable configuration overrides for all system categories
License: Apache 2.0
"""

USER_CUSTOM_CONFIG = {
    
    "cache": {
        "total_cache_allocation_mb": 8.0,
        "lambda_cache_mb": 4.0,
        "response_cache_mb": 3.0,
        "utility_cache_mb": 1.0,
        "default_ttl_seconds": 300,
        "max_entries_per_pool": 200,
        "eviction_policy": "lru",
        "background_cleanup_enabled": True,
        "compression_enabled": True,
        "serialization_method": "json",
        "concurrent_access_enabled": True,
        "enable_pressure_monitoring": True,
        "pressure_check_interval_seconds": 10,
        "warning_threshold_percent": 75,
        "critical_threshold_percent": 85,
        "emergency_cleanup_threshold": 95
    },
    
    "logging": {
        "default_level": "INFO",
        "interface_levels": {
            "cache": "INFO",
            "security": "INFO",
            "metrics": "INFO",
            "circuit_breaker": "INFO",
            "zaph": "INFO"
        },
        "include_timestamps": True,
        "include_caller_info": True,
        "structured_logging": True,
        "console_enabled": True,
        "file_enabled": False,
        "cloudwatch_enabled": True,
        "enable_batching": True,
        "batch_size": 10,
        "flush_interval_seconds": 30
    },
    
    "metrics": {
        "total_metrics_used": 6,
        "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
        "optional_metrics": ["cache_hit_rate", "cost_protection_status"],
        "custom_metrics": [],
        "collection_interval_seconds": 30,
        "batch_submission": True,
        "metric_buffering": True,
        "namespace": "Lambda/Ultra-Optimized",
        "dimension_strategy": "standard",
        "api_call_optimization": True
    },
    
    "security": {
        "total_security_memory_mb": 4.0,
        "validation_memory_mb": 2.0,
        "threat_detection_memory_mb": 2.0,
        "validation_level": "standard",
        "sanitization_enabled": True,
        "pattern_matching_enabled": True,
        "anomaly_detection_enabled": True,
        "rate_limiting_enabled": True,
        "behavioral_analysis_enabled": False,
        "security_events_logged": True,
        "audit_trail_enabled": True,
        "security_metrics_enabled": True
    },
    
    "circuit_breaker": {
        "total_circuit_breaker_memory_mb": 2.0,
        "state_management_memory_mb": 1.2,
        "metrics_memory_mb": 0.8,
        "default_failure_threshold": 3,
        "default_recovery_timeout": 45,
        "failure_detection_window": 300,
        "cloudwatch_api": {
            "failure_threshold": 3,
            "recovery_timeout_seconds": 45,
            "max_test_calls": 2
        },
        "home_assistant": {
            "failure_threshold": 2,
            "recovery_timeout_seconds": 20,
            "max_test_calls": 1
        },
        "external_http": {
            "failure_threshold": 3,
            "recovery_timeout_seconds": 30,
            "max_test_calls": 2
        }
    },
    
    "singleton": {
        "total_singleton_overhead_mb": 4.0,
        "max_singletons": 20,
        "cleanup_threshold_percent": 85,
        "enable_lazy_initialization": True,
        "enable_automatic_disposal": True,
        "disposal_idle_timeout_seconds": 600,
        "enable_reference_counting": True,
        "pressure_response_enabled": True,
        "voluntary_reduction_enabled": True,
        "predictive_memory_management": False
    },
    
    "http_client": {
        "default_timeout_seconds": 30,
        "connect_timeout_seconds": 10,
        "read_timeout_seconds": 30,
        "pool_connections": 10,
        "pool_maxsize": 10,
        "pool_block": False,
        "max_retries": 3,
        "backoff_base_ms": 100,
        "backoff_multiplier": 2.0,
        "max_backoff_seconds": 120,
        "ssl_verify": True,
        "allow_redirects": True,
        "max_redirects": 5,
        "enable_dns_cache": True,
        "dns_cache_ttl_seconds": 300
    },
    
    "lambda_opt": {
        "enable_lazy_loading": True,
        "enable_module_unloading": False,
        "module_unload_threshold_seconds": 300,
        "enable_aggressive_gc": False,
        "gc_threshold_percent": 80,
        "enable_memory_profiling": False,
        "enable_fast_path": True,
        "fast_path_threshold": 10,
        "max_concurrent_executions": 10,
        "reserved_concurrency": 0
    },
    
    "cost_protection": {
        "lambda_invocations_monthly": 1000000,
        "lambda_compute_seconds_monthly": 400000,
        "cloudwatch_metrics_limit": 10,
        "cloudwatch_api_calls_monthly": 1000000,
        "warning_threshold_percent": 75.0,
        "critical_threshold_percent": 90.0,
        "emergency_threshold_percent": 95.0,
        "enable_emergency_mode": True,
        "emergency_mode_duration_seconds": 3600,
        "emergency_reset_threshold_percent": 70.0,
        "enable_real_time_tracking": True,
        "tracking_interval_seconds": 60,
        "enable_projected_usage": True
    },
    
    "utility": {
        "json_max_depth": 20,
        "json_max_size_kb": 100,
        "enable_response_transformation": True,
        "transformation_pipeline": ["validate", "normalize"],
        "enable_correlation_id": True,
        "correlation_id_format": "uuid",
        "enable_detailed_errors": False,
        "error_retry_strategy": "backoff"
    },
    
    "initialization": {
        "enable_warm_start_optimization": True,
        "preload_modules": [],
        "enable_startup_health_check": True,
        "health_check_timeout_seconds": 5,
        "health_check_services": ["cache", "logging"],
        "log_initialization_stages": True,
        "initialization_log_level": "INFO"
    },
    
    "zaph": {
        "enabled": True,
        "cache_size_limit": 100,
        "warm_threshold": 5,
        "hot_threshold": 20,
        "critical_threshold": 100,
        "prewarm_on_cold_start": True,
        "prewarm_common_operations": True,
        "track_heat_metrics": True,
        "protect_hot_modules_from_unload": True,
        "auto_optimize_interval_seconds": 300,
        "stale_operation_timeout_seconds": 300
    }
}

# EOF
