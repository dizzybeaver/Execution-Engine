"""
variables.py
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
            "utility_cache_mb": 0
        },
        "cache_policies": {
            "default_ttl_seconds": 60,
            "max_entries_per_pool": 50,
            "eviction_policy": "lru",
            "background_cleanup_enabled": False
        },
        "performance_settings": {
            "compression_enabled": False,
            "serialization_method": "pickle",
            "concurrent_access_enabled": False
        }
    },
    
    ConfigurationTier.STANDARD: {
        "cache_pools": {
            "total_cache_allocation_mb": 8,
            "lambda_cache_mb": 4,
            "response_cache_mb": 3,
            "utility_cache_mb": 1
        },
        "cache_policies": {
            "default_ttl_seconds": 300,
            "max_entries_per_pool": 200,
            "eviction_policy": "lru",
            "background_cleanup_enabled": True
        },
        "performance_settings": {
            "compression_enabled": True,
            "serialization_method": "json",
            "concurrent_access_enabled": True
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        "cache_pools": {
            "total_cache_allocation_mb": 24,
            "lambda_cache_mb": 12,
            "response_cache_mb": 8,
            "utility_cache_mb": 4
        },
        "cache_policies": {
            "default_ttl_seconds": 600,
            "max_entries_per_pool": 500,
            "eviction_policy": "advanced_lru",
            "background_cleanup_enabled": True
        },
        "performance_settings": {
            "compression_enabled": True,
            "serialization_method": "optimized_json",
            "concurrent_access_enabled": True
        }
    }
}

# ===== LOGGING INTERFACE CONFIGURATION =====

LOGGING_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "log_levels": {
            "default_level": "ERROR",
            "interface_levels": {
                "cache": "ERROR",
                "security": "ERROR",
                "metrics": "ERROR"
            }
        },
        "log_formatting": {
            "include_timestamps": True,
            "include_caller_info": False,
            "structured_logging": False
        },
        "log_destinations": {
            "console_enabled": True,
            "file_enabled": False,
            "cloudwatch_enabled": False
        }
    },
    
    ConfigurationTier.STANDARD: {
        "log_levels": {
            "default_level": "INFO",
            "interface_levels": {
                "cache": "INFO",
                "security": "INFO",
                "metrics": "INFO",
                "circuit_breaker": "INFO"
            }
        },
        "log_formatting": {
            "include_timestamps": True,
            "include_caller_info": True,
            "structured_logging": True
        },
        "log_destinations": {
            "console_enabled": True,
            "file_enabled": False,
            "cloudwatch_enabled": True
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        "log_levels": {
            "default_level": "DEBUG",
            "interface_levels": {
                "cache": "DEBUG",
                "security": "DEBUG",
                "metrics": "DEBUG",
                "circuit_breaker": "DEBUG",
                "singleton": "DEBUG"
            }
        },
        "log_formatting": {
            "include_timestamps": True,
            "include_caller_info": True,
            "structured_logging": True
        },
        "log_destinations": {
            "console_enabled": True,
            "file_enabled": True,
            "cloudwatch_enabled": True
        }
    }
}

# ===== METRICS INTERFACE CONFIGURATION =====

METRICS_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "metric_allocation": {
            "total_metrics_used": 4,
            "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
            "optional_metrics": [],
            "custom_metrics": []
        },
        "collection_settings": {
            "collection_interval_seconds": 60,
            "batch_submission": True,
            "metric_buffering": False
        },
        "cloudwatch_settings": {
            "namespace": "Lambda/Ultra-Optimized",
            "dimension_strategy": "minimal",
            "api_call_optimization": True
        }
    },
    
    ConfigurationTier.STANDARD: {
        "metric_allocation": {
            "total_metrics_used": 6,
            "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
            "optional_metrics": ["cache_hit_rate", "cost_protection_status"],
            "custom_metrics": []
        },
        "collection_settings": {
            "collection_interval_seconds": 30,
            "batch_submission": True,
            "metric_buffering": True
        },
        "cloudwatch_settings": {
            "namespace": "Lambda/Ultra-Optimized",
            "dimension_strategy": "standard",
            "api_call_optimization": True
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        "metric_allocation": {
            "total_metrics_used": 10,
            "core_metrics": ["memory_usage", "error_count", "invocation_count", "duration"],
            "optional_metrics": ["cache_hit_rate", "cost_protection_status", "security_events", "circuit_breaker_status"],
            "custom_metrics": ["performance_score", "optimization_events"]
        },
        "collection_settings": {
            "collection_interval_seconds": 15,
            "batch_submission": True,
            "metric_buffering": True
        },
        "cloudwatch_settings": {
            "namespace": "Lambda/Ultra-Optimized",
            "dimension_strategy": "comprehensive",
            "api_call_optimization": True
        }
    }
}

# ===== SECURITY INTERFACE CONFIGURATION =====

SECURITY_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "resource_allocation": {
            "total_security_memory_mb": 1,
            "validation_memory_mb": 0.5,
            "threat_detection_memory_mb": 0.5
        },
        "input_validation": {
            "validation_level": "basic",
            "sanitization_enabled": True,
            "pattern_matching_enabled": False
        },
        "threat_detection": {
            "anomaly_detection_enabled": False,
            "rate_limiting_enabled": True,
            "behavioral_analysis_enabled": False
        },
        "security_logging": {
            "security_events_logged": False,
            "audit_trail_enabled": False,
            "security_metrics_enabled": False
        }
    },
    
    ConfigurationTier.STANDARD: {
        "resource_allocation": {
            "total_security_memory_mb": 4,
            "validation_memory_mb": 2,
            "threat_detection_memory_mb": 2
        },
        "input_validation": {
            "validation_level": "standard",
            "sanitization_enabled": True,
            "pattern_matching_enabled": True
        },
        "threat_detection": {
            "anomaly_detection_enabled": True,
            "rate_limiting_enabled": True,
            "behavioral_analysis_enabled": False
        },
        "security_logging": {
            "security_events_logged": True,
            "audit_trail_enabled": True,
            "security_metrics_enabled": True
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        "resource_allocation": {
            "total_security_memory_mb": 12,
            "validation_memory_mb": 6,
            "threat_detection_memory_mb": 6
        },
        "input_validation": {
            "validation_level": "comprehensive",
            "sanitization_enabled": True,
            "pattern_matching_enabled": True
        },
        "threat_detection": {
            "anomaly_detection_enabled": True,
            "rate_limiting_enabled": True,
            "behavioral_analysis_enabled": True
        },
        "security_logging": {
            "security_events_logged": True,
            "audit_trail_enabled": True,
            "security_metrics_enabled": True
        }
    }
}

# ===== CIRCUIT BREAKER INTERFACE CONFIGURATION =====

CIRCUIT_BREAKER_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "resource_allocation": {
            "total_circuit_breaker_memory_mb": 0.5,
            "state_management_memory_mb": 0.3,
            "metrics_memory_mb": 0.2
        },
        "service_configurations": {
            "cloudwatch_api": {
                "failure_threshold": 3,
                "recovery_timeout_seconds": 60,
                "max_test_calls": 1
            },
            "home_assistant": {
                "failure_threshold": 2,
                "recovery_timeout_seconds": 30,
                "max_test_calls": 1
            }
        },
        "circuit_breaker_policies": {
            "default_failure_threshold": 3,
            "default_recovery_timeout": 60,
            "failure_detection_window": 300
        }
    },
    
    ConfigurationTier.STANDARD: {
        "resource_allocation": {
            "total_circuit_breaker_memory_mb": 2,
            "state_management_memory_mb": 1.2,
            "metrics_memory_mb": 0.8
        },
        "service_configurations": {
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
        "circuit_breaker_policies": {
            "default_failure_threshold": 3,
            "default_recovery_timeout": 45,
            "failure_detection_window": 300
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        "resource_allocation": {
            "total_circuit_breaker_memory_mb": 6,
            "state_management_memory_mb": 3.6,
            "metrics_memory_mb": 2.4
        },
        "service_configurations": {
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
            },
            "database": {
                "failure_threshold": 2,
                "recovery_timeout_seconds": 60,
                "max_test_calls": 1
            },
            "custom_services": {
                "failure_threshold": 3,
                "recovery_timeout_seconds": 30,
                "max_test_calls": 2
            }
        },
        "circuit_breaker_policies": {
            "default_failure_threshold": 3,
            "default_recovery_timeout": 30,
            "failure_detection_window": 180
        }
    }
}

# ===== SINGLETON INTERFACE CONFIGURATION =====

SINGLETON_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {
        "resource_allocation": {
            "total_singleton_overhead_mb": 2
        },
        "singleton_types": {
            "cache_manager": {
                "memory_allocation_mb": 0.5,
                "priority": "high",
                "cleanup_strategy": "maintain"
            },
            "security_validator": {
                "memory_allocation_mb": 0.5,
                "priority": "high",
                "cleanup_strategy": "maintain"
            },
            "config_manager": {
                "memory_allocation_mb": 0.5,
                "priority": "critical",
                "cleanup_strategy": "maintain"
            }
        },
        "memory_coordination": {
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": False,
            "predictive_memory_management": False
        }
    },
    
    ConfigurationTier.STANDARD: {
        "resource_allocation": {
            "total_singleton_overhead_mb": 4
        },
        "singleton_types": {
            "cache_manager": {
                "memory_allocation_mb": 1,
                "priority": "high",
                "cleanup_strategy": "reduce"
            },
            "security_validator": {
                "memory_allocation_mb": 1,
                "priority": "high",
                "cleanup_strategy": "reduce"
            },
            "config_manager": {
                "memory_allocation_mb": 0.5,
                "priority": "critical",
                "cleanup_strategy": "maintain"
            },
            "response_processor": {
                "memory_allocation_mb": 0.5,
                "priority": "medium",
                "cleanup_strategy": "reduce"
            },
            "cost_protection": {
                "memory_allocation_mb": 1,
                "priority": "high",
                "cleanup_strategy": "reduce"
            }
        },
        "memory_coordination": {
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": True,
            "predictive_memory_management": False
        }
    },
    
    ConfigurationTier.MAXIMUM: {
        "resource_allocation": {
            "total_singleton_overhead_mb": 6
        },
        "singleton_types": {
            "cache_manager": {
                "memory_allocation_mb": 2,
                "priority": "high",
                "cleanup_strategy": "reduce"
            },
            "security_validator": {
                "memory_allocation_mb": 2,
                "priority": "high",
                "cleanup_strategy": "reduce"
            },
            "config_manager": {
                "memory_allocation_mb": 1,
                "priority": "critical",
                "cleanup_strategy": "maintain"
            },
            "response_processor": {
                "memory_allocation_mb": 1,
                "priority": "medium",
                "cleanup_strategy": "reduce"
            },
            "cost_protection": {
                "memory_allocation_mb": 2,
                "priority": "high",
                "cleanup_strategy": "reduce"
            },
            "lambda_optimizer": {
                "memory_allocation_mb": 1,
                "priority": "medium",
                "cleanup_strategy": "suspend"
            },
            "memory_manager": {
                "memory_allocation_mb": 1,
                "priority": "medium",
                "cleanup_strategy": "reduce"
            }
        },
        "memory_coordination": {
            "pressure_response_enabled": True,
            "voluntary_reduction_enabled": True,
            "predictive_memory_management": True
        }
    }
}

# ===== PLACEHOLDER INTERFACE CONFIGURATIONS (FUTURE PHASES) =====

LAMBDA_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {"tier": "minimum", "status": "placeholder"},
    ConfigurationTier.STANDARD: {"tier": "standard", "status": "placeholder"},
    ConfigurationTier.MAXIMUM: {"tier": "maximum", "status": "placeholder"}
}

HTTP_CLIENT_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {"tier": "minimum", "status": "placeholder"},
    ConfigurationTier.STANDARD: {"tier": "standard", "status": "placeholder"},
    ConfigurationTier.MAXIMUM: {"tier": "maximum", "status": "placeholder"}
}

UTILITY_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {"tier": "minimum", "status": "placeholder"},
    ConfigurationTier.STANDARD: {"tier": "standard", "status": "placeholder"},
    ConfigurationTier.MAXIMUM: {"tier": "maximum", "status": "placeholder"}
}

INITIALIZATION_INTERFACE_CONFIG = {
    ConfigurationTier.MINIMUM: {"tier": "minimum", "status": "placeholder"},
    ConfigurationTier.STANDARD: {"tier": "standard", "status": "placeholder"},
    ConfigurationTier.MAXIMUM: {"tier": "maximum", "status": "placeholder"}
}

# ===== CONFIGURATION PRESETS =====

CONFIGURATION_PRESETS = {
    "ultra_conservative": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {},
        "description": "Absolute minimum resource usage - survival mode",
        "memory_estimate": 8,
        "metric_estimate": 4
    },
    
    "production_balanced": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {},
        "description": "Balanced production configuration - recommended default",
        "memory_estimate": 32,
        "metric_estimate": 6
    },
    
    "performance_optimized": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
            InterfaceType.METRICS: ConfigurationTier.MAXIMUM,
        },
        "description": "High performance with maximum cache and metrics",
        "memory_estimate": 56,
        "metric_estimate": 10
    },
    
    "development_debug": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
            InterfaceType.UTILITY: ConfigurationTier.MAXIMUM,
        },
        "description": "Enhanced logging and debugging for development", 
        "memory_estimate": 48,
        "metric_estimate": 7
    },
    
    "security_focused": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.SECURITY: ConfigurationTier.MAXIMUM,
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum security validation and audit logging",
        "memory_estimate": 64,
        "metric_estimate": 8
    },
    
    "resource_constrained": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.STANDARD,
        },
        "description": "Minimal resources with standard caching",
        "memory_estimate": 16,
        "metric_estimate": 5
    },
    
    "cache_optimized": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.CACHE: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum cache performance with minimal other resources",
        "memory_estimate": 32,
        "metric_estimate": 5
    },
    
    "logging_intensive": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.LOGGING: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum logging detail for debugging with minimal other resources",
        "memory_estimate": 16,
        "metric_estimate": 4
    },
    
    "metrics_focused": {
        "base_tier": ConfigurationTier.MINIMUM,
        "overrides": {
            InterfaceType.METRICS: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum metrics collection with minimal other resources",
        "memory_estimate": 16,
        "metric_estimate": 10
    },
    
    "circuit_breaker_enhanced": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.CIRCUIT_BREAKER: ConfigurationTier.MAXIMUM,
        },
        "description": "Enhanced circuit breaker protection for unreliable services",
        "memory_estimate": 40,
        "metric_estimate": 6
    },
    
    "singleton_optimized": {
        "base_tier": ConfigurationTier.STANDARD,
        "overrides": {
            InterfaceType.SINGLETON: ConfigurationTier.MAXIMUM,
        },
        "description": "Maximum singleton performance and memory management",
        "memory_estimate": 36,
        "metric_estimate": 6
    }
}

# ===== CONSTRAINT DEFINITIONS =====

AWS_LAMBDA_CONSTRAINTS = {
    "memory_limit_mb": 128,
    "cloudwatch_metrics_limit": 10,
    "deployment_package_mb": 50,
    "execution_time_limit_seconds": 900,
    "free_tier_invocations_monthly": 1000000,
    "free_tier_compute_time_seconds": 400000
}

OPTIMIZATION_TARGETS = {
    "memory_conservative_mb": 64,
    "memory_balanced_mb": 96,
    "memory_aggressive_mb": 120,
    "metrics_conservative": 5,
    "metrics_balanced": 7,
    "metrics_aggressive": 10
}

# ===== EXPORTED DATA STRUCTURES =====

__all__ = [
    # Enums
    'ConfigurationTier', 'InterfaceType',
    
    # Interface configurations
    'CACHE_INTERFACE_CONFIG', 'LOGGING_INTERFACE_CONFIG', 'METRICS_INTERFACE_CONFIG',
    'SECURITY_INTERFACE_CONFIG', 'CIRCUIT_BREAKER_INTERFACE_CONFIG', 'SINGLETON_INTERFACE_CONFIG',
    'LAMBDA_INTERFACE_CONFIG', 'HTTP_CLIENT_INTERFACE_CONFIG', 'UTILITY_INTERFACE_CONFIG',
    'INITIALIZATION_INTERFACE_CONFIG',
    
    # Presets and constraints
    'CONFIGURATION_PRESETS', 'AWS_LAMBDA_CONSTRAINTS', 'OPTIMIZATION_TARGETS'
]

# EOF
