"""variables.py
Version: 2025.10.11.01
Description: Configuration System Core Data Structure with inheritance, override management, and resource constraint validation

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

# pylint: disable=too-many-lines
# Configuration module with extensive tier-based settings - large size is intentional

from typing import Optional
import os
from enum import Enum

# ===== CONFIGURATION TIER DEFINITIONS =====

class ConfigurationTier(Enum):
    """Configuration tier enumeration for four-tier system."""

    MINIMUM = "minimum"
    STANDARD = "standard"
    MAXIMUM = "maximum"
    USER = "user"

class InterfaceType(Enum):
    """Interface type enumeration for configuration organization."""

    CACHE = "cache"
    LOGGING = "logging"
    METRICS = "metrics"
    SECURITY = "security"
    CIRCUIT_BREAKER = "circuit_breaker"
    SINGLETON = "singleton"
    LAMBDA = "lambda"
    HTTP_CLIENT = "http_client"
    UTILITY = "utility"
    INITIALIZATION = "initialization"

# ===== CACHE INTERFACE CONFIGURATION =====

CACHE_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "cache_pools": {
            "total_cache_allocation_mb": 2,
            "lambda_cache_mb": 1,
            "response_cache_mb": 1,
            "utility_cache_mb": 0,
        },
        "cache_policies": {
            "default_ttl_seconds": 60,
            "max_entries_per_pool": 50,
            "eviction_policy": "lru",
            "background_cleanup_enabled": False,
        },
        "performance_settings": {
            "compression_enabled": False,
            "serialization_method": "pickle",
            "concurrent_access_enabled": False,
        },
    },

    ConfigurationTier.STANDARD: {
        "cache_pools": {
            "total_cache_allocation_mb": 8,
            "lambda_cache_mb": 4,
            "response_cache_mb": 3,
            "utility_cache_mb": 1,
        },
        "cache_policies": {
            "default_ttl_seconds": 300,
            "max_entries_per_pool": 200,
            "eviction_policy": "lru",
            "background_cleanup_enabled": True,
        },
        "performance_settings": {
            "compression_enabled": True,
            "serialization_method": "json",
            "concurrent_access_enabled": True,
        },
    },

    ConfigurationTier.MAXIMUM: {
        "cache_pools": {
            "total_cache_allocation_mb": 24,
            "lambda_cache_mb": 12,
            "response_cache_mb": 8,
            "utility_cache_mb": 4,
        },
        "cache_policies": {
            "default_ttl_seconds": 600,
            "max_entries_per_pool": 500,
            "eviction_policy": "advanced_lru",
            "background_cleanup_enabled": True,
        },
        "performance_settings": {
            "compression_enabled": True,
            "serialization_method": "optimized_json",
            "concurrent_access_enabled": True,
        },
    },
}

# ===== LOGGING INTERFACE CONFIGURATION =====

LOGGING_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "log_levels": {
            "default_level": "ERROR",
            "interface_levels": {
                "cache": "ERROR",
                "security": "ERROR",
                "metrics": "ERROR",
            },
        },
        "log_formatting": {
            "include_timestamps": True,
            "include_caller_info": False,
            "structured_logging": False,
        },
        "log_destinations": {
            "console_enabled": True,
            "file_enabled": False,
            "cloudwatch_enabled": False,
        },
    },

    ConfigurationTier.STANDARD: {
        "log_levels": {
            "default_level": "INFO",
            "interface_levels": {
                "cache": "INFO",
                "security": "INFO",
                "metrics": "INFO",
                "circuit_breaker": "INFO",
            },
        },
        "log_formatting": {
            "include_timestamps": True,
            "include_caller_info": True,
            "structured_logging": True,
        },
        "log_destinations": {
            "console_enabled": True,
            "file_enabled": False,
            "cloudwatch_enabled": True,
        },
    },

    ConfigurationTier.MAXIMUM: {
        "log_levels": {
            "default_level": "DEBUG",
            "interface_levels": {
                "cache": "DEBUG",
                "security": "DEBUG",
                "metrics": "DEBUG",
                "circuit_breaker": "DEBUG",
                "singleton": "DEBUG",
            },
        },
        "log_formatting": {
            "include_timestamps": True,
            "include_caller_info": True,
            "structured_logging": True,
        },
        "log_destinations": {
            "console_enabled": True,
            "file_enabled": True,
            "cloudwatch_enabled": True,
        },
    },
}

# ===== METRICS INTERFACE CONFIGURATION =====

METRICS_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "metric_allocation": {
            "total_metrics_used": 4,
            "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
            "optional_metrics": [],
            "custom_metrics": [],
        },
        "collection_settings": {
            "collection_interval_seconds": 60,
            "batch_submission": True,
            "metric_buffering": False,
        },
        "cloudwatch_settings": {
            "namespace": "Lambda/Ultra-Optimized",
            "dimension_strategy": "minimal",
            "api_call_optimization": True,
        },
    },

    ConfigurationTier.STANDARD: {
        "metric_allocation": {
            "total_metrics_used": 6,
            "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
            "optional_metrics": ["cache_hit_rate", "cost_protection_status"],
            "custom_metrics": [],
        },
        "collection_settings": {
            "collection_interval_seconds": 30,
            "batch_submission": True,
            "metric_buffering": True,
        },
        "cloudwatch_settings": {
            "namespace": "Lambda/Ultra-Optimized",
            "dimension_strategy": "standard",
            "api_call_optimization": True,
        },
    },

    ConfigurationTier.MAXIMUM: {
        "metric_allocation": {
            "total_metrics_used": 10,
            "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
            "optional_metrics": ["cache_hit_rate", "cost_protection_status", "security_events", "circuit_breaker_status"],
            "custom_metrics": ["performance_score", "optimization_events"],
        },
        "collection_settings": {
            "collection_interval_seconds": 15,
            "batch_submission": True,
            "metric_buffering": True,
        },
        "cloudwatch_settings": {
            "namespace": "Lambda/Ultra-Optimized",
            "dimension_strategy": "comprehensive",
            "api_call_optimization": True,
        },
    },
}

# ===== SECURITY INTERFACE CONFIGURATION =====

SECURITY_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "resource_allocation": {
            "total_security_memory_mb": 1,
            "validation_memory_mb": 0.5,
            "threat_detection_memory_mb": 0.5,
        },
        "input_validation": {
            "validation_level": "basic",
            "sanitization_enabled": True,
            "pattern_matching_enabled": False,
        },
        "threat_detection": {
            "anomaly_detection_enabled": False,
            "rate_limiting_enabled": True,
            "behavioral_analysis_enabled": False,
        },
        "security_logging": {
            "security_events_logged": False,
            "audit_trail_enabled": False,
            "security_metrics_enabled": False,
        },
    },

    ConfigurationTier.STANDARD: {
        "resource_allocation": {
            "total_security_memory_mb": 4,
            "validation_memory_mb": 2,
            "threat_detection_memory_mb": 2,
        },
        "input_validation": {
            "validation_level": "standard",
            "sanitization_enabled": True,
            "pattern_matching_enabled": True,
        },
        "threat_detection": {
            "anomaly_detection_enabled": True,
            "rate_limiting_enabled": True,
            "behavioral_analysis_enabled": False,
        },
        "security_logging": {
            "security_events_logged": True,
            "audit_trail_enabled": True,
            "security_metrics_enabled": True,
        },
    },

    ConfigurationTier.MAXIMUM: {
        "resource_allocation": {
            "total_security_memory_mb": 12,
            "validation_memory_mb": 6,
            "threat_detection_memory_mb": 6,
        },
        "input_validation": {
            "validation_level": "comprehensive",
            "sanitization_enabled": True,
            "pattern_matching_enabled": True,
        },
        "threat_detection": {
            "anomaly_detection_enabled": True,
            "rate_limiting_enabled": True,
            "behavioral_analysis_enabled": True,
        },
        "security_logging": {
            "security_events_logged": True,
            "audit_trail_enabled": True,
            "security_metrics_enabled": True,
        },
    },
}

# ===== CIRCUIT BREAKER INTERFACE CONFIGURATION =====

CIRCUIT_BREAKER_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "resource_allocation": {
            "total_circuit_breaker_memory_mb": 0.5,
            "state_management_memory_mb": 0.3,
            "metrics_memory_mb": 0.2,
        },
        "service_configurations": {
            "cloudwatch_api": {
                "failure_threshold": 3,
                "recovery_timeout_seconds": 60,
                "max_test_calls": 1,
            },
            "home_assistant": {
                "failure_threshold": 2,
                "recovery_timeout_seconds": 30,
                "max_test_calls": 1,
            },
        },
        "circuit_breaker_policies": {
            "default_failure_threshold": 3,
            "default_recovery_timeout": 60,
            "failure_detection_window": 300,
        },
    },

    ConfigurationTier.STANDARD: {
        "resource_allocation": {
            "total_circuit_breaker_memory_mb": 2,
            "state_management_memory_mb": 1.2,
            "metrics_memory_mb": 0.8,
        },
        "service_configurations": {
            "cloudwatch_api": {
                "failure_threshold": 3,
                "recovery_timeout_seconds": 45,
                "max_test_calls": 2,
            },
            "home_assistant": {
                "failure_threshold": 2,
                "recovery_timeout_seconds": 20,
                "max_test_calls": 1,
            },
            "external_http": {
                "failure_threshold": 3,
                "recovery_timeout_seconds": 30,
                "max_test_calls": 2,
            },
        },
        "circuit_breaker_policies": {
            "default_failure_threshold": 3,
            "default_recovery_timeout": 45,
            "failure_detection_window": 300,
        },
    },

    ConfigurationTier.MAXIMUM: {
        "resource_allocation": {
            "total_circuit_breaker_memory_mb": 6,
            "state_management_memory_mb": 3.6,
            "metrics_memory_mb": 2.4,
        },
        "service_configurations": {
            "cloudwatch_api": {
                "failure_threshold": 3,
                "recovery_timeout_seconds": 45,
                "max_test_calls": 2,
            },
            "home_assistant": {
                "failure_threshold": 2,
                "recovery_timeout_seconds": 20,
                "max_test_calls": 1,
            },
            "external_http": {
                "failure_threshold": 3,
                "recovery_timeout_seconds": 30,
                "max_test_calls": 2,
            },
            "database": {
                "failure_threshold": 2,
                "recovery_timeout_seconds": 60,
                "max_test_calls": 1,
            },
            "custom_services": {
                "failure_threshold": 3,
                "recovery_timeout_seconds": 30,
                "max_test_calls": 2,
            },
        },
        "circuit_breaker_policies": {
            "default_failure_threshold": 3,
            "default_recovery_timeout": 30,
            "failure_detection_window": 180,
        },
    },
}

# ===== SINGLETON INTERFACE CONFIGURATION =====

SINGLETON_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "resource_allocation": {
            "total_singleton_overhead_mb": 2,
        },
        "singleton_types": {
            "cache_manager": {
                "memory_allocation_mb": 0.5,
                "priority": "high",
                "cleanup_strategy": "maintain",
            },
            "security_validator": {
                "memory_allocation_mb": 0.5,
                "priority": "high",
                "cleanup_strategy": "maintain",
            },
            "config_manager": {
                "memory_allocation_mb": 0.5,
                "priority": "critical",
                "cleanup_strategy": "maintain",
            },
        },
        "memory_coordination": {
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": False,
            "predictive_memory_management": False,
        },
    },

    ConfigurationTier.STANDARD: {
        "resource_allocation": {
            "total_singleton_overhead_mb": 4,
        },
        "singleton_types": {
            "cache_manager": {
                "memory_allocation_mb": 1,
                "priority": "high",
                "cleanup_strategy": "reduce",
            },
            "security_validator": {
                "memory_allocation_mb": 1,
                "priority": "high",
                "cleanup_strategy": "reduce",
            },
            "config_manager": {
                "memory_allocation_mb": 0.5,
                "priority": "critical",
                "cleanup_strategy": "maintain",
            },
            "response_processor": {
                "memory_allocation_mb": 0.5,
                "priority": "medium",
                "cleanup_strategy": "reduce",
            },
            "cost_protection": {
                "memory_allocation_mb": 1,
                "priority": "high",
                "cleanup_strategy": "reduce",
            },
        },
        "memory_coordination": {
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": True,
            "predictive_memory_management": False,
        },
    },

    ConfigurationTier.MAXIMUM: {
        "resource_allocation": {
            "total_singleton_overhead_mb": 6,
        },
        "singleton_types": {
            "cache_manager": {
                "memory_allocation_mb": 2,
                "priority": "high",
                "cleanup_strategy": "reduce",
            },
            "security_validator": {
                "memory_allocation_mb": 2,
                "priority": "high",
                "cleanup_strategy": "reduce",
            },
            "config_manager": {
                "memory_allocation_mb": 1,
                "priority": "critical",
                "cleanup_strategy": "maintain",
            },
            "response_processor": {
                "memory_allocation_mb": 1,
                "priority": "medium",
                "cleanup_strategy": "reduce",
            },
            "cost_protection": {
                "memory_allocation_mb": 2,
                "priority": "high",
                "cleanup_strategy": "reduce",
            },
            "lambda_optimizer": {
                "memory_allocation_mb": 1,
                "priority": "medium",
                "cleanup_strategy": "suspend",
            },
            "memory_manager": {
                "memory_allocation_mb": 1,
                "priority": "medium",
                "cleanup_strategy": "reduce",
            },
        },
        "memory_coordination": {
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": True,
            "predictive_memory_management": True,
        },
    },
}

# ===== PLACEHOLDER INTERFACE CONFIGURATIONS (FUTURE PHASES) =====

LAMBDA_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {"tier": "minimum", "status": "placeholder"},
    ConfigurationTier.STANDARD: {"tier": "standard", "status": "placeholder"},
    ConfigurationTier.MAXIMUM: {"tier": "maximum", "status": "placeholder"},
}

HTTP_CLIENT_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {"tier": "minimum", "status": "placeholder"},
    ConfigurationTier.STANDARD: {"tier": "standard", "status": "placeholder"},
    ConfigurationTier.MAXIMUM: {"tier": "maximum", "status": "placeholder"},
}

UTILITY_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {"tier": "minimum", "status": "placeholder"},
    ConfigurationTier.STANDARD: {"tier": "standard", "status": "placeholder"},
    ConfigurationTier.MAXIMUM: {"tier": "maximum", "status": "placeholder"},
}

INITIALIZATION_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {"tier": "minimum", "status": "placeholder"},
    ConfigurationTier.STANDARD: {"tier": "standard", "status": "placeholder"},
    ConfigurationTier.MAXIMUM: {"tier": "maximum", "status": "placeholder"},
}

# ===== CONFIGURATION PRESETS =====

CONFIGURATION_PRESETS = {
    "ultra_conservative": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {},
        "description": "Absolute minimum resource usage - survival mode",
        "memory_estimate": 8,
        "metric_estimate": 4,
    },

    "production_balanced": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {},
        "description": "Balanced production configuration - recommended default",
        "memory_estimate": 32,
        "metric_estimate": 6,
    },

    "performance_optimized": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
            InterfaceType.METRICS: ConfigurationTier.MAXIMUM,
        },
        "description": "High performance with maximum cache and metrics",
        "memory_estimate": 56,
        "metric_estimate": 10,
    },

    "development_debug": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
            InterfaceType.UTILITY: ConfigurationTier.MAXIMUM,
        },
        "description": "Enhanced logging and debugging for development",
        "memory_estimate": 48,
        "metric_estimate": 7,
    },

    "security_focused": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.SECURITY: ConfigurationTier.MAXIMUM,
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum security validation and audit logging",
        "memory_estimate": 64,
        "metric_estimate": 8,
    },

    "resource_constrained": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.STANDARD,
        },
        "description": "Minimal resources with standard caching",
        "memory_estimate": 16,
        "metric_estimate": 5,
    },

    "cache_optimized": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum cache performance with minimal other resources",
        "memory_estimate": 32,
        "metric_estimate": 5,
    },

    "logging_intensive": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum logging detail for debugging with minimal other resources",
        "memory_estimate": 16,
        "metric_estimate": 4,
    },

    "metrics_focused": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.METRICS: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum metrics collection with minimal other resources",
        "memory_estimate": 16,
        "metric_estimate": 10,
    },

    "circuit_breaker_enhanced": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.CIRCUIT_BREAKER: ConfigurationTier.MAXIMUM,
        },
        "description": "Enhanced circuit breaker protection for unreliable services",
        "memory_estimate": 40,
        "metric_estimate": 6,
    },

    "singleton_optimized": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.SINGLETON: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum singleton performance and memory management",
        "memory_estimate": 36,
        "metric_estimate": 6,
    },
}

# ===== CONSTRAINT DEFINITIONS =====

AWS_LAMBDA_CONSTRAINTS = {
    "memory_limit_mb": 128,
    "cloudwatch_metrics_limit": 10,
    "deployment_package_mb": 50,
    "execution_time_limit_seconds": 900,
    "free_tier_invocations_monthly": 1000000,
    "free_tier_compute_time_seconds": 400000,
}

OPTIMIZATION_TARGETS = {
    "memory_conservative_mb": 64,
    "memory_balanced_mb": 96,
    "memory_aggressive_mb": 120,
    "metrics_conservative": 5,
    "metrics_balanced": 7,
    "metrics_aggressive": 10,
}

# ===== PERFORMANCE CONFIGURATION (Environment Variable Overrides) =====
# Performance configuration values extracted from hardcoded constants
# These can be overridden via environment variables for deployment flexibility

# CloudWatch: Maximum metrics per batch (API limit)
CLOUDWATCH_MAX_METRICS_PER_BATCH: int = int(
    os.getenv("LEE_CLOUDWATCH_MAX_METRICS_PER_BATCH", "20")
)

# CloudWatch: Maximum datum size in bytes
CLOUDWATCH_MAX_DATUM_SIZE_BYTES: int = int(
    os.getenv("LEE_CLOUDWATCH_MAX_DATUM_SIZE_BYTES", "2048")
)

# CloudWatch: Maximum metrics per minute (rate limiting)
CLOUDWATCH_MAX_METRICS_PER_MINUTE: int = int(
    os.getenv("LEE_CLOUDWATCH_MAX_METRICS_PER_MINUTE", "1000")
)

# CloudWatch: Maximum buffer size for metric batching
CLOUDWATCH_MAX_BUFFER_SIZE: int = int(
    os.getenv("LEE_CLOUDWATCH_MAX_BUFFER_SIZE", "100")
)

# CloudWatch: Auto-flush threshold (metrics count)
CLOUDWATCH_AUTO_FLUSH_THRESHOLD: int = int(
    os.getenv("LEE_CLOUDWATCH_AUTO_FLUSH_THRESHOLD", "15")
)

# CloudWatch: Maximum flush failures before giving up
CLOUDWATCH_MAX_FLUSH_FAILURES: int = int(
    os.getenv("LEE_CLOUDWATCH_MAX_FLUSH_FAILURES", "3")
)

# Circuit Breaker: Alexa HA API failure threshold
CIRCUIT_BREAKER_ALEXA_HA_API_FAILURE_THRESHOLD: int = int(
    os.getenv("LEE_CIRCUIT_BREAKER_ALEXA_HA_API_FAILURE_THRESHOLD", "5")
)

# Circuit Breaker: Alexa HA API timeout in seconds
CIRCUIT_BREAKER_ALEXA_HA_API_TIMEOUT: float = float(
    os.getenv("LEE_CIRCUIT_BREAKER_ALEXA_HA_API_TIMEOUT", "60.0")
)

# Circuit Breaker: Alexa OAuth failure threshold
CIRCUIT_BREAKER_ALEXA_OAUTH_FAILURE_THRESHOLD: int = int(
    os.getenv("LEE_CIRCUIT_BREAKER_ALEXA_OAUTH_FAILURE_THRESHOLD", "3")
)

# Circuit Breaker: Alexa OAuth timeout in seconds
CIRCUIT_BREAKER_ALEXA_OAUTH_TIMEOUT: float = float(
    os.getenv("LEE_CIRCUIT_BREAKER_ALEXA_OAUTH_TIMEOUT", "120.0")
)

# Cache: Default TTL in seconds
CACHE_DEFAULT_TTL_SECONDS: int = int(
    os.getenv("LEE_CACHE_DEFAULT_TTL_SECONDS", "300")
)

# Cache: Maximum cache size in bytes (100MB default)
CACHE_MAX_BYTES: int = int(
    os.getenv("LEE_CACHE_MAX_BYTES", str(100 * 1024 * 1024))
)

# Cache Warming: Maximum access history records
CACHE_WARMING_MAX_ACCESS_HISTORY: int = int(
    os.getenv("LEE_CACHE_WARMING_MAX_ACCESS_HISTORY", "10000")
)

# Cache Warming: Maximum temporal patterns
CACHE_WARMING_MAX_TEMPORAL_PATTERNS: int = int(
    os.getenv("LEE_CACHE_WARMING_MAX_TEMPORAL_PATTERNS", "100")
)

# Cache Warming: Maximum user patterns
CACHE_WARMING_MAX_USER_PATTERNS: int = int(
    os.getenv("LEE_CACHE_WARMING_MAX_USER_PATTERNS", "1000")
)

# Cache Warming: Maximum top keys to track
CACHE_WARMING_MAX_TOP_KEYS: int = int(
    os.getenv("LEE_CACHE_WARMING_MAX_TOP_KEYS", "100")
)

# HTTP Client: Maximum connection pool size
HTTP_CLIENT_MAX_CONNECTIONS: int = int(
    os.getenv("LEE_HTTP_CLIENT_MAX_CONNECTIONS", "50")
)


# ===== OBSERVABILITY CONFIGURATION (Environment Variable Overrides) =====
# Observability configuration values extracted from hardcoded constants
# These can be overridden via environment variables for deployment flexibility

# Debug: Maximum number of traces to store in memory
DEBUG_MAX_TRACES: int = int(
    os.getenv("LEE_DEBUG_MAX_TRACES", "100")
)

# Debug: Maximum step name length for trace steps
DEBUG_MAX_STEP_NAME_LENGTH: int = int(
    os.getenv("LEE_DEBUG_MAX_STEP_NAME_LENGTH", "200")
)

# Debug: Default count of slowest steps to return
DEBUG_DEFAULT_SLOWEST_STEPS_COUNT: int = int(
    os.getenv("LEE_DEBUG_DEFAULT_SLOWEST_STEPS_COUNT", "5")
)

# Debug: Default count of slowest steps for analysis
DEBUG_DEFAULT_SLOWEST_STEPS_FOR_ANALYSIS: int = int(
    os.getenv("LEE_DEBUG_DEFAULT_SLOWEST_STEPS_FOR_ANALYSIS", "3")
)

# Debug: Default count of top operations to return
DEBUG_DEFAULT_TOP_OPERATIONS_COUNT: int = int(
    os.getenv("LEE_DEBUG_DEFAULT_TOP_OPERATIONS_COUNT", "10")
)

# AST Scanner: Default complexity threshold
AST_SCANNER_DEFAULT_COMPLEXITY_THRESHOLD: int = int(
    os.getenv("LEE_AST_SCANNER_DEFAULT_COMPLEXITY_THRESHOLD", "10")
)

# AST Scanner: Default maximum complexity
AST_SCANNER_DEFAULT_MAX_COMPLEXITY: int = int(
    os.getenv("LEE_AST_SCANNER_DEFAULT_MAX_COMPLEXITY", "15")
)

# AST Scanner: Default duplication threshold
AST_SCANNER_DEFAULT_DUPLICATION_THRESHOLD: int = int(
    os.getenv("LEE_AST_SCANNER_DEFAULT_DUPLICATION_THRESHOLD", "3")
)

# AST Scanner: Default clone type
AST_SCANNER_DEFAULT_CLONE_TYPE: int = int(
    os.getenv("LEE_AST_SCANNER_DEFAULT_CLONE_TYPE", "3")
)

# AST Scanner: Default function length threshold
AST_SCANNER_DEFAULT_FUNCTION_LENGTH_THRESHOLD: int = int(
    os.getenv("LEE_AST_SCANNER_DEFAULT_FUNCTION_LENGTH_THRESHOLD", "50")
)

# AST Scanner: Default cache size limit
AST_SCANNER_DEFAULT_CACHE_SIZE_LIMIT: int = int(
    os.getenv("LEE_AST_SCANNER_DEFAULT_CACHE_SIZE_LIMIT", "1000")
)

# Data: Maximum batch size for batch operations
DATA_MAX_BATCH_SIZE: int = int(
    os.getenv("LEE_DATA_MAX_BATCH_SIZE", "100")
)

# Data: Maximum parallel operations
DATA_MAX_PARALLEL_OPS: int = int(
    os.getenv("LEE_DATA_MAX_PARALLEL_OPS", "20")
)

# Architectural Scanner: Default coupling threshold
ARCH_SCANNER_DEFAULT_COUPLING_THRESHOLD: int = int(
    os.getenv("LEE_ARCH_SCANNER_DEFAULT_COUPLING_THRESHOLD", "10")
)

# Architectural Scanner: Default cohesion threshold
ARCH_SCANNER_DEFAULT_COHESION_THRESHOLD: int = int(
    os.getenv("LEE_ARCH_SCANNER_DEFAULT_COHESION_THRESHOLD", "50")
)

# Architectural Scanner: Maximum file size to scan (bytes)
ARCH_SCANNER_MAX_FILE_SIZE: int = int(
    os.getenv("LEE_ARCH_SCANNER_MAX_FILE_SIZE", str(500 * 1024))
)

# Architectural Scanner: Default pattern threshold
ARCH_SCANNER_DEFAULT_PATTERN_THRESHOLD: int = int(
    os.getenv("LEE_ARCH_SCANNER_DEFAULT_PATTERN_THRESHOLD", "3")
)

# Architectural Scanner: Maximum pattern instances
ARCH_SCANNER_MAX_PATTERN_INSTANCES: int = int(
    os.getenv("LEE_ARCH_SCANNER_MAX_PATTERN_INSTANCES", "100")
)


# ===== SECURITY CONFIGURATION (Environment Variable Overrides) =====
# Security configuration values extracted from hardcoded constants
# These can be overridden via environment variables for deployment flexibility

# Security: Maximum token length for cryptographic operations
SECURITY_MAX_TOKEN_LENGTH: int = int(
    os.getenv("LEE_SECURITY_MAX_TOKEN_LENGTH", "4096")
)

# Security: Maximum log message length to prevent log injection
SECURITY_MAX_LOG_MESSAGE_LENGTH: int = int(
    os.getenv("LEE_SECURITY_MAX_LOG_MESSAGE_LENGTH", "10000")
)

# Security: Maximum log buffer size for bootstrap logging
SECURITY_MAX_LOG_BUFFER_SIZE: int = int(
    os.getenv("LEE_SECURITY_MAX_LOG_BUFFER_SIZE", "100")
)

# Home Assistant: WebSocket connection timeout in seconds
HOME_ASSISTANT_WEBSOCKET_TIMEOUT: int = int(
    os.getenv("LEE_HA_WEBSOCKET_TIMEOUT", "10")
)

# SSRF Protection: Default blocked network ranges (comma-separated CIDR blocks)
# Can be overridden via environment variable: LEE_SSRF_BLOCKED_NETWORKS
_DEFAULT_BLOCKED_NETWORKS_STR = os.getenv(
    "LEE_SSRF_BLOCKED_NETWORKS",
    "127.0.0.0/8,0.0.0.0/32,::1/128,::/128,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,169.254.169.254/32,169.254.0.0/16,fc00::/7,fd00::/8"
)
SECURITY_BLOCKED_NETWORKS: list[str] = [
    net.strip() for net in _DEFAULT_BLOCKED_NETWORKS_STR.split(",")
]


def get_config_value(
    value: int | str | list[str],
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
) -> int | str | list[str]:
    """Validate configuration value with min/max bounds checking.

    Args:
        value: Configuration value to validate
        min_value: Minimum allowed value (for integers only)
        max_value: Maximum allowed value (for integers only)

    Returns:
        Validated configuration value

    Raises:
        ValueError: If value is outside allowed bounds

    Examples:
        >>> # Validate integer with bounds
        >>> timeout = get_config_value(HOME_ASSISTANT_WEBSOCKET_TIMEOUT, 1, 60)
        >>>
        >>> # Validate string (no bounds)
        >>> token_length = get_config_value(SECURITY_MAX_TOKEN_LENGTH, 8, 8192)
    """
    if isinstance(value, int):
        if min_value is not None and value < min_value:
            raise ValueError(f"Value {value} is below minimum {min_value}")
        if max_value is not None and value > max_value:
            raise ValueError(f"Value {value} exceeds maximum {max_value}")
    return value


# ===== EXPORTED DATA STRUCTURES =====

__all__ = [
    # Enums
    "ConfigurationTier", "InterfaceType",

    # Interface configurations
    "CACHE_INTERFACE_CONFIG", "LOGGING_INTERFACE_CONFIG", "METRICS_INTERFACE_CONFIG",
    "SECURITY_INTERFACE_CONFIG", "CIRCUIT_BREAKER_INTERFACE_CONFIG", "SINGLETON_INTERFACE_CONFIG",
    "LAMBDA_INTERFACE_CONFIG", "HTTP_CLIENT_INTERFACE_CONFIG", "UTILITY_INTERFACE_CONFIG",
    "INITIALIZATION_INTERFACE_CONFIG",

    # Presets and constraints
    "CONFIGURATION_PRESETS", "AWS_LAMBDA_CONSTRAINTS", "OPTIMIZATION_TARGETS",

    # Performance configuration
    "CLOUDWATCH_MAX_METRICS_PER_BATCH",
    "CLOUDWATCH_MAX_DATUM_SIZE_BYTES",
    "CLOUDWATCH_MAX_METRICS_PER_MINUTE",
    "CLOUDWATCH_MAX_BUFFER_SIZE",
    "CLOUDWATCH_AUTO_FLUSH_THRESHOLD",
    "CLOUDWATCH_MAX_FLUSH_FAILURES",
    "CIRCUIT_BREAKER_ALEXA_HA_API_FAILURE_THRESHOLD",
    "CIRCUIT_BREAKER_ALEXA_HA_API_TIMEOUT",
    "CIRCUIT_BREAKER_ALEXA_OAUTH_FAILURE_THRESHOLD",
    "CIRCUIT_BREAKER_ALEXA_OAUTH_TIMEOUT",
    "CACHE_DEFAULT_TTL_SECONDS",
    "CACHE_MAX_BYTES",
    "CACHE_WARMING_MAX_ACCESS_HISTORY",
    "CACHE_WARMING_MAX_TEMPORAL_PATTERNS",
    "CACHE_WARMING_MAX_USER_PATTERNS",
    "CACHE_WARMING_MAX_TOP_KEYS",
    "HTTP_CLIENT_MAX_CONNECTIONS",

    # Observability configuration
    "DEBUG_MAX_TRACES",
    "DEBUG_MAX_STEP_NAME_LENGTH",
    "DEBUG_DEFAULT_SLOWEST_STEPS_COUNT",
    "DEBUG_DEFAULT_SLOWEST_STEPS_FOR_ANALYSIS",
    "DEBUG_DEFAULT_TOP_OPERATIONS_COUNT",
    "AST_SCANNER_DEFAULT_COMPLEXITY_THRESHOLD",
    "AST_SCANNER_DEFAULT_MAX_COMPLEXITY",
    "AST_SCANNER_DEFAULT_DUPLICATION_THRESHOLD",
    "AST_SCANNER_DEFAULT_CLONE_TYPE",
    "AST_SCANNER_DEFAULT_FUNCTION_LENGTH_THRESHOLD",
    "AST_SCANNER_DEFAULT_CACHE_SIZE_LIMIT",
    "DATA_MAX_BATCH_SIZE",
    "DATA_MAX_PARALLEL_OPS",
    "ARCH_SCANNER_DEFAULT_COUPLING_THRESHOLD",
    "ARCH_SCANNER_DEFAULT_COHESION_THRESHOLD",
    "ARCH_SCANNER_MAX_FILE_SIZE",
    "ARCH_SCANNER_DEFAULT_PATTERN_THRESHOLD",
    "ARCH_SCANNER_MAX_PATTERN_INSTANCES",

    # Security configuration
    "SECURITY_MAX_TOKEN_LENGTH",
    "SECURITY_MAX_LOG_MESSAGE_LENGTH",
    "SECURITY_MAX_LOG_BUFFER_SIZE",
    "HOME_ASSISTANT_WEBSOCKET_TIMEOUT",
    "SECURITY_BLOCKED_NETWORKS",
    "get_config_value",
]

